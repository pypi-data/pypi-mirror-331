from unittest.mock import mock_open, patch

from ocroy.reader import read_image


def test_read_image():
    with patch(
        "ocroy.reader.open", mock_open(read_data=b"image_content")
    ) as m:
        actual = read_image("path/to/image.png")

    assert actual == b"image_content"
    m.assert_called_once_with("path/to/image.png", "rb")
