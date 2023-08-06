from typing import Optional
from model import Model
from translator.pdf_parser import PDFParser
from translator.writer import Writer
from utils import LOG
import json
import time

class PDFTranslator:
    def __init__(self, model: Model):
        self.model = model
        self.pdf_parser = PDFParser()
        self.writer = Writer()

    def translate_pdf(self, pdf_file_path: str, file_format: str = 'PDF', target_language: str = 'Chinese', output_file_path: str = None, pages: Optional[int] = None):
        self.book = self.pdf_parser.parse_pdf(pdf_file_path, pages)

        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                time.sleep(60)
                prompt_messages = self.model.translate_prompt(content, target_language)
                LOG.debug(prompt_messages)
                if prompt_messages:
                    translation, status = self.model.make_request(prompt_messages)
                    LOG.info(translation)

                    translation_obj = json.loads(translation)
                    # TODO: validate the translation_obj and translation key exists
                    LOG.info(translation_obj)

                    # Update the content in self.book.pages directly
                    self.book.pages[page_idx].contents[content_idx].set_translation(translation_obj['translation'], status)
                else:
                    LOG.info("No prompt message generated, skip translation for " + content.content_type.name)
                    self.book.pages[page_idx].contents[content_idx].set_translation(content.original, True)

        self.writer.save_translated_book(self.book, output_file_path, file_format)
