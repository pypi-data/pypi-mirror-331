from typing import Protocol


class ContentRecognizable(Protocol):
    def recognize(self, content: bytes) -> str: ...
