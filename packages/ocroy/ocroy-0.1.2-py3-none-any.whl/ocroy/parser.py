import argparse
from pathlib import Path

from ocroy.recognizers.google_vision_api import (
    recognize_command as google_vision_api_recognize,
)
from ocroy.recognizers.tesseract import (
    recognize_command as tesseract_recognize,
)


def parse_args():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("image_path", type=Path)

    parser = argparse.ArgumentParser()
    method_parsers = parser.add_subparsers(title="method")

    tesseract_parser = method_parsers.add_parser(
        "tesseract", parents=[common_parser]
    )
    tesseract_parser.set_defaults(func=tesseract_recognize)

    google_api_parser = method_parsers.add_parser(
        "google_api", parents=[common_parser]
    )
    google_api_parser.add_argument("--handle-document", action="store_true")
    google_api_parser.set_defaults(func=google_vision_api_recognize)

    return parser.parse_args()
