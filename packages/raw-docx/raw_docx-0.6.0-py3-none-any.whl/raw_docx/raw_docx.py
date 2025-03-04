import os
import re
import docx
import zipfile
from pathlib import Path
from .raw_document import RawDocument
from .raw_section import RawSection
from .raw_paragraph import RawParagraph
from .raw_image import RawImage
from .raw_table import RawTable
from .raw_table_row import RawTableRow
from .raw_table_cell import RawTableCell
from .raw_list import RawList
from .raw_list_item import RawListItem
from docx import Document as DocXProcessor
from docx.document import Document
from docx.oxml.table import CT_Tbl, CT_TcPr
from docx.oxml.text.paragraph import CT_P
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from lxml import etree
from .raw_logger import logger
from .docx_paragraph import extract_runs  # Needed such that method inserted into class


class RawDocx:
    class LogicError(Exception):
        pass

    def __init__(self, full_path: str):
        path = Path(full_path)
        # path.stem, path.suffix[1:]
        self.full_path = full_path
        self.dir = path.parent
        self.filename = path.name
        self.image_path = os.path.join(self.dir, "images")
        self.image_rels = {}
        self._organise_dir()
        self.source_document = DocXProcessor(self.full_path)
        self.target_document = RawDocument()
        self._process()

    def _organise_dir(self):
        try:
            os.mkdir(self.image_path)
        except FileExistsError:
            pass
        except Exception as e:
            logger.exception("Failed to create image directory", e)

    def _process(self):
        try:
            self._extract_images()
            for block_item in self._iter_block_items(self.source_document):
                target_section = self.target_document.current_section()
                if isinstance(block_item, Paragraph):
                    # print(f"PARA BLOCK: {block_item.text}")
                    self._process_paragraph(block_item, target_section, self.image_rels)
                elif isinstance(block_item, Table):
                    self._process_table(block_item, target_section)
                else:
                    logger.warning("Ignoring element")
                    raise ValueError
        except Exception as e:
            logger.exception("Exception raised processing document", e)

    def _extract_images(self):
        # Extract images to image dir
        self._extract_images()
        # Save all 'rId:filenames' as references
        for r in self.source_document.part.rels.values():
            if isinstance(r._target, docx.parts.image.ImagePart):
                self.image_rels[r.rId] = os.path.join(
                    self.image_path, os.path.basename(r._target.partname)
                )

    def _iter_block_items(self, parent):
        """
        Yield each paragraph and table child within *parent*, in document
        order. Each returned value is an instance of either Table or
        Paragraph. *parent* would most commonly be a reference to a main
        Document object, but also works for a _Cell object, which itself can
        contain paragraphs and tables.
        """
        if isinstance(parent, Document):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            raise ValueError("something's not right with the parent")

        for child in parent_elm.iterchildren():
            if isinstance(child, str):
                logger.warning(f"Ignoring eTree element {child}")
            elif isinstance(child, CT_P):
                # print(f"PARA: {child.text}")
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)
            elif isinstance(child, etree._Element):
                if (
                    child.tag
                    == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcPr"
                ):
                    pass
                elif (
                    child.tag
                    == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdt"
                ):
                    pass
                else:
                    logger.warning(f"Ignoring eTree element {self._tree(child)}")

            else:
                raise ValueError(f"something's not right with a child {type(child)}")

    def _tree(self, node, tab=1):
        # print(f"{'  ' * tab}{node.tag} {node.text}")
        for child in node:
            self._tree(child, tab + 1)

    def _process_table(self, table, target: RawSection | RawTableCell):
        target_table = RawTable()
        target.add(target_table)
        for r_index, row in enumerate(table.rows):
            target_row = RawTableRow()
            target_table.add(target_row)
            cells = row.cells
            for c_index, cell in enumerate(cells):
                if cell._tc is not None:
                    x = cell._tc
                    right = x.right
                    left = x.left
                    top = x.top
                    try:
                        # Bottom method seems to have a bug.
                        # See https://github.com/python-openxml/python-docx/issues/1433
                        bottom = x.bottom
                    except Exception:
                        bottom = top + 1
                    h_span = right - left
                    v_span = bottom - top
                else:
                    h_span = 1
                    v_span = 1
                first = r_index == cell._tc.top and c_index == cell._tc.left
                target_cell = RawTableCell(h_span, v_span, first)
                target_row.add(target_cell)
                for block_item in self._iter_block_items(cell):
                    if isinstance(block_item, Paragraph):
                        self._process_cell(block_item, target_cell)
                    elif isinstance(block_item, Table):
                        raise self.LogicError("Table within table detected")
                    elif isinstance(block_item, etree._Element):
                        if block_item.tag == CT_TcPr:
                            pass
                        else:
                            logger.warning(f"Ignoring eTree element {block_item.tag}")
                    else:
                        raise self.LogicError(
                            f"something's not right with a child {type(block_item)}"
                        )

    def _process_cell(self, paragraph, target_cell: RawTableCell):
        if self._is_list(paragraph):
            list_level = self.get_list_level(paragraph)
            item = RawListItem(paragraph.extract_runs(), list_level)
            if target_cell.is_in_list():
                list = target_cell.current_list()
            else:
                list = RawList()
                target_cell.add(list)
            list.add(item)
        else:
            target_paragraph = RawParagraph(paragraph.extract_runs())
            target_cell.add(target_paragraph)

    def _process_paragraph(
        self, paragraph, target_section: RawSection, image_rels: dict
    ):
        is_heading, level = self._is_heading(paragraph.style.name)
        if is_heading:
            target_section = RawSection(paragraph.text, paragraph.text, level)
            self.target_document.add(target_section)
        elif self._is_list(paragraph):
            # print(f"START LIST: {paragraph.text}")
            list_level = self.get_list_level(paragraph)
            item = RawListItem(paragraph.extract_runs(), list_level)
            if target_section.is_in_list():
                list = target_section.current_list()
            else:
                list = RawList()
                target_section.add(list)
            list.add(item)
        elif "Graphic" in paragraph._p.xml:
            for rId in image_rels:
                if rId in paragraph._p.xml:
                    target_image = RawImage(image_rels[rId])
                    target_section.add(target_image)
        else:
            # print(f"START RUNS: {paragraph.text}")
            target_paragraph = RawParagraph(paragraph.extract_runs())
            target_section.add(target_paragraph)

    def get_list_level(self, paragraph):
        list_level = paragraph._p.xpath("./w:pPr/w:numPr/w:ilvl/@w:val")
        return int(str(list_level[0])) if list_level else 0

    def _is_heading(self, text):
        if re.match(r"^\d\dHeading \d", text):
            try:
                level = int(text[0:2])
                return True, level
            except Exception:
                return True, 0
        if re.match(r"^Heading \d", text):
            try:
                level = int(text[8])
                return True, level
            except Exception:
                return True, 0
        return False, 0

    def _is_list(self, paragraph):
        level = paragraph._p.xpath("./w:pPr/w:numPr/w:ilvl/@w:val")
        if level:
            return True
        if paragraph.style.name in ["CPT_List Bullet", "List Bullet"]:
            return True
        if paragraph.text:
            if hex(ord(paragraph.text[0])) == "0x2022":
                return True
        return False

    def _extract_images(self):
        archive = zipfile.ZipFile(self.full_path)
        for file in archive.filelist:
            if file.filename.startswith("word/media/"):
                # Extract the image file name from the path
                image_name = Path(file.filename).name
                # Create the target path for the image
                target_path = os.path.join(self.image_path, image_name)
                # Extract the file to the target path
                with archive.open(file) as source, open(target_path, "wb") as target:
                    target.write(source.read())

    def to_dict(self) -> dict:
        """Convert the RawDocx instance to a dictionary representation"""
        if hasattr(self, "target_document"):
            return {
                "type": "raw_docx",
                "document": self.target_document.to_dict()
                if hasattr(self.target_document, "to_dict")
                else None,
            }
        return {"type": "raw_docx", "document": None}
