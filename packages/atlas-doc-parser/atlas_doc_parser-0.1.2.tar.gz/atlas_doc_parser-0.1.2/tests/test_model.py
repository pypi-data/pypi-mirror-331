# -*- coding: utf-8 -*-

import pytest

from atlas_doc_parser.exc import ParamError
from atlas_doc_parser.model import (
    MarkBackGroundColor,
    MarkCode,
    MarkEm,
    MarkLinkAttrs,
    MarkLink,
    MarkStrike,
    MarkStrong,
    MarkSubSup,
    MarkTextColor,
    MarkUnderLine,
    NodeBlockCard,
    NodeBlockQuote,
    NodeBulletList,
    NodeCodeBlock,
    NodeDate,
    NodeDoc,
    NodeEmoji,
    NodeExpand,
    NodeHardBreak,
    NodeHeading,
    NodeInlineCard,
    NodeListItem,
    NodeMedia,
    NodeMediaGroup,
    NodeMediaSingle,
    NodeMention,
    NodeNestedExpand,
    NodeOrderedList,
    NodePanel,
    NodeParagraph,
    NodeRule,
    NodeStatus,
    NodeTable,
    NodeTableCell,
    NodeTableHeader,
    NodeTableRow,
    NodeTaskItem,
    NodeTaskList,
    NodeText,
    parse_node,
)
from atlas_doc_parser.tests import check_seder
from atlas_doc_parser.tests.case import NodeCase, CaseEnum


class TestMarkBackGroundColor:
    def test_case_1(self):
        pass


class TestMarkCode:
    def test_basic_code_mark(self):
        """Test basic code mark creation and serialization."""
        data = {"type": "code"}
        mark = MarkCode.from_dict(data)
        check_seder(mark)

        # Verify the mark properties
        assert mark.type == "code"
        assert mark.to_dict() == data

        # Test markdown conversion
        assert mark.to_markdown("print('hello')") == "`print('hello')`"

    def test_code_mark_with_special_chars(self):
        """Test code mark with text containing special characters."""
        data = {"type": "code"}
        mark = MarkCode.from_dict(data)

        # Test with backticks in code
        text_with_backticks = "var x = `template string`"
        assert mark.to_markdown(text_with_backticks) == "`var x = `template string``"

        # Test with multiple lines
        multiline_code = "def func():\n    return True"
        assert mark.to_markdown(multiline_code) == "`def func():\n    return True`"

    def test_code_mark_with_empty_string(self):
        """Test code mark with empty string."""
        data = {"type": "code"}
        mark = MarkCode.from_dict(data)
        assert mark.to_markdown("") == "``"

    def test_code_mark_preserves_whitespace_and_newlines(self):
        """Test code mark with various whitespace scenarios."""
        data = {"type": "code"}
        mark = MarkCode.from_dict(data)

        # Test with leading/trailing whitespace
        assert mark.to_markdown("  code  ") == "`  code  `"

        # Test with tabs
        assert mark.to_markdown("\tcode\t") == "`\tcode\t`"

        # Test with newlines
        assert mark.to_markdown("code\nmore code") == "`code\nmore code`"


class TestMarkEm:
    def test_case_1(self):
        pass


class TestMarkLink:
    def test_link_mark_with_title_and_href(self):
        data = {
            "type": "link",
            "attrs": {"href": "http://atlassian.com", "title": "Atlassian"},
        }
        mark = MarkLink.from_dict(data)
        check_seder(mark)

        assert isinstance(mark.attrs, MarkLinkAttrs)
        assert mark.to_dict() == data
        assert mark.to_markdown("Atlassian") == "[Atlassian](http://atlassian.com)"

    def test_link_mark_without_title_uses_text(self):
        data = {"type": "link", "attrs": {"href": "http://example.com"}}
        mark = MarkLink.from_dict(data)
        check_seder(mark)
        # When no title is provided, it should use the text content
        assert mark.to_markdown("Click here") == "[Click here](http://example.com)"

    def test_link_mark_missing_required_attrs_raises(self):
        data = {"type": "link", "attrs": {}}
        with pytest.raises(ParamError):
            MarkLink.from_dict(data)

    def test_link_mark_with_special_chars_in_url(self):
        data = {
            "type": "link",
            "attrs": {
                "href": "http://example.com/path?param=value&other=123",
                "title": "Complex URL",
            },
        }
        mark = MarkLink.from_dict(data)
        check_seder(mark)

        assert (
            mark.to_markdown("Special Link")
            == "[Complex URL](http://example.com/path?param=value&other=123)"
        )


class TestMarkStrike:
    def test_case_1(self):
        pass


class TestMarkStrong:
    def test_basic_strong_mark(self):
        """Test basic strong mark creation and markdown conversion."""
        data = {"type": "strong"}
        mark = MarkStrong.from_dict(data)
        check_seder(mark)
        assert mark.to_markdown("Hello world") == "**Hello world**"

    def test_strong_mark_with_special_chars(self):
        """Test strong mark with text containing special characters."""
        data = {"type": "strong"}
        mark = MarkStrong.from_dict(data)
        check_seder(mark)
        special_text = "Hello * World ** !"
        assert mark.to_markdown(special_text) == f"**{special_text}**"

    def test_strong_mark_with_empty_string(self):
        """Test strong mark with empty text."""
        data = {"type": "strong"}
        mark = MarkStrong.from_dict(data)
        check_seder(mark)
        assert mark.to_markdown("") == "****"

    def test_strong_mark_preserves_whitespace(self):
        """Test strong mark with text containing various whitespace."""
        data = {"type": "strong"}
        mark = MarkStrong.from_dict(data)
        check_seder(mark)
        text_with_spaces = "  Hello  World  "
        assert mark.to_markdown(text_with_spaces) == f"**{text_with_spaces}**"


class TestMarkSubSup:
    def test_case_1(self):
        pass


class TestMarkTextColor:
    def test_case_1(self):
        pass


class TestMarkUnderLine:
    def test_case_1(self):
        pass


class TestNodeBlockCard:
    def test_block_card_with_url_to_markdown(self):
        CaseEnum.block_card_with_url_to_markdown.test()


class TestNodeBlockQuote:
    def test_block_quote_basic(self):
        CaseEnum.block_quote_basic.test()

    def test_block_quote_with_nested_structure(self):
        CaseEnum.block_quote_with_nested_structure.test()


class TestNodeBulletList:
    def test_bullet_list_with_single_plain_text_item(self):
        case = CaseEnum.bullet_list_with_single_plain_text_item.test()

        node = case.node
        node_list_item = node.content[0]
        assert isinstance(node_list_item, NodeListItem)
        node_paragraph = node_list_item.content[0]
        assert isinstance(node_paragraph, NodeParagraph)
        node_text = node_paragraph.content[0]
        assert isinstance(node_text, NodeText)

    def test_bullet_list_with_formatted_text_marks(self):
        CaseEnum.bullet_list_with_formatted_text_marks.test()

    def test_bullet_list_with_links_and_mixed_formatting(self):
        CaseEnum.bullet_list_with_links_and_mixed_formatting.test()

    def test_bullet_list_with_nested_structure(self):
        CaseEnum.bullet_list_with_nested_structure.test()


class TestNodeCodeBlock:
    def test_code_block_none(self):
        CaseEnum.code_block_none.test()

    def test_code_block_python(self):
        CaseEnum.code_block_python.test()

    def test_code_block_without_attributes(self):
        CaseEnum.code_block_without_attributes.test()


class TestNodeDate:
    def test_date_basic(self):
        CaseEnum.date_basic.test()

    def test_missing_timestamp(self):
        # Test error handling for missing timestamp.
        data = {"type": "date", "attrs": {}}
        with pytest.raises(ParamError):
            NodeDate.from_dict(data)

    def test_invalid_timestamp_format(self):
        # Test error handling for invalid timestamp format.
        data = {"type": "date", "attrs": {"timestamp": "not-a-timestamp"}}
        node = NodeDate.from_dict(data)
        with pytest.raises(ValueError):
            node.to_markdown()

    def test_timestamp_conversion(self):
        # Test various timestamp conversions.
        test_cases = [
            # (timestamp in ms, expected date string)
            ("0", "1970-01-01"),  # Unix epoch
            ("1704067200000", "2024-01-01"),  # 2024 New Year
            ("1735689600000", "2025-01-01"),  # 2025 New Year
        ]
        for timestamp, expected in test_cases:
            case = NodeCase(
                klass=NodeDate,
                data={"type": "date", "attrs": {"timestamp": timestamp}},
                md=expected,
            )
            case.test()

    def test_very_large_timestamp(self):
        # Test handling of very large timestamps.
        # Year 2100 timestamp
        data = {"type": "date", "attrs": {"timestamp": "4102444800000"}}
        node = NodeDate.from_dict(data)
        check_seder(node)
        assert node.to_markdown() == "2100-01-01"


# class TestNodeDoc:
#     def test(self):
#         pass
#
#
# class TestNodeEmoji:
#     def test(self):
#         pass
#
#
# class TestNodeExpand:
#     def test(self):
#         pass
#
#
# class TestNodeHardBreak:
#     def test(self):
#         pass
#
#
# class TestNodeHeading:
#     def test(self):
#         pass
#
#
class TestNodeInlineCard:
    def test_inline_card_url_to_markdown_link(self):
        CaseEnum.inline_card_url_to_markdown_link.test()


class TestNodeListItem:
    def test_list_item_with_simple_text(self):
        CaseEnum.list_item_with_simple_text.test()

    def test_list_item_with_multiple_text_formats(self):
        CaseEnum.list_item_with_multiple_text_formats.test()


class TestNodeMedia:
    def test_media_external_image_basic_markdown(self):
        CaseEnum.media_external_image_basic_markdown.test()

    def test_media_external_image_with_alt_text(self):
        CaseEnum.media_external_image_with_alt_text.test()

    def test_media_external_image_with_hyperlink(self):
        CaseEnum.media_external_image_with_hyperlink.test()

    def test_media_external_image_with_alt_and_link(self):
        CaseEnum.media_external_image_with_alt_and_link.test()


class TestNodeMediaGroup:
    def test_case_1(self):
        pass


class TestNodeMediaSingle:
    def test_media_single_with_one_image(self):
        CaseEnum.media_single_with_one_image.test()


class TestNodeMention:
    def test_mention_basic(self):
        CaseEnum.mention_basic.test()


class TestNodeNestedExpand:
    def test(self):
        pass


class TestNodeOrderedList:
    def test_ordered_list_with_single_item(self):
        CaseEnum.ordered_list_with_single_item.test()

    def test_ordered_list_with_formatted_text(self):
        CaseEnum.ordered_list_with_formatted_text.test()

    def test_ordered_list_with_nested_structure(self):
        CaseEnum.ordered_list_with_nested_structure.test()

    def test_ordered_list_custom_start_number(self):
        CaseEnum.ordered_list_custom_start_number.test()


class TestNodePanel:
    def test_panel_basic(self):
        CaseEnum.panel_basic.test()

    def test_panel_with_multiple_content_types(self):
        CaseEnum.panel_with_multiple_content_types.test()


class TestNodeParagraph:
    def test_paragraph_with_simple_text(self):
        CaseEnum.paragraph_with_simple_text.test()

    def test_paragraph_without_content(self):
        CaseEnum.paragraph_without_content.test()

    def test_paragraph_with_multiple_text_nodes(self):
        CaseEnum.paragraph_with_multiple_text_nodes.test()

    def test_paragraph_with_multiple_text_formats(self):
        CaseEnum.paragraph_with_multiple_text_formats.test()

    def test_paragraph_with_local_id(self):
        case = CaseEnum.paragraph_with_local_id.test()
        assert case.node.attrs.localId == "unique-id-123"

    def test_paragraph_with_emoji_and_mention(self):
        CaseEnum.paragraph_with_emoji_and_mention.test()

    def test_paragraph_with_hyperlink(self):
        CaseEnum.paragraph_with_hyperlink.test()


class TestNodeRule:
    def test_rule_basic(self):
        case = NodeCase(
            klass=NodeRule,
            data={"type": "rule"},
            md="---",
        )
        case.test()


class TestNodeStatus:
    def test_status_basic(self):
        CaseEnum.status_basic.test()


class TestNodeTable:
    def test_table_with_complex_nested_content(self):
        CaseEnum.table_with_complex_nested_content.test()


class TestNodeTableCell:
    def test_table_cell_with_escaped_pipe_char(self):
        CaseEnum.table_cell_with_escaped_pipe_char.test()

    def test_table_cell_with_bullet_list(self):
        CaseEnum.table_cell_with_bullet_list.test()


class TestNodeTableHeader:
    def test_table_header_with_bold_text(self):
        CaseEnum.table_header_with_bold_text.test()


class TestNodeTableRow:
    def test_table_row_with_multiple_cells(self):
        CaseEnum.table_row_with_multiple_cells.test()


class TestNodeTaskItem:
    def test_task_item_done_and_todo_states(self):
        case = NodeCase(
            klass=NodeTaskItem,
            data={
                "type": "taskItem",
                "attrs": {"state": "DONE", "localId": "25"},
                "content": [{"text": "Do this", "type": "text"}],
            },
            md="[x] Do this",
        )
        case.test()

        case = NodeCase(
            klass=NodeTaskItem,
            data={
                "type": "taskItem",
                "attrs": {"state": "TODO", "localId": "26"},
                "content": [{"text": "And do this", "type": "text"}],
            },
            md="[ ] And do this",
        )
        case.test()


class TestNodeTaskList:
    def test_task_list_with_multiple_states(self):
        CaseEnum.task_list_with_multiple_states.test()

    def test_task_list_with_nested_structure(self):
        CaseEnum.task_list_with_nested_structure.test()


class TestNodeText:
    def test_text_node_plain_text(self):
        CaseEnum.text_node_plain_text.test()

    def test_text_node_missing_text_raises(self):
        data = {"type": "text"}
        with pytest.raises(ParamError):
            NodeText.from_dict(data)

    def test_text_node_with_strong_emphasis(self):
        CaseEnum.text_node_with_strong_emphasis.test()

    def test_text_node_with_italic(self):
        CaseEnum.text_node_with_italic.test()

    def test_text_node_with_underline(self):
        CaseEnum.text_node_with_underline.test()

    def test_text_node_with_strikethrough(self):
        CaseEnum.text_node_with_strikethrough.test()

    def test_text_node_with_code_mark(self):
        CaseEnum.text_node_with_code_mark.test()

    def test_text_node_with_subscript(self):
        CaseEnum.text_node_with_subscript.test()
        CaseEnum.text_node_with_superscript.test()

    def test_text_node_with_text_color(self):
        CaseEnum.text_node_with_text_color.test()

    def test_text_node_with_background_color(self):
        CaseEnum.text_node_with_background_color.test()

    def test_text_node_with_titled_hyperlink(self):
        CaseEnum.text_node_with_titled_hyperlink.test()

    def test_text_node_with_url_hyperlink(self):
        CaseEnum.text_node_with_url_hyperlink.test()


if __name__ == "__main__":
    from atlas_doc_parser.tests import run_cov_test

    run_cov_test(__file__, "atlas_doc_parser.model", preview=False)
