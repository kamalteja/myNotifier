"""Rich text library for slack"""


import json
import typing as t
from dataclasses import asdict, dataclass


@dataclass
class Type:
    type: str


@dataclass
class TextBlock(Type):
    text: object | str


@dataclass
class EmojiText(TextBlock):
    emoji: bool = True


@dataclass(kw_only=True)
class Block(Type):
    block_type: str

    def __post_init__(self):
        self.type = self.block_type

    def dict_factory(self, result):
        _result = {}
        for key, value in result:
            if key == "block_type" or key.startswith("_"):
                continue
            if value is None:
                continue
            _result[key] = value

        return _result

    def to_dict(self):
        return asdict(self, dict_factory=self.dict_factory)

    def get_slack_payload(self):
        return json.dumps({"blocks": [self.to_dict()]})


@dataclass(kw_only=True)
class DividerBlock(Block):
    type: str = "divider"
    block_type: str = "divider"


@dataclass(kw_only=True)
class SectionBlock(TextBlock, Block):
    block_type: str = "section"
    text_class = EmojiText

    def __post_init__(self):
        self.text = self.text_class(type=self.type, text=self.text)
        return super().__post_init__()


@dataclass(kw_only=True)
class PlainText(SectionBlock):
    type: str = "plain_text"


@dataclass(kw_only=True)
class MrkDwnText(SectionBlock):
    type: str = "mrkdwn"
    text_class = TextBlock


@dataclass(kw_only=True)
class HeaderText(SectionBlock):
    block_type: str = "header"


@dataclass(kw_only=True)
class AccessoryBlock(MrkDwnText):
    accessory: object


@dataclass(kw_only=True)
class CheckboxesAccessory:
    type: str = "checkboxes"
    options: t.List[object]


@dataclass(kw_only=True)
class Checkbox:
    text: TextBlock
    description: TextBlock | None = None
    value: str

    _text_type: str = "mrkdwn"

    def __post_init__(self):
        # Change TextBlock with MrkDwnText
        self.text = TextBlock(type=self._text_type, text=self.text)
        self.description = (
            TextBlock(type=self._text_type, text=self.description)
            if self.description
            else None
        )
