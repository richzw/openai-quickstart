import pandas as pd
from enum import Enum, auto
from PIL import Image as PILImage
from utils import LOG

class ContentType(Enum):
    def __str__(self):
        return str(self.value)

    TEXT = auto()
    TABLE = auto()
    IMAGE = auto()

class Content:
    def __init__(self, content_type, original, blank_line_count: int = 1, skip_translation: bool = False, translation=None):
        self.content_type = content_type
        self.original = original
        # skip translation for header and footer of page for simplicity
        self.skip_translation = skip_translation
        self.blank_line_count = blank_line_count
        self.translation = translation
        self.status = False

    def set_translation(self, translation, status):
        if not self.check_translation_type(translation):
            raise ValueError(f"Invalid translation type. Expected {self.content_type}, but got {type(translation)}")
        self.translation = translation
        self.status = status

    def check_translation_type(self, translation):
        if self.content_type == ContentType.TEXT and isinstance(translation, str):
            return True
        elif self.content_type == ContentType.TABLE and isinstance(translation, list):
            return True
        elif self.content_type == ContentType.IMAGE and isinstance(translation, PILImage.Image):
            return True
        return False

class ImageContent(Content):
    def __init__(self, image, image_params, translation=None):
        if not isinstance(image, PILImage.Image):
            raise ValueError(f"Invalid image type. Expected PIL.Image, but got {type(image)}")
        self.image_params = image_params
        super().__init__(ContentType.IMAGE, image, translation)

    def set_translation(self, translation, status):
        self.translation = translation
        self.status = status

class TableContent(Content):
    def __init__(self, data, translation=None):
        df = pd.DataFrame(data)

        # Verify if the number of rows and columns in the data and DataFrame object match
        if len(data) != len(df) or len(data[0]) != len(df.columns):
            raise ValueError("The number of rows and columns in the extracted table data and DataFrame object do not match.")
        
        super().__init__(ContentType.TABLE, df)

    def set_translation(self, translation, status):
        try:
            # if not isinstance(translation, str):
            #     raise ValueError(f"Invalid translation type. Expected str, but got {type(translation)}")
            #
            # LOG.debug(translation)
            # # Convert the string to a list of lists
            # table_data = [row.strip().split() for row in translation.strip().split('\n')]
            LOG.debug(translation)
            # Create a DataFrame from the table_data
            translated_df = pd.DataFrame(translation[1:], columns=translation[0])
            LOG.debug(translated_df)
            self.translation = translated_df
            self.status = status
        except Exception as e:
            LOG.error(f"An error occurred during table translation: {e}")
            self.translation = None
            self.status = False

    def __str__(self):
        return "[" + self.original.to_string(header=False, index=False) + "]"

    def iter_items(self, translated=False):
        target_df = self.translation if translated else self.original
        for row_idx, row in target_df.iterrows():
            for col_idx, item in enumerate(row):
                yield (row_idx, col_idx, item)

    def update_item(self, row_idx, col_idx, new_value, translated=False):
        target_df = self.translation if translated else self.original
        target_df.at[row_idx, col_idx] = new_value

    def get_original_as_str(self):
        return "[" + self.original.to_string(header=False, index=False) + "]"