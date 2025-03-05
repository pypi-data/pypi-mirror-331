import logging
from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Self

logger = logging.getLogger(__name__)


class SectionContent(ABC):
    """Base class for document section contents"""

    @abstractmethod
    def get_markdown(self) -> str: ...


class UnacceptableDocumentFilename(ValueError):
    """Exception class for handling validation of a document filename"""


class DocumentLink:
    def __init__(self, text: str, target: str, link_id: str) -> None:
        self.text = text
        self.target = target
        self.link_id = link_id

    def get_markdown(self) -> str:
        return str(self)

    def get_footnote_markdown(self) -> str:
        return f"[{self.link_id}]: {self.target}"

    def __repr__(self) -> str:
        return f"[{self.text}][{self.link_id}]"

    def __str__(self) -> str:
        return f"[{self.text}][{self.link_id}]"


class DocumentSection:
    def __init__(self, header: str, depth: int = 0) -> None:
        self.depth = depth
        self.header = header
        self.contents: list[SectionContent | DocumentSection] = []

    def set_header(self, header: str) -> None:
        self.header = header

    def add_subsection(self, header: str) -> Self:
        new_section = self.__class__(header, depth=self.depth + 1)
        self.contents.append(new_section)
        return new_section

    def add_content(self, content: SectionContent) -> None:
        self.contents.append(content)

    def get_markdown(self) -> str:
        indenting_hashes = f"{'#'*self.depth}"
        markdown = f"##{indenting_hashes} {self.header}\n\n"
        for i, content in enumerate(self.contents):
            markdown += content.get_markdown()
            # Add some separation between content
            if i != len(self.contents) - 1:
                markdown += "\n\n"
        return markdown


class Document:
    def __init__(self, filename: str) -> None:
        def validate_filename(filename: str) -> Collection[str]:
            issues = []
            if not filename.islower():
                issues.append("Filenames must be lower cased.")
            if " " in filename:
                issues.append("Filenames must not contain spaces (use `-` or `_`).")
            if filename.endswith(".md"):
                issues.append("The .md suffix will be attached automatically.")
            return issues

        filename_issues = validate_filename(filename)
        if len(filename_issues) > 0:
            filename_issues_concat = "\n - ".join(filename_issues)
            raise RuntimeError(
                f"Filename not acceptable for document:\n - {filename_issues_concat}"
            )

        self.filename = filename
        self.header = ""
        # https://academia.stackexchange.com/questions/162433/what-is-the-name-of-the-text-that-might-exist-after-the-chapter-heading-and-befo
        self.lede = ""
        self.sections: list[DocumentSection] = []
        self.links: Mapping[str, DocumentLink] = {}

    def set_header(self, header: str) -> None:
        self.header = header

    def set_lede(self, lede: str) -> None:
        self.lede = lede

    def add_section(self, header: str) -> DocumentSection:
        new_section = DocumentSection(header)
        self.sections.append(new_section)
        return new_section

    def add_link(self, text: str, target: str) -> DocumentLink:
        new_id = str(len(self.links.values()))
        new_link = DocumentLink(text, target, new_id)
        self.links[new_id] = new_link
        return new_link

    def get_markdown(self) -> str:
        # Generate document header
        markdown = f"# {self.header}"
        if self.lede:
            markdown += f"\n\n{self.lede}"
        if len(self.sections) > 0:
            markdown += "\n\n"

        # Generate contents of document
        for i, section in enumerate(self.sections):
            markdown += section.get_markdown()
            # Add some separation between sections
            if i != len(self.sections) - 1:
                markdown += "\n\n"

        # Generate footnotes of link targets if any added to document
        if len(self.links.values()) > 0:
            markdown += "\n\n"
            for i, link in enumerate(self.links.values()):
                markdown += link.get_footnote_markdown()
                # Add newline between links
                if i != len(self.links.values()) - 1:
                    markdown += "\n"

        # End document with an empty line
        markdown += "\n"
        return markdown
