"""Reviewed answer cards, local multilingual similarity, and conservative abstention."""

import hashlib
import importlib
import json
import re
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from src.llm.claims import HINDI, PRODUCT_QUESTION

ROOT = Path(__file__).resolve().parents[2] / "data" / "knowledge"
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ABSTAIN = "I don't have that information, I'll have a specialist follow up"
SEMANTIC_THRESHOLD = 0.58
SEMANTIC_MARGIN = 0.08
QUESTION = re.compile(
    r"\b(?:shelfpilot|plan|enterprise|student|refund|warranty|weather|integrate)\b", re.I
)
UNSUPPORTED = re.compile(
    r"\b(?:enterprise|student|bulk discount|refund|warranty|weather|amazon|shopify|"
    r"lifetime|nonprofit|weekend discount|black friday|price match)\b|छात्र|रिफंड",
    re.I,
)
PERCENT = re.compile(r"\d+(?:\.\d+)?\s*(?:%|percent\b)", re.I)
DISCOUNT = re.compile(r"\b(?:discounts?|off|percent|chhoot)\b|%|छूट", re.I)
REFUND = re.compile(r"\brefunds?\b|रिफंड|पैसे वापस", re.I)


def abstention(query: str) -> str:
    if REFUND.search(query):
        return (
            "रिफंड के सवाल हमारी सेल्स टीम देखती है। मैं उनसे बात करवाने में मदद कर सकता हूँ।"
            if HINDI.search(query)
            else "Refund questions are handled by our sales team. I can arrange a follow-up with them."
        )
    if DISCOUNT.search(query):
        return (
            "छूट के सवाल हमारी सेल्स टीम देखती है। मैं उनसे बात करवाने में मदद कर सकता हूँ।"
            if HINDI.search(query)
            else "Discounts are handled by our sales team. I can arrange a follow-up with them."
        )
    return ABSTAIN


def words(text: str) -> str:
    return " ".join(
        "".join(
            ch if ch.isalnum() or "\u0900" <= ch <= "\u097f" else " " for ch in text.casefold()
        ).split()
    )


class Chunk(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    title: str
    kind: Literal["product", "pricing", "discount", "faq"]
    aliases: list[str]
    en: str
    hi: str


@dataclass(frozen=True)
class Answer:
    text: str
    chunk: Chunk | None = None
    source: str | None = None


def unit(vector: list[float]) -> list[float]:
    size = sqrt(sum(value * value for value in vector))
    return [value / size for value in vector] if size else vector


class Knowledge:
    def __init__(self, records: list[tuple[Chunk, str]]) -> None:
        self.records = records
        self.embedder: Any = None
        self.vectors: list[list[float]] = []

    @classmethod
    def load(cls, root: Path = ROOT) -> "Knowledge":
        # Trust is established during source review. Uploads cannot alter this allowlist.
        manifest = json.loads((ROOT / "approval.json").read_text(encoding="utf-8"))
        records: list[tuple[Chunk, str]] = []
        for filename, expected in manifest.items():
            path = root / filename
            if not path.is_file():
                continue
            data = path.read_text(encoding="utf-8")
            if hashlib.sha256(data.encode()).hexdigest() != expected:
                continue
            try:
                chunks = [Chunk.model_validate(item) for item in json.loads(data)]
                records.extend((chunk, filename) for chunk in chunks)
            except (ValidationError, ValueError, TypeError):
                continue
        return cls(records)

    def enable_embeddings(self, *, download: bool = False) -> None:
        fastembed = importlib.import_module("fastembed")
        self.embedder = fastembed.TextEmbedding(MODEL, threads=2, local_files_only=not download)
        self.vectors = [
            unit(vector.tolist())
            for vector in self.embedder.embed(
                [" ".join([*chunk.aliases, chunk.en, chunk.hi]) for chunk, _ in self.records]
            )
        ]

    def lookup(self, query: str) -> Answer | None:
        prepared = " " + words(query) + " "
        commercial = bool(PRODUCT_QUESTION.search(query) or DISCOUNT.search(query))
        if UNSUPPORTED.search(query) or REFUND.search(query):
            return Answer(abstention(query))
        prices = re.search(r"\b(?:price|pricing|cost|costs|kitne|rupees?)\b|कीमत|दाम", query, re.I)
        discount = DISCOUNT.search(query)
        candidates = [
            (index, chunk, file)
            for index, (chunk, file) in enumerate(self.records)
            if (not prices or chunk.kind == "pricing")
            and (not discount or chunk.kind == "discount")
        ]
        ranked = sorted(
            (
                (
                    max(
                        (
                            len(words(alias).split())
                            for alias in chunk.aliases
                            if " " + words(alias) + " " in prepared
                        ),
                        default=0,
                    ),
                    chunk,
                    file,
                )
                for _, chunk, file in candidates
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        match = (
            ranked[0][1:]
            if ranked and ranked[0][0] and (len(ranked) == 1 or ranked[0][0] > ranked[1][0])
            else None
        )
        # Explicit price/discount evidence requires a recognized topic label; similarity alone can conflate plans.
        if match is None and self.embedder is not None and candidates and not (prices or discount):
            query_vector = unit(next(self.embedder.embed([query])).tolist())
            scores = sorted(
                (
                    (
                        sum(a * b for a, b in zip(query_vector, self.vectors[index], strict=True)),
                        chunk,
                        file,
                    )
                    for index, chunk, file in candidates
                ),
                key=lambda item: item[0],
                reverse=True,
            )
            best, *rest = scores
            if best[0] >= SEMANTIC_THRESHOLD and (
                not rest or best[0] - rest[0][0] >= SEMANTIC_MARGIN
            ):
                match = best[1:]
        if match:
            chunk, file = match
            if any(
                value.replace(" ", "") not in chunk.en.replace(" ", "")
                for value in PERCENT.findall(query)
            ):
                return Answer(abstention(query))
            return Answer(chunk.hi if HINDI.search(query) else chunk.en, chunk, file)
        return Answer(abstention(query)) if commercial or QUESTION.search(query) else None
