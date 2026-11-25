import re

# Periods need following whitespace to distinguish decimals split across chunks.
BOUNDARY = re.compile(r"[.!?]+(?=\s)|[।॥！？]+")


class SentenceBuffer:
    def __init__(self) -> None:
        self.pending = ""

    def push(self, delta: str) -> list[str]:
        self.pending += delta
        sentences = []
        while match := BOUNDARY.search(self.pending):
            sentence = self.pending[: match.end()].strip()
            self.pending = self.pending[match.end() :].lstrip()
            if sentence:
                sentences.append(sentence)
        return sentences

    def finish(self) -> list[str]:
        remainder, self.pending = self.pending.strip(), ""
        return [remainder] if remainder else []
