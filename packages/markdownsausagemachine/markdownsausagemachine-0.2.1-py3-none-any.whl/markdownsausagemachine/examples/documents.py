#!/usr/bin/env python3

import logging
from pathlib import Path

from markdownsausagemachine.contents import OrderedList, Paragraph, UnorderedList
from markdownsausagemachine.sausage_machine import SausageMachine

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.DEBUG)


def generate_example() -> None:
    logger.info("Generating example...")

    my_sausage_machine = SausageMachine()
    index_doc = my_sausage_machine.add_document("index")
    index_doc.set_header("Index")
    index_doc.set_lede("A small document preamble.")
    new_section = index_doc.add_section("My Sausage Machine")
    new_section.add_content(
        Paragraph("P1: How does a sausage machine become a reality")
    )

    supp_doc = my_sausage_machine.add_document("supplementary-words")
    supp_doc.set_header("Supplementary Words")
    supp_doc.set_lede("Some supplementary words.")
    new_section = supp_doc.add_section("Word List")
    new_section.add_content(
        Paragraph("Tree\n\nFlower\n\nSoil")
    )

    extras_doc = my_sausage_machine.add_document("extra-words")
    extras_doc.set_header("Extra Words")
    extras_doc.set_lede("Some extra words.")
    new_section = extras_doc.add_section("Word List")
    new_section.add_content(
        Paragraph("Water\n\nFire\n\nAir")
    )

    output_dir = Path("./outputs/documents")
    output_dir.mkdir(parents=True, exist_ok=True)
    my_sausage_machine.output_markdown_documents(output_dir)
    logger.info("Done! Output created in: %s", output_dir)


if __name__ == "__main__":
    generate_example()
