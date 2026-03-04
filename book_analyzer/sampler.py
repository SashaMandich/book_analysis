"""
network.sampler
===============
Samples beginning + middle + end of a long text so Claude sees
the full narrative arc without exceeding token limits.
"""


class TextSampler:
    """Samples beginning + middle + end so Claude sees the full narrative arc."""

    def __init__(self, max_chars: int = 80_000):
        self.max_chars = max_chars

    def sample(self, text: str) -> str:
        if len(text) <= self.max_chars:
            return text

        chunk  = self.max_chars // 3
        start  = text[:chunk]
        mid_s  = len(text) // 2 - chunk // 2
        middle = text[mid_s : mid_s + chunk]
        end    = text[-chunk:]

        return (
            start
            + "\n\n[... middle section ...]\n\n"
            + middle
            + "\n\n[... later section ...]\n\n"
            + end
        )
