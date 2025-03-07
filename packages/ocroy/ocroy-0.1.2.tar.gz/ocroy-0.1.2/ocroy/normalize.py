# ref: https://nikkie-ftnext.hatenablog.com/entry/remove-whitespace-in-text-with-regex  # NOQA: E501
import re


class RemoveWhitespaceNormalizer:
    """
    >>> normalizer = RemoveWhitespaceNormalizer()
    >>> normalizer.normalize("アルゴリズム C")
    'アルゴリズムC'
    >>> normalizer.normalize("アルゴ B リズム C")
    'アルゴBリズムC'
    >>> normalizer.normalize("アイ の 歌声 を 聴か せ て")
    'アイの歌声を聴かせて'
    >>> normalizer.normalize("ういっす ういっす ういっすー✌️")
    'ういっすういっすういっすー✌️'
    >>> normalizer.normalize("検索 エンジン 自作 入門 を 買い ました ！！！")
    '検索エンジン自作入門を買いました！！！'
    >>> normalizer.normalize("Algorithm C")
    'Algorithm C'
    >>> normalizer.normalize("Coding the Matrix")
    'Coding the Matrix'
    """

    basic_latin = "\u0000-\u007f"
    blocks = "".join(
        (
            "\u4e00-\u9fff",  # CJK UNIFIED IDEOGRAPHS
            "\u3040-\u309f",  # HIRAGANA
            "\u30a0-\u30ff",  # KATAKANA
            "\u3000-\u303f",  # CJK SYMBOLS AND PUNCTUATION
            "\uff00-\uffef",  # HALFWIDTH AND FULLWIDTH FORMS
        )
    )

    def __init__(self) -> None:
        pattern1 = re.compile("([{}]) ([{}])".format(self.blocks, self.blocks))
        pattern2 = re.compile(
            "([{}]) ([{}])".format(self.blocks, self.basic_latin)
        )
        pattern3 = re.compile(
            "([{}]) ([{}])".format(self.basic_latin, self.blocks)
        )
        self.patterns = (pattern1, pattern2, pattern3)

    def normalize(self, text: str) -> str:
        for pattern in self.patterns:
            while pattern.search(text):
                text = pattern.sub(r"\1\2", text)
        return text
