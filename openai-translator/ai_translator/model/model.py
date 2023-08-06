from book import ContentType


class Model:
    def __init__(self):
        pass

    def make_text_prompt(self, text: str, target_language: str) -> list:
        return [{
            "role": "system",
            "content": f"From the input text, output each of these data products in json format:\n\n1. (language) Identify the language of input text \n2. (translation) Translate to {target_language} as a native speaker and keep the original character format of the text unchanged\n3.(translation_language) The language translated from the input text"
        },
            {
                "role": "user",
                "content": f"{text}"
            }
        ]

    def make_table_prompt(self, table: str, target_language: str) -> list:
        # return f"翻译为{target_language}，保持间距（空格，分隔符），以表格形式返回：\n{table}" Maintain spacing (spaces, separators), and return in tabular form
        return [{
            "role": "system",
            "content": f"From the input text, output each of these data products:\n\n1. (language) Identify language\n2. (translation) Translate to {target_language} as a native speaker, format and maintain spacing (spaces, separators), and return in tabular form\n3. (output) output using the data products: [language, translation] in json format"
        },
            {
                "role": "user",
                "content": f"{table}"
            }
        ]

    def translate_prompt(self, content, target_language: str) -> list:
        if content.content_type == ContentType.TEXT and not content.skip_translation:
            return self.make_text_prompt(content.original, target_language)
        elif content.content_type == ContentType.TABLE:
            return self.make_table_prompt(content.get_original_as_str(), target_language)

    def make_request(self, prompt_messages: list):
        raise NotImplementedError("子类必须实现 make_request 方法")
