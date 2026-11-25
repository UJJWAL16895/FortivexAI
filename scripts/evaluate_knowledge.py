import argparse
import json
from pathlib import Path

from src.rag.index import Knowledge

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--embeddings", action="store_true")
    options = parser.parse_args()
    knowledge = Knowledge.load()
    if options.embeddings:
        knowledge.enable_embeddings()
    rows = json.loads(Path("tests/rag_eval/questions.json").read_text(encoding="utf-8"))
    hits = abstains = abstain_total = 0
    for question, expected in rows:
        answer = knowledge.lookup(question)
        actual = answer.chunk.id if answer and answer.chunk else None
        abstain_total += expected is None
        abstains += expected is None and answer is not None and actual is None
        hits += expected is not None and actual == expected
        print(
            json.dumps(
                {"query": question, "expected": expected, "actual": actual}, ensure_ascii=True
            )
        )
    print(
        f"Source hits {hits}/{len(rows) - abstain_total}; correct abstentions {abstains}/{abstain_total}"
    )
