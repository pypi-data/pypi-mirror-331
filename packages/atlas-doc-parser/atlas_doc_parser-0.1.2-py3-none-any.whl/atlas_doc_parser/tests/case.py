# -*- coding: utf-8 -*-

"""
为了方便测试, 我们在 Confluence Cloud 上维护着这样一篇 Confluence Page
https://example.atlassian.net/wiki/spaces/JWBMT/pages/294223873/Atlassian+Document+Format+Parser+Test
里面包含了基本上所有主要文档元素和格式, 以及一些特殊情况, 用于测试解析器的正确性.

我们有一个 `脚本 <https://github.com/MacHu-GWU/atlas_doc_parser-project/tree/dev/scripts/get_examples>`_
可以将这个 Confluence Page 对应的 JSON 数据下载到本地, 以便于测试.

在 `test_model.py <https://github.com/MacHu-GWU/atlas_doc_parser-project/blob/dev/tests/test_model.py>`_
这个单元测试中, 我们需要使用很多 JSON 来进行测试. 有些 JSON 的体积太大了, 不适合直接放在代码中,
所以我们将这些 JSON 放在了这个模块中, 以便于让单元测试的代码更好维护, 并且方便需要的时候一键
点击跳转查看原始 JSON.
"""

import typing as T
import dataclasses

from .helper import check_seder, check_markdown

from ..model import T_DATA, T_NODE
from .. import model


@dataclasses.dataclass
class NodeCase:
    klass: T.Type[T_NODE] = dataclasses.field()
    data: T_DATA = dataclasses.field()
    md: str = dataclasses.field()
    node: T_NODE = dataclasses.field(init=False)

    def __post_init__(self):
        self.node = self.klass.from_dict(self.data)

    def test(self):
        check_seder(self.node)
        check_markdown(self.node, self.md)
        return self


class CaseEnum:
    block_card_with_url_to_markdown = NodeCase(
        klass=model.NodeBlockCard,
        data={
            "type": "blockCard",
            "attrs": {
                "url": "https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/"
            },
        },
        md="[https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)",
    )
    block_quote_basic = NodeCase(
        klass=model.NodeBlockQuote,
        data={
            "type": "blockquote",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"text": "Alice says:", "type": "text"}],
                },
                {
                    "type": "paragraph",
                    "content": [{"text": "Just do it!", "type": "text"}],
                },
            ],
        },
        md="""
        > Alice says:
        > 
        > Just do it!
        """,
    )
    block_quote_with_nested_structure = NodeCase(
        klass=model.NodeBlockQuote,
        data={
            "type": "blockquote",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "text": "This is a one line paragraph. Text may have ",
                            "type": "text",
                        },
                        {"text": "bold", "type": "text", "marks": [{"type": "strong"}]},
                        {"text": ", ", "type": "text"},
                        {"text": "italic", "type": "text", "marks": [{"type": "em"}]},
                        {"text": ", ", "type": "text"},
                        {
                            "text": "underscore",
                            "type": "text",
                            "marks": [{"type": "underline"}],
                        },
                        {"text": ", ", "type": "text"},
                        {
                            "text": "strike through",
                            "type": "text",
                            "marks": [{"type": "strike"}],
                        },
                        {"text": ", ", "type": "text"},
                        {
                            "text": "hyperlink",
                            "type": "text",
                            "marks": [
                                {
                                    "type": "link",
                                    "attrs": {
                                        "href": "https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/"
                                    },
                                }
                            ],
                        },
                        {"text": " and more.", "type": "text"},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [{"text": "This is a bullet list", "type": "text"}],
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"text": "bullet 1 in quote", "type": "text"}
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"text": "bullet 2 in quote", "type": "text"}
                                    ],
                                }
                            ],
                        },
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [{"text": "Code block in quote", "type": "text"}],
                },
                {"type": "paragraph", "content": [{"text": "Start", "type": "text"}]},
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [
                        {"text": "def mul_two(a, b):\n    return a * b", "type": "text"}
                    ],
                },
                {"type": "paragraph", "content": [{"text": "End", "type": "text"}]},
            ],
        },
        md="""
        > This is a one line paragraph. Text may have **bold**, *italic*, underscore, ~~strike through~~, [hyperlink](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) and more.
        > 
        > This is a bullet list
        > 
        > - bullet 1 in quote
        > - bullet 2 in quote
        > 
        > Code block in quote
        > 
        > Start
        > 
        > ```python
        > def mul_two(a, b):
        >     return a * b
        > ```
        > 
        > End
        """,
    )
    bullet_list_with_single_plain_text_item = NodeCase(
        klass=model.NodeBulletList,
        data={
            "type": "bulletList",
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": "Hello world"}],
                        }
                    ],
                }
            ],
        },
        md="- Hello world",
    )
    bullet_list_with_formatted_text_marks = NodeCase(
        klass=model.NodeBulletList,
        data={
            "type": "bulletList",
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Bold",
                                    "marks": [{"type": "strong"}],
                                },
                                {"type": "text", "text": " and "},
                                {
                                    "type": "text",
                                    "text": "italic",
                                    "marks": [{"type": "em"}],
                                },
                                {"type": "text", "text": " and "},
                                {
                                    "type": "text",
                                    "text": "code",
                                    "marks": [{"type": "code"}],
                                },
                            ],
                        }
                    ],
                }
            ],
        },
        md="- **Bold** and *italic* and `code`",
    )
    bullet_list_with_links_and_mixed_formatting = NodeCase(
        klass=model.NodeBulletList,
        data={
            "type": "bulletList",
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Visit ",
                                },
                                {
                                    "type": "text",
                                    "text": "Atlassian",
                                    "marks": [
                                        {
                                            "type": "link",
                                            "attrs": {
                                                "href": "http://atlassian.com",
                                                "title": "Atlassian",
                                            },
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                },
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "This is ",
                                },
                                {
                                    "type": "text",
                                    "text": "strikethrough",
                                    "marks": [{"type": "strike"}],
                                },
                            ],
                        }
                    ],
                },
            ],
        },
        md="""
        - Visit [Atlassian](http://atlassian.com)
        - This is ~~strikethrough~~
        """,
    )
    bullet_list_with_nested_structure = NodeCase(
        klass=model.NodeBulletList,
        data={
            "type": "bulletList",
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": "item 1", "type": "text"}],
                        }
                    ],
                },
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": "item 2", "type": "text"}],
                        },
                        {
                            "type": "bulletList",
                            "content": [
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"text": "item 2.1", "type": "text"}
                                            ],
                                        },
                                        {
                                            "type": "bulletList",
                                            "content": [
                                                {
                                                    "type": "listItem",
                                                    "content": [
                                                        {
                                                            "type": "paragraph",
                                                            "content": [
                                                                {
                                                                    "text": "item 2.1.1",
                                                                    "type": "text",
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                },
                                                {
                                                    "type": "listItem",
                                                    "content": [
                                                        {
                                                            "type": "paragraph",
                                                            "content": [
                                                                {
                                                                    "text": "item 2.1.2",
                                                                    "type": "text",
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"text": "item 2.2", "type": "text"}
                                            ],
                                        },
                                        {
                                            "type": "bulletList",
                                            "content": [
                                                {
                                                    "type": "listItem",
                                                    "content": [
                                                        {
                                                            "type": "paragraph",
                                                            "content": [
                                                                {
                                                                    "text": "item 2.2.1",
                                                                    "type": "text",
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                },
                                                {
                                                    "type": "listItem",
                                                    "content": [
                                                        {
                                                            "type": "paragraph",
                                                            "content": [
                                                                {
                                                                    "text": "item 2.2.2",
                                                                    "type": "text",
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                },
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        md="""
        - item 1
        - item 2
            - item 2.1
                - item 2.1.1
                - item 2.1.2
            - item 2.2
                - item 2.2.1
                - item 2.2.2
        """,
    )
    code_block_none = NodeCase(
        klass=model.NodeCodeBlock,
        data={
            "type": "codeBlock",
            "attrs": {"language": "none"},
            "content": [{"text": "> Hello world", "type": "text"}],
        },
        md="""
        ```
        > Hello world
        ```
        """,
    )
    code_block_python = NodeCase(
        klass=model.NodeCodeBlock,
        data={
            "type": "codeBlock",
            "attrs": {"language": "python"},
            "content": [
                {"text": "def add_two(a, b):\n    return a + b", "type": "text"}
            ],
        },
        md="""
        ```python
        def add_two(a, b):
            return a + b
        ```
        """,
    )
    code_block_without_attributes = NodeCase(
        klass=model.NodeCodeBlock,
        data={
            "type": "codeBlock",
        },
        md="""
        ```
        
        ```
        """,
    )
    date_basic = NodeCase(
        klass=model.NodeDate,
        data={
            "type": "date",
            # Unix timestamp for 2024-01-01 00:00:00 UTC
            "attrs": {"timestamp": "1704067200000"},  # Note: ADF uses milliseconds
        },
        md="2024-01-01",
    )
    inline_card_url_to_markdown_link = NodeCase(
        klass=model.NodeInlineCard,
        data={
            "type": "inlineCard",
            "attrs": {
                "url": "https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/"
            },
        },
        md="[https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)",
    )
    list_item_with_simple_text = NodeCase(
        klass=model.NodeListItem,
        data={
            "type": "listItem",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello world"}],
                }
            ],
        },
        md="Hello world",
    )
    list_item_with_multiple_text_formats = NodeCase(
        klass=model.NodeListItem,
        data={
            "type": "listItem",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Bold",
                            "marks": [{"type": "strong"}],
                        },
                        {"type": "text", "text": " and "},
                        {
                            "type": "text",
                            "text": "italic",
                            "marks": [{"type": "em"}],
                        },
                        {"type": "text", "text": " and "},
                        {
                            "type": "text",
                            "text": "code",
                            "marks": [{"type": "code"}],
                        },
                    ],
                }
            ],
        },
        md="**Bold** and *italic* and `code`",
    )
    ordered_list_with_single_item = NodeCase(
        klass=model.NodeOrderedList,
        data={
            "type": "orderedList",
            "attrs": {"order": 1},
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": "Hello world", "type": "text"}],
                        }
                    ],
                }
            ],
        },
        md="1. Hello world",
    )
    ordered_list_with_formatted_text = NodeCase(
        klass=model.NodeOrderedList,
        data={
            "type": "orderedList",
            "attrs": {"order": 1},
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Bold",
                                    "marks": [{"type": "strong"}],
                                },
                                {"type": "text", "text": " and "},
                                {
                                    "type": "text",
                                    "text": "italic",
                                    "marks": [{"type": "em"}],
                                },
                                {"type": "text", "text": " and "},
                                {
                                    "type": "text",
                                    "text": "code",
                                    "marks": [{"type": "code"}],
                                },
                            ],
                        }
                    ],
                }
            ],
        },
        md="1. **Bold** and *italic* and `code`",
    )
    ordered_list_with_nested_structure = NodeCase(
        klass=model.NodeOrderedList,
        data={
            "type": "orderedList",
            "attrs": {"order": 1},
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": "Alice", "type": "text"}],
                        }
                    ],
                },
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": "Bob", "type": "text"}],
                        }
                    ],
                },
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": "Cathy", "type": "text"}],
                        },
                        {
                            "type": "orderedList",
                            "attrs": {"order": 1},
                            "content": [
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"text": "Cathy 1", "type": "text"}
                                            ],
                                        },
                                        {
                                            "type": "orderedList",
                                            "attrs": {"order": 1},
                                            "content": [
                                                {
                                                    "type": "listItem",
                                                    "content": [
                                                        {
                                                            "type": "paragraph",
                                                            "content": [
                                                                {
                                                                    "text": "Cathy 1.1",
                                                                    "type": "text",
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                },
                                                {
                                                    "type": "listItem",
                                                    "content": [
                                                        {
                                                            "type": "paragraph",
                                                            "content": [
                                                                {
                                                                    "text": "Cathy 1.2",
                                                                    "type": "text",
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"text": "Cathy 2", "type": "text"}
                                            ],
                                        },
                                        {
                                            "type": "orderedList",
                                            "attrs": {"order": 1},
                                            "content": [
                                                {
                                                    "type": "listItem",
                                                    "content": [
                                                        {
                                                            "type": "paragraph",
                                                            "content": [
                                                                {
                                                                    "text": "Cathy 2.1",
                                                                    "type": "text",
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                },
                                                {
                                                    "type": "listItem",
                                                    "content": [
                                                        {
                                                            "type": "paragraph",
                                                            "content": [
                                                                {
                                                                    "text": "Cathy 2.2",
                                                                    "type": "text",
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                },
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        md="""
        1. Alice
        2. Bob
        3. Cathy
            1. Cathy 1
                1. Cathy 1.1
                2. Cathy 1.2
            2. Cathy 2
                1. Cathy 2.1
                2. Cathy 2.2
        """,
    )
    ordered_list_custom_start_number = NodeCase(
        klass=model.NodeOrderedList,
        data={
            "type": "orderedList",
            "attrs": {"order": 5},
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": "Starting at 5", "type": "text"}],
                        }
                    ],
                }
            ],
        },
        md="5. Starting at 5",
    )
    media_external_image_basic_markdown = NodeCase(
        klass=model.NodeMedia,
        data={
            "type": "media",
            "attrs": {
                "width": 580,
                "type": "external",
                "url": "https://www.python.org/static/img/python-logo.png",
                "height": 164,
            },
        },
        md="![](https://www.python.org/static/img/python-logo.png)",
    )
    media_external_image_with_alt_text = NodeCase(
        klass=model.NodeMedia,
        data={
            "type": "media",
            "attrs": {
                "width": 580,
                "alt": "Python Logo",
                "type": "external",
                "url": "https://www.python.org/static/img/python-logo.png",
                "height": 164,
            },
        },
        md="![Python Logo](https://www.python.org/static/img/python-logo.png)",
    )
    media_external_image_with_hyperlink = NodeCase(
        klass=model.NodeMedia,
        data={
            "type": "media",
            "attrs": {
                "width": 580,
                "type": "external",
                "url": "https://www.python.org/static/img/python-logo.png",
                "height": 164,
            },
            "marks": [{"type": "link", "attrs": {"href": "https://www.python.org/"}}],
        },
        md="[![](https://www.python.org/static/img/python-logo.png)](https://www.python.org/)",
    )
    media_external_image_with_alt_and_link = NodeCase(
        klass=model.NodeMedia,
        data={
            "type": "media",
            "attrs": {
                "width": 580,
                "alt": "Python Logo",
                "type": "external",
                "url": "https://www.python.org/static/img/python-logo.png",
                "height": 164,
            },
            "marks": [{"type": "link", "attrs": {"href": "https://www.python.org/"}}],
        },
        md="[![Python Logo](https://www.python.org/static/img/python-logo.png)](https://www.python.org/)",
    )
    media_single_with_one_image = NodeCase(
        klass=model.NodeMediaSingle,
        data={
            "type": "mediaSingle",
            "attrs": {"layout": "center", "width": 250, "widthType": "pixel"},
            "content": [
                {
                    "type": "media",
                    "attrs": {
                        "width": 580,
                        "alt": "Python Logo",
                        "type": "external",
                        "url": "https://www.python.org/static/img/python-logo.png",
                        "height": 164,
                    },
                    "marks": [
                        {"type": "link", "attrs": {"href": "https://www.python.org/"}}
                    ],
                }
            ],
        },
        md="[![Python Logo](https://www.python.org/static/img/python-logo.png)](https://www.python.org/)",
    )
    mention_basic = NodeCase(
        klass=model.NodeMention,
        data={
            "type": "mention",
            "attrs": {
                "id": "70121:5e8e6032-7f3d-4cfa-a4f7-c1bce3f8f06a",
                "localId": "bed788de-f5fb-4cd2-9ee7-cdd775c66dc9",
                "text": "@alice",
            },
        },
        md="@alice",
    )
    panel_basic = NodeCase(
        klass=model.NodePanel,
        data={
            "type": "panel",
            "attrs": {"panelType": "info"},
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello world"}],
                }
            ],
        },
        md="""
        > **INFO**
        > 
        > Hello world
        """,
    )
    panel_with_multiple_content_types = NodeCase(
        klass=model.NodePanel,
        data={
            "type": "panel",
            "attrs": {"panelType": "warning"},
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Warning Title"}],
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "List item 1"}
                                    ],
                                }
                            ],
                        }
                    ],
                },
            ],
        },
        md="""
        > **WARNING**
        > 
        > ## Warning Title
        > 
        > - List item 1
        """,
    )
    paragraph_with_simple_text = NodeCase(
        klass=model.NodeParagraph,
        data={
            "type": "paragraph",
            "content": [{"type": "text", "text": "Hello world"}],
        },
        md="Hello world",
    )
    paragraph_without_content = NodeCase(
        klass=model.NodeParagraph,
        data={
            "type": "paragraph",
        },
        md="",
    )
    paragraph_with_multiple_text_nodes = NodeCase(
        klass=model.NodeParagraph,
        data={
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "text", "text": " "},
                {"type": "text", "text": "world"},
            ],
        },
        md="Hello world",
    )
    paragraph_with_multiple_text_formats = NodeCase(
        klass=model.NodeParagraph,
        data={
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Bold", "marks": [{"type": "strong"}]},
                {"type": "text", "text": " and "},
                {"type": "text", "text": "italic", "marks": [{"type": "em"}]},
            ],
        },
        md="**Bold** and *italic*",
    )

    paragraph_with_local_id = NodeCase(
        klass=model.NodeParagraph,
        data={
            "type": "paragraph",
            "attrs": {"localId": "unique-id-123"},
            "content": [{"type": "text", "text": "Hello world"}],
        },
        md="Hello world",
    )
    paragraph_with_emoji_and_mention = NodeCase(
        klass=model.NodeParagraph,
        data={
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Hello "},
                {"type": "emoji", "attrs": {"shortName": ":smile:", "text": "😊"}},
                {"type": "text", "text": " "},
                {"type": "mention", "attrs": {"id": "123", "text": "@user"}},
            ],
        },
        md="Hello 😊 @user",
    )
    paragraph_with_hyperlink = NodeCase(
        klass=model.NodeParagraph,
        data={
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "Visit us at ",
                },
                {
                    "type": "text",
                    "text": "HERE",
                    "marks": [
                        {
                            "type": "link",
                            "attrs": {
                                "href": "https://example.com",
                            },
                        }
                    ],
                },
            ],
        },
        md="Visit us at [HERE](https://example.com)",
    )
    status_basic = NodeCase(
        klass=model.NodeStatus,
        data={
            "type": "status",
            "attrs": {
                "color": "blue",
                "style": "bold",
                "text": "In Progress",
                "localId": "35d3cbcc-15b9-4e34-9bc2-6fcd0739fb12",
            },
        },
        md="`In Progress`",
    )
    table_with_complex_nested_content = NodeCase(
        klass=model.NodeTable,
        data={
            "type": "table",
            "attrs": {
                "layout": "default",
                "width": 760.0,
                "localId": "662e4ab6-11fd-4afa-8c15-613b7bee54cb",
            },
            "content": [
                {
                    "type": "tableRow",
                    "content": [
                        {
                            "type": "tableHeader",
                            "attrs": {"colspan": 1, "rowspan": 1},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "text": "Col 1",
                                            "type": "text",
                                            "marks": [{"type": "strong"}],
                                        }
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "tableHeader",
                            "attrs": {"colspan": 1, "rowspan": 1},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "text": "Col 2",
                                            "type": "text",
                                            "marks": [{"type": "strong"}],
                                        }
                                    ],
                                }
                            ],
                        },
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {
                            "type": "tableCell",
                            "attrs": {"colspan": 1, "rowspan": 1},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"text": "key 1", "type": "text"}],
                                },
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "text": "special character | is not markdown friendly",
                                            "type": "text",
                                        }
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "tableCell",
                            "attrs": {"colspan": 1, "rowspan": 1},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"text": "value 1", "type": "text"}],
                                },
                                {
                                    "type": "bulletList",
                                    "content": [
                                        {
                                            "type": "listItem",
                                            "content": [
                                                {
                                                    "type": "paragraph",
                                                    "content": [
                                                        {
                                                            "text": "this is ",
                                                            "type": "text",
                                                        },
                                                        {
                                                            "text": "Alice",
                                                            "type": "text",
                                                            "marks": [
                                                                {"type": "strong"}
                                                            ],
                                                        },
                                                        {"text": ", ", "type": "text"},
                                                        {
                                                            "text": "Bob",
                                                            "type": "text",
                                                            "marks": [{"type": "em"}],
                                                        },
                                                        {"text": ", ", "type": "text"},
                                                        {
                                                            "text": "Cathy",
                                                            "type": "text",
                                                            "marks": [
                                                                {"type": "underline"}
                                                            ],
                                                        },
                                                        {"text": ", ", "type": "text"},
                                                        {
                                                            "text": "David",
                                                            "type": "text",
                                                            "marks": [
                                                                {"type": "strike"}
                                                            ],
                                                        },
                                                        {"text": ", ", "type": "text"},
                                                        {
                                                            "text": "Edward",
                                                            "type": "text",
                                                            "marks": [{"type": "code"}],
                                                        },
                                                        {"text": ", ", "type": "text"},
                                                        {
                                                            "text": "Frank",
                                                            "type": "text",
                                                            "marks": [
                                                                {
                                                                    "type": "subsup",
                                                                    "attrs": {
                                                                        "type": "sub"
                                                                    },
                                                                }
                                                            ],
                                                        },
                                                        {"text": ", ", "type": "text"},
                                                        {
                                                            "text": "George",
                                                            "type": "text",
                                                            "marks": [
                                                                {
                                                                    "type": "subsup",
                                                                    "attrs": {
                                                                        "type": "sup"
                                                                    },
                                                                }
                                                            ],
                                                        },
                                                        {"text": ".", "type": "text"},
                                                    ],
                                                }
                                            ],
                                        },
                                        {
                                            "type": "listItem",
                                            "content": [
                                                {
                                                    "type": "paragraph",
                                                    "content": [
                                                        {
                                                            "text": "This line has titled hyperlink ",
                                                            "type": "text",
                                                        },
                                                        {
                                                            "text": "Atlas Doc Format",
                                                            "type": "text",
                                                            "marks": [
                                                                {
                                                                    "type": "link",
                                                                    "attrs": {
                                                                        "href": "https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/"
                                                                    },
                                                                }
                                                            ],
                                                        },
                                                        {"text": ".", "type": "text"},
                                                    ],
                                                }
                                            ],
                                        },
                                        {
                                            "type": "listItem",
                                            "content": [
                                                {
                                                    "type": "paragraph",
                                                    "content": [
                                                        {
                                                            "text": "This line has url hyperlink ",
                                                            "type": "text",
                                                        },
                                                        {
                                                            "type": "inlineCard",
                                                            "attrs": {
                                                                "url": "https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/"
                                                            },
                                                        },
                                                        {
                                                            "text": "    ",
                                                            "type": "text",
                                                        },
                                                    ],
                                                }
                                            ],
                                        },
                                        {
                                            "type": "listItem",
                                            "content": [
                                                {
                                                    "type": "paragraph",
                                                    "content": [
                                                        {
                                                            "text": "This line has inline hyperlink ",
                                                            "type": "text",
                                                        },
                                                        {
                                                            "type": "inlineCard",
                                                            "attrs": {
                                                                "url": "https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/"
                                                            },
                                                        },
                                                    ],
                                                }
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {
                            "type": "tableCell",
                            "attrs": {"colspan": 1, "rowspan": 1},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"text": "key 2", "type": "text"}],
                                },
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "text": "special character | is not markdown friendly",
                                            "type": "text",
                                        }
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "tableCell",
                            "attrs": {"colspan": 1, "rowspan": 1},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"text": "value 2", "type": "text"}],
                                },
                                {
                                    "type": "orderedList",
                                    "attrs": {"order": 1},
                                    "content": [
                                        {
                                            "type": "listItem",
                                            "content": [
                                                {
                                                    "type": "paragraph",
                                                    "content": [
                                                        {
                                                            "text": "Alice",
                                                            "type": "text",
                                                        }
                                                    ],
                                                }
                                            ],
                                        },
                                        {
                                            "type": "listItem",
                                            "content": [
                                                {
                                                    "type": "paragraph",
                                                    "content": [
                                                        {"text": "Bob", "type": "text"}
                                                    ],
                                                }
                                            ],
                                        },
                                        {
                                            "type": "listItem",
                                            "content": [
                                                {
                                                    "type": "paragraph",
                                                    "content": [
                                                        {
                                                            "text": "Cathy",
                                                            "type": "text",
                                                        }
                                                    ],
                                                },
                                                {
                                                    "type": "orderedList",
                                                    "attrs": {"order": 1},
                                                    "content": [
                                                        {
                                                            "type": "listItem",
                                                            "content": [
                                                                {
                                                                    "type": "paragraph",
                                                                    "content": [
                                                                        {
                                                                            "text": "Cathy 1",
                                                                            "type": "text",
                                                                        }
                                                                    ],
                                                                },
                                                                {
                                                                    "type": "orderedList",
                                                                    "attrs": {
                                                                        "order": 1
                                                                    },
                                                                    "content": [
                                                                        {
                                                                            "type": "listItem",
                                                                            "content": [
                                                                                {
                                                                                    "type": "paragraph",
                                                                                    "content": [
                                                                                        {
                                                                                            "text": "Cathy 1.1",
                                                                                            "type": "text",
                                                                                        }
                                                                                    ],
                                                                                }
                                                                            ],
                                                                        },
                                                                        {
                                                                            "type": "listItem",
                                                                            "content": [
                                                                                {
                                                                                    "type": "paragraph",
                                                                                    "content": [
                                                                                        {
                                                                                            "text": "Cathy 1.2",
                                                                                            "type": "text",
                                                                                        }
                                                                                    ],
                                                                                }
                                                                            ],
                                                                        },
                                                                    ],
                                                                },
                                                            ],
                                                        },
                                                        {
                                                            "type": "listItem",
                                                            "content": [
                                                                {
                                                                    "type": "paragraph",
                                                                    "content": [
                                                                        {
                                                                            "text": "Cathy 2",
                                                                            "type": "text",
                                                                        }
                                                                    ],
                                                                },
                                                                {
                                                                    "type": "orderedList",
                                                                    "attrs": {
                                                                        "order": 1
                                                                    },
                                                                    "content": [
                                                                        {
                                                                            "type": "listItem",
                                                                            "content": [
                                                                                {
                                                                                    "type": "paragraph",
                                                                                    "content": [
                                                                                        {
                                                                                            "text": "Cathy 2.1",
                                                                                            "type": "text",
                                                                                        }
                                                                                    ],
                                                                                }
                                                                            ],
                                                                        },
                                                                        {
                                                                            "type": "listItem",
                                                                            "content": [
                                                                                {
                                                                                    "type": "paragraph",
                                                                                    "content": [
                                                                                        {
                                                                                            "text": "Cathy 2.2",
                                                                                            "type": "text",
                                                                                        }
                                                                                    ],
                                                                                }
                                                                            ],
                                                                        },
                                                                    ],
                                                                },
                                                            ],
                                                        },
                                                    ],
                                                },
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {
                            "type": "tableCell",
                            "attrs": {"colspan": 1, "rowspan": 1},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"text": "key 3", "type": "text"}],
                                },
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "text": "special character | is not markdown friendly",
                                            "type": "text",
                                        }
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "tableCell",
                            "attrs": {"colspan": 1, "rowspan": 1},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"text": "value 3", "type": "text"}],
                                },
                                {
                                    "type": "taskList",
                                    "attrs": {"localId": ""},
                                    "content": [
                                        {
                                            "type": "taskItem",
                                            "attrs": {"state": "DONE", "localId": "33"},
                                            "content": [
                                                {"text": "Do this", "type": "text"}
                                            ],
                                        },
                                        {
                                            "type": "taskItem",
                                            "attrs": {"state": "TODO", "localId": "34"},
                                            "content": [
                                                {"text": "And do ", "type": "text"},
                                                {
                                                    "text": "this",
                                                    "type": "text",
                                                    "marks": [{"type": "strong"}],
                                                },
                                            ],
                                        },
                                        {
                                            "type": "taskList",
                                            "attrs": {"localId": ""},
                                            "content": [
                                                {
                                                    "type": "taskItem",
                                                    "attrs": {
                                                        "state": "TODO",
                                                        "localId": "35",
                                                    },
                                                    "content": [
                                                        {
                                                            "text": "sub ",
                                                            "type": "text",
                                                        },
                                                        {
                                                            "text": "task",
                                                            "type": "text",
                                                            "marks": [{"type": "code"}],
                                                        },
                                                        {"text": " 1", "type": "text"},
                                                    ],
                                                },
                                                {
                                                    "type": "taskList",
                                                    "attrs": {"localId": ""},
                                                    "content": [
                                                        {
                                                            "type": "taskItem",
                                                            "attrs": {
                                                                "state": "DONE",
                                                                "localId": "36",
                                                            },
                                                            "content": [
                                                                {
                                                                    "text": "sub ",
                                                                    "type": "text",
                                                                },
                                                                {
                                                                    "text": "task",
                                                                    "type": "text",
                                                                    "marks": [
                                                                        {
                                                                            "type": "underline"
                                                                        }
                                                                    ],
                                                                },
                                                                {
                                                                    "text": " 1.1",
                                                                    "type": "text",
                                                                },
                                                            ],
                                                        },
                                                        {
                                                            "type": "taskItem",
                                                            "attrs": {
                                                                "state": "TODO",
                                                                "localId": "37",
                                                            },
                                                            "content": [
                                                                {
                                                                    "text": "sub ",
                                                                    "type": "text",
                                                                },
                                                                {
                                                                    "text": "task",
                                                                    "type": "text",
                                                                    "marks": [
                                                                        {
                                                                            "type": "strike"
                                                                        }
                                                                    ],
                                                                },
                                                                {
                                                                    "text": " 1.2",
                                                                    "type": "text",
                                                                },
                                                            ],
                                                        },
                                                    ],
                                                },
                                                {
                                                    "type": "taskItem",
                                                    "attrs": {
                                                        "state": "TODO",
                                                        "localId": "38",
                                                    },
                                                    "content": [
                                                        {
                                                            "text": "sub ",
                                                            "type": "text",
                                                        },
                                                        {
                                                            "text": "task",
                                                            "type": "text",
                                                            "marks": [
                                                                {"type": "strong"}
                                                            ],
                                                        },
                                                        {"text": " 2", "type": "text"},
                                                    ],
                                                },
                                                {
                                                    "type": "taskList",
                                                    "attrs": {"localId": ""},
                                                    "content": [
                                                        {
                                                            "type": "taskItem",
                                                            "attrs": {
                                                                "state": "TODO",
                                                                "localId": "39",
                                                            },
                                                            "content": [
                                                                {
                                                                    "text": "sub ",
                                                                    "type": "text",
                                                                },
                                                                {
                                                                    "text": "task",
                                                                    "type": "text",
                                                                    "marks": [
                                                                        {
                                                                            "type": "textColor",
                                                                            "attrs": {
                                                                                "color": "#ff5630"
                                                                            },
                                                                        }
                                                                    ],
                                                                },
                                                                {
                                                                    "text": " 2.1",
                                                                    "type": "text",
                                                                },
                                                            ],
                                                        },
                                                        {
                                                            "type": "taskItem",
                                                            "attrs": {
                                                                "state": "DONE",
                                                                "localId": "40",
                                                            },
                                                            "content": [
                                                                {
                                                                    "text": "sub ",
                                                                    "type": "text",
                                                                },
                                                                {
                                                                    "text": "task",
                                                                    "type": "text",
                                                                    "marks": [
                                                                        {
                                                                            "type": "backgroundColor",
                                                                            "attrs": {
                                                                                "color": "#c6edfb"
                                                                            },
                                                                        }
                                                                    ],
                                                                },
                                                                {
                                                                    "text": " 2.2",
                                                                    "type": "text",
                                                                },
                                                            ],
                                                        },
                                                    ],
                                                },
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        md=r"""
        | **Col 1**<br> | **Col 2**<br> |
        | --- | --- |
        | key 1<br>special character \| is not markdown friendly<br> | value 1<br>- this is **Alice**, *Bob*, Cathy, ~~David~~, `Edward`, Frank, George.<br>- This line has titled hyperlink [Atlas Doc Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/).<br>- This line has url hyperlink [https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)<br>- This line has inline hyperlink [https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) |
        | key 2<br>special character \| is not markdown friendly<br> | value 2<br>1. Alice<br>2. Bob<br>3. Cathy<br>    1. Cathy 1<br>        1. Cathy 1.1<br>        2. Cathy 1.2<br>    2. Cathy 2<br>        1. Cathy 2.1<br>        2. Cathy 2.2 |
        | key 3<br>special character \| is not markdown friendly<br> | value 3<br>- [x] Do this<br>- [ ] And do **this**<br>    - [ ] sub `task` 1<br>        - [x] sub task 1.1<br>        - [ ] sub ~~task~~ 1.2<br>    - [ ] sub **task** 2<br>        - [ ] sub task 2.1<br>        - [x] sub task 2.2 |
        """,
    )
    table_cell_with_escaped_pipe_char = NodeCase(
        klass=model.NodeTableCell,
        data={
            "type": "tableCell",
            "attrs": {"colspan": 1, "rowspan": 1},
            "content": [
                {"type": "paragraph", "content": [{"text": "key 1", "type": "text"}]},
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "text": "special character | is not markdown friendly",
                            "type": "text",
                        }
                    ],
                },
            ],
        },
        md=r"key 1<br>special character \| is not markdown friendly<br>",
    )
    table_cell_with_bullet_list = NodeCase(
        klass=model.NodeTableCell,
        data={
            "type": "tableCell",
            "attrs": {"colspan": 1, "rowspan": 1},
            "content": [
                {"type": "paragraph", "content": [{"text": "value 1", "type": "text"}]},
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"text": "a", "type": "text"}],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"text": "b", "type": "text"}],
                                }
                            ],
                        },
                    ],
                },
            ],
        },
        md="value 1<br>- a<br>- b",
    )
    table_header_with_bold_text = NodeCase(
        klass=model.NodeTableHeader,
        data={
            "type": "tableHeader",
            "attrs": {"colspan": 1, "rowspan": 1},
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"text": "Col 1", "type": "text", "marks": [{"type": "strong"}]}
                    ],
                }
            ],
        },
        md="**Col 1**<br>",
    )
    table_row_with_multiple_cells = NodeCase(
        klass=model.NodeTableRow,
        data={
            "type": "tableRow",
            "content": [
                {
                    "type": "tableCell",
                    "attrs": {"colspan": 1, "rowspan": 1},
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": "key 1", "type": "text"}],
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "text": "special character | is not markdown friendly",
                                    "type": "text",
                                }
                            ],
                        },
                    ],
                },
                {
                    "type": "tableCell",
                    "attrs": {"colspan": 1, "rowspan": 1},
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": "value 1", "type": "text"}],
                        },
                        {
                            "type": "bulletList",
                            "content": [
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [{"text": "a", "type": "text"}],
                                        }
                                    ],
                                },
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [{"text": "b", "type": "text"}],
                                        }
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        md=r"| key 1<br>special character \| is not markdown friendly<br> | value 1<br>- a<br>- b |",
    )
    task_list_with_multiple_states = NodeCase(
        klass=model.NodeTaskList,
        data={
            "type": "taskList",
            "attrs": {"localId": ""},
            "content": [
                {
                    "type": "taskItem",
                    "attrs": {"state": "DONE", "localId": "25"},
                    "content": [{"text": "Do this", "type": "text"}],
                },
                {
                    "type": "taskItem",
                    "attrs": {"state": "TODO", "localId": "26"},
                    "content": [{"text": "And do this", "type": "text"}],
                },
            ],
        },
        md="""
        - [x] Do this
        - [ ] And do this
        """,
    )
    task_list_with_nested_structure = NodeCase(
        klass=model.NodeTaskList,
        data={
            "type": "taskList",
            "attrs": {"localId": ""},
            "content": [
                {
                    "type": "taskItem",
                    "attrs": {"state": "DONE", "localId": "25"},
                    "content": [{"text": "Do this", "type": "text"}],
                },
                {
                    "type": "taskItem",
                    "attrs": {"state": "TODO", "localId": "26"},
                    "content": [{"text": "And do this", "type": "text"}],
                },
                {
                    "type": "taskList",
                    "attrs": {"localId": ""},
                    "content": [
                        {
                            "type": "taskItem",
                            "attrs": {"state": "TODO", "localId": "27"},
                            "content": [
                                {"text": "sub ", "type": "text"},
                                {
                                    "text": "task 1",
                                    "type": "text",
                                    "marks": [{"type": "code"}],
                                },
                            ],
                        },
                        {
                            "type": "taskList",
                            "attrs": {"localId": ""},
                            "content": [
                                {
                                    "type": "taskItem",
                                    "attrs": {"state": "DONE", "localId": "28"},
                                    "content": [
                                        {"text": "sub task 1.1", "type": "text"}
                                    ],
                                },
                                {
                                    "type": "taskItem",
                                    "attrs": {"state": "TODO", "localId": "29"},
                                    "content": [
                                        {"text": "sub task 1.2", "type": "text"}
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "taskItem",
                            "attrs": {"state": "TODO", "localId": "30"},
                            "content": [
                                {"text": "sub ", "type": "text"},
                                {
                                    "text": "task 2",
                                    "type": "text",
                                    "marks": [{"type": "strong"}],
                                },
                            ],
                        },
                        {
                            "type": "taskList",
                            "attrs": {"localId": ""},
                            "content": [
                                {
                                    "type": "taskItem",
                                    "attrs": {"state": "TODO", "localId": "31"},
                                    "content": [
                                        {"text": "sub task 2.1", "type": "text"}
                                    ],
                                },
                                {
                                    "type": "taskItem",
                                    "attrs": {"state": "DONE", "localId": "32"},
                                    "content": [
                                        {"text": "sub task 2.2", "type": "text"}
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        md="""
        - [x] Do this
        - [ ] And do this
            - [ ] sub `task 1`
                - [x] sub task 1.1
                - [ ] sub task 1.2
            - [ ] sub **task 2**
                - [ ] sub task 2.1
                - [x] sub task 2.2
        """,
    )
    text_node_plain_text = NodeCase(
        klass=model.NodeText,
        data={"type": "text", "text": "Hello world"},
        # Plain text should remain unchanged
        md="Hello world",
    )
    text_node_with_strong_emphasis = NodeCase(
        klass=model.NodeText,
        data={"type": "text", "text": "Hello world", "marks": [{"type": "strong"}]},
        md="**Hello world**",
    )
    text_node_with_italic = NodeCase(
        klass=model.NodeText,
        data={"type": "text", "text": "Hello world", "marks": [{"type": "em"}]},
        md="*Hello world*",
    )
    text_node_with_underline = NodeCase(
        klass=model.NodeText,
        data={"type": "text", "text": "Hello world", "marks": [{"type": "underline"}]},
        # HTML underline doesn't have standard markdown equivalent
        md="Hello world",
    )
    text_node_with_strikethrough = NodeCase(
        klass=model.NodeText,
        data={"type": "text", "text": "Hello world", "marks": [{"type": "strike"}]},
        md="~~Hello world~~",
    )
    text_node_with_code_mark = NodeCase(
        klass=model.NodeText,
        data={"type": "text", "text": "Hello world", "marks": [{"type": "code"}]},
        md="`Hello world`",
    )
    text_node_with_subscript = NodeCase(
        klass=model.NodeText,
        data={
            "type": "text",
            "text": "Hello world",
            "marks": [{"type": "subsup", "attrs": {"type": "sub"}}],
        },
        # Subscript doesn't have standard markdown equivalent
        md="Hello world",
    )
    text_node_with_superscript = NodeCase(
        klass=model.NodeText,
        data={
            "type": "text",
            "text": "superscript",
            "marks": [{"type": "subsup", "attrs": {"type": "sup"}}],
        },
        # Superscript doesn't have standard markdown equivalent
        md="superscript",
    )
    text_node_with_text_color = NodeCase(
        klass=model.NodeText,
        data={
            "type": "text",
            "text": "Hello world",
            "marks": [{"type": "textColor", "attrs": {"color": "#97a0af"}}],
        },
        # Text color doesn't have markdown equivalent
        md="Hello world",
    )
    text_node_with_background_color = NodeCase(
        klass=model.NodeText,
        data={
            "type": "text",
            "text": "Hello world",
            "marks": [{"type": "backgroundColor", "attrs": {"color": "#fedec8"}}],
        },
        # Background color doesn't have markdown equivalent
        md="Hello world",
    )
    text_node_with_titled_hyperlink = NodeCase(
        klass=model.NodeText,
        data={
            "text": "Atlassian",
            "type": "text",
            "marks": [
                {
                    "type": "link",
                    "attrs": {"href": "http://atlassian.com", "title": "Atlassian"},
                }
            ],
        },
        md="[Atlassian](http://atlassian.com)",
    )
    text_node_with_url_hyperlink = NodeCase(
        klass=model.NodeText,
        data={
            "text": "Atlassian",
            "type": "text",
            "marks": [{"type": "link", "attrs": {"href": "http://atlassian.com"}}],
        },
        md="[Atlassian](http://atlassian.com)",
    )
