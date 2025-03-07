from dataclasses import dataclass
from pathlib import Path

from ocroy.reader import read_image
from ocroy.recognizers.base import ContentRecognizable


@dataclass(frozen=True)
class OcrRequest:
    file_path: Path


class OcrRecognizer:
    def __init__(self, recognizer: ContentRecognizable) -> None:
        self.recognizer = recognizer

    def __call__(self, request: OcrRequest) -> str:
        content = read_image(request.file_path)
        return self.recognizer.recognize(content)
