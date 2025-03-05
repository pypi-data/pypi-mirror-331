#!/usr/bin/env python3

import logging
from pathlib import Path

from markdownsausagemachine.contents import Paragraph, UnorderedList
from markdownsausagemachine.sausage_machine import SausageMachine

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.DEBUG)


def generate_example() -> None:
    logger.info("Generating example...")

    my_sausage_machine = SausageMachine()
    index_doc = my_sausage_machine.add_document("linked-sausages")
    index_doc.set_header("Links to Sausages")
    index_doc.set_lede("Sausages can also be linked to.")

    section_one = index_doc.add_section("Sausage Links")
    bratwurst = index_doc.add_link(
        "Bratwurst", "https://en.wikipedia.org/wiki/Bratwurst"
    )
    chorizo = index_doc.add_link("Chorizo", "https://en.wikipedia.org/wiki/Chorizo")
    italian = index_doc.add_link(
        "Italian", "https://en.wikipedia.org/wiki/Italian_sausage"
    )
    section_one.add_content(Paragraph("Here are some links to sausages:"))
    section_one.add_content(
        Paragraph(
            f"The mighty {bratwurst} comes from Germany. The {chorizo} however, "
            f"comes from Spain. And the {italian} comes from, of course, Italy."
        )
    )

    section_two = index_doc.add_section("Sausage Links in Lists")
    andouille = index_doc.add_link(
        "Andouille", "https://en.wikipedia.org/wiki/Andouille"
    )
    merguez = index_doc.add_link("Merguez", "https://en.wikipedia.org/wiki/Merguez")
    section_two.add_content(
        Paragraph(
            "Here are some links to sausages in a list. "
            "Please enjoy each sausage equally."
        )
    )
    section_two.add_content(
        UnorderedList(
            [
                f"{andouille}",
                f"{merguez}",
                f"{bratwurst}",
                f"{italian}",
                f"{chorizo}",
                f"{andouille}",
            ]
        )
    )

    output_dir = Path("./outputs/document_links")
    output_dir.mkdir(parents=True, exist_ok=True)
    my_sausage_machine.output_markdown_documents(output_dir)
    logger.info("Done! Output created in: %s", output_dir)


if __name__ == "__main__":
    generate_example()
