from abc import abstractmethod
from collections.abc import Collection

from markdownsausagemachine.contents_codeblock import CodeBlock
from markdownsausagemachine.contents_paragraph import Paragraph
from markdownsausagemachine.document import SectionContent

type ListItem = str | Paragraph | CodeBlock | MarkdownList


class MarkdownList(SectionContent):
    """Shared abstraction for list classes"""

    def __init__(self, items: Collection[ListItem]) -> None:
        self.items = items
        self.nesting_level = 0

    @abstractmethod
    def get_initial_indent(self, item_no: int) -> str: ...

    def get_markdown(self) -> str:
        markdown = ""

        # Cannot use enumeration here because not nested lists should not be
        # counted.
        item_no = 0
        for i, item in enumerate(self.items):
            # Pre-calculate the indentation of the item
            initial_indent = self.get_initial_indent(item_no)
            subsequent_indent = f"{' '*len(initial_indent)}"

            # Update list items attributes to inform them they are indented in a
            # list before capturing their equivalent markdown
            if isinstance(item, MarkdownList):
                item.nesting_level = self.nesting_level + 1
            else:
                item_no = item_no + 1
                if isinstance(item, str):
                    # Sneaky hack: replace the string item with a Paragraph to
                    # reuse its Paragraph indentation logic and provide still
                    # the simplified interface of basic strings to users.
                    item = Paragraph(item)
                    item.initial_indent = initial_indent
                    item.subsequent_indent = subsequent_indent
                elif isinstance(item, Paragraph):
                    item.initial_indent = initial_indent
                    item.subsequent_indent = subsequent_indent
                elif isinstance(item, CodeBlock):
                    item.initial_indent = initial_indent
                    item.subsequent_indent = subsequent_indent
                else:
                    raise ValueError(f"Unsupported list item: {type(item)}")

            # Get the items markdown
            markdown += item.get_markdown()

            # Add some separation between items
            if i != len(self.items) - 1:
                markdown += "\n"
        return markdown


class UnorderedList(MarkdownList):
    def get_initial_indent(self, item_no: int) -> str:
        return f"{' '*(self.nesting_level*4)}*   "


class OrderedList(MarkdownList):
    def get_initial_indent(self, item_no: int) -> str:
        return f"{' '*(self.nesting_level*4)}{item_no+1}.  "
