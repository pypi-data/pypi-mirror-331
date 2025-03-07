import argparse
from io import BytesIO
from pathlib import Path

from ocroy.normalize import RemoveWhitespaceNormalizer
from ocroy.recognizers.core import OcrRecognizer, OcrRequest


class ImageRecognizer:
    def recognize(self, content: bytes) -> str:
        import pytesseract
        from PIL import Image

        image = Image.open(BytesIO(content))
        result = pytesseract.image_to_string(image, lang="jpn")

        normalizer = RemoveWhitespaceNormalizer()
        return normalizer.normalize(result)


def recognize(request: OcrRequest) -> str:
    tesseract_recognizer = ImageRecognizer()
    recognizer = OcrRecognizer(tesseract_recognizer)
    return recognizer(request)


def recognize_command(args: argparse.Namespace) -> str:
    return recognize(OcrRequest(args.image_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", type=Path)
    args = parser.parse_args()

    print(recognize_command(args))
