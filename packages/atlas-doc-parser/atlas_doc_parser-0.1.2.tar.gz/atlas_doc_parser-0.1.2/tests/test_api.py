# -*- coding: utf-8 -*-

from atlas_doc_parser import api


def test():
    _ = api
    _ = api.ParamError
    _ = api.TypeEnum
    _ = api.BaseMark
    _ = api.T_MARK
    _ = api.MarkBackGroundColorAttrs
    _ = api.MarkBackGroundColor
    _ = api.MarkCode
    _ = api.MarkEm
    _ = api.MarkLinkAttrs
    _ = api.MarkLink
    _ = api.MarkStrike
    _ = api.MarkStrong
    _ = api.MarkSubSupAttrs
    _ = api.MarkSubSup
    _ = api.MarkTextColorAttrs
    _ = api.MarkTextColor
    _ = api.MarkUnderLine
    _ = api.parse_mark
    _ = api.BaseNode
    _ = api.T_NODE
    _ = api.NodeBlockCardAttrs
    _ = api.NodeBlockCard
    _ = api.NodeBlockQuote
    _ = api.NodeBulletList
    _ = api.NodeCodeBlockAttrs
    _ = api.NodeCodeBlock
    _ = api.NodeDateAttrs
    _ = api.NodeDate
    _ = api.NodeDoc
    _ = api.NodeEmojiAttrs
    _ = api.NodeEmoji
    _ = api.NodeExpandAttrs
    _ = api.NodeExpand
    _ = api.NodeHardBreak
    _ = api.NodeHeadingAttrs
    _ = api.NodeHeading
    _ = api.NodeInlineCardAttrs
    _ = api.NodeInlineCard
    _ = api.NodeListItem
    _ = api.T_NODE_MEDIA_ATTRS_TYPE
    _ = api.NodeMediaAttrs
    _ = api.NodeMedia
    _ = api.NodeMediaGroup
    _ = api.T_NODE_MEDIA_SINGLE_ATTRS_LAYOUT
    _ = api.NodeMediaSingleAttrs
    _ = api.NodeMediaSingle
    _ = api.T_NODE_MENTION_ATTRS_USER_TYPE
    _ = api.T_NODE_MENTION_ATTRS_ACCESS_LEVEL
    _ = api.NodeMentionAttrs
    _ = api.NodeMention
    _ = api.NodeNestedExpandAttrs
    _ = api.NodeNestedExpand
    _ = api.NodeOrderedListAttrs
    _ = api.NodeOrderedList
    _ = api.T_NODE_PANEL_ATTRS_PANEL_TYPE
    _ = api.NodePanelAttrs
    _ = api.NodePanel
    _ = api.NodeParagraphAttrs
    _ = api.NodeParagraph
    _ = api.NodeRule
    _ = api.T_NODE_STATUS_ATTRS_COLOR
    _ = api.NodeStatusAttrs
    _ = api.NodeStatus
    _ = api.NodeTableAttrs
    _ = api.NodeTable
    _ = api.NodeTableCellAttrs
    _ = api.NodeTableCell
    _ = api.NodeTableHeaderAttrs
    _ = api.NodeTableHeader
    _ = api.NodeTableRow
    _ = api.NodeHeadingAttrs
    _ = api.NodeTaskItemAttrs
    _ = api.NodeTaskItem
    _ = api.NodeTaskListAttrs
    _ = api.NodeTaskList
    _ = api.NodeText
    _ = api.parse_node


if __name__ == "__main__":
    from atlas_doc_parser.tests import run_cov_test

    run_cov_test(__file__, "atlas_doc_parser.api", preview=False)
