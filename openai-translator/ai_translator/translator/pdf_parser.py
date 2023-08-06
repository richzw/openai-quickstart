import pdfplumber
from typing import Optional
from book import Book, Page, Content, ContentType, TableContent, ImageContent
from translator.exceptions import PageOutOfRangeException
from utils import LOG
import re

class PDFParser:
    def __init__(self):
        pass

    def parse_pdf(self, pdf_file_path: str, pages: Optional[int] = None) -> Book:
        book = Book(pdf_file_path)

        with pdfplumber.open(pdf_file_path) as pdf:
            if pages is not None and pages > len(pdf.pages):
                raise PageOutOfRangeException(len(pdf.pages), pages)

            if pages is None:
                pages_to_parse = pdf.pages
            else:
                pages_to_parse = pdf.pages[:pages]

            for pdf_page in pages_to_parse:
                page = Page()

                # Store the original text content
                raw_text = pdf_page.extract_text(layout=True)
                # LOG.debug(f"[raw_text 1]\n {raw_text}")
                tables = pdf_page.extract_tables()
                # LOG.debug(f"[tables 1]\n {tables}")

                page_width, page_height = pdf_page.width, pdf_page.height
                header_bbox = (0, 0, page_width, page_height * 0.08)
                # Extract the header
                header = pdf_page.crop(header_bbox)
                header_text = header.extract_text()
                LOG.debug(f"[header_text]\n {header_text}")

                footer_bbox = (0, page_height * 0.92, page_width, page_height)
                # Extract the footer
                footer = pdf_page.crop(footer_bbox)
                footer_text = footer.extract_text()
                LOG.debug(f"[footer_text]\n {footer_text}")

                # Remove each cell's content from the original text
                for table_data in tables:
                    for row in table_data:
                        for cell in row:
                            raw_text = raw_text.replace(cell, "", 1)

                # Handling text
                if raw_text:
                    # # Remove empty lines and leading/trailing whitespaces
                    # raw_text_lines = raw_text.splitlines()
                    # LOG.debug(f"[raw_text_lines]\n {raw_text_lines}")
                    # cleaned_raw_text_lines = [line.strip() for line in raw_text_lines if line.strip()]
                    # LOG.debug(f"[cleaned_raw_text_lines]\n {cleaned_raw_text_lines}")
                    # cleaned_raw_text = "\n".join(cleaned_raw_text_lines)
                    # LOG.debug(f"[raw_text]\n {raw_text.splitlines()}")

                    # Remove empty lines and leading/trailing whitespaces
                    cleaned_raw_text_lines = []
                    prev_line_blank = True
                    blank_line_count = 0
                    for line in raw_text.splitlines():
                        line = line.strip()  # Remove leading and trailing white space
                        if line:  # If the line is not blank
                            if line[0].islower() and prev_line_blank:  # If the line starts with a lowercase letter and the previous line was blank
                                # remove the blank line that separates this line from the previous paragraph
                                if cleaned_raw_text_lines[-1][0] == '':
                                    cleaned_raw_text_lines = cleaned_raw_text_lines[:-1]
                            cleaned_raw_text_lines.append((line, blank_line_count))
                            prev_line_blank = False
                            blank_line_count = 0
                        elif not prev_line_blank:  # If the line is blank but the previous line wasn't
                            cleaned_raw_text_lines.append(('', 0))  # Add a blank line to separate paragraphs
                            prev_line_blank = True
                            blank_line_count += 1
                        else:
                            blank_line_count += 1

                    LOG.debug(f"[cleaned_raw_text_lines]\n {cleaned_raw_text_lines}")

                    # Split the text into paragraphs
                    is_new_paragraph = False
                    paragraph = ""
                    blank_line_count = 0
                    for line in cleaned_raw_text_lines:
                        if line and line[0]:
                            paragraph += line[0] + "\n"
                            if is_new_paragraph is False:
                                blank_line_count = line[1]
                            is_new_paragraph = True
                        else:
                            if is_new_paragraph:
                                skip_translation = False
                                if re.sub('\s+', ' ', paragraph).strip() == header_text or \
                                        paragraph.strip() == footer_text:
                                    skip_translation = True
                                text_content = Content(content_type=ContentType.TEXT,
                                                       original=paragraph,
                                                       blank_line_count=blank_line_count,
                                                       skip_translation=skip_translation)
                                page.add_content(text_content)
                                LOG.debug(f"[raw_text]\n {paragraph} \n {blank_line_count}")
                            is_new_paragraph = False
                            paragraph = ""

                # Handling tables
                if tables:
                    table = TableContent(tables)
                    page.add_content(table)
                    LOG.debug(f"[table]\n{table}")

                # Handling images
                images = pdf_page.images
                if images:
                    for i, img in enumerate(images):
                        img_box = (img["x0"], img["top"], img["x1"], img["bottom"])
                        img_params = (img["width"], img["height"])
                        image_content = ImageContent(pdf_page.crop(img_box).to_image(antialias=True, resolution=300).original, img_params)
                        page.add_content(image_content)

                book.add_page(page)

        return book
