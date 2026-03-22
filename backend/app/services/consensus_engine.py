class ConsensusResult:
    def __init__(self, final_text: str):
        self.final_text = final_text


class ConsensusEngine:
    def resolve(self, results):
        texts = [r.text for r in results if r.success and r.text]

        if not texts:
            return ConsensusResult(final_text="")

        # simple strategy: pick longest text
        final_text = max(texts, key=len)

        return ConsensusResult(final_text=final_text)