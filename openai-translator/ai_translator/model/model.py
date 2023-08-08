from book import ContentType


class Model:
    def __init__(self):
        pass

    def make_text_prompt(self, text: str, target_language: str) -> list:
        return [{
            "role": "system",
            "content": f"You act as a language expert, do a language translation job, here are the steps:\n\n"
                       f"1. (language) Identify the language of input text \n"
                       f"2. (translation) Translate the input text to {target_language} as a native speaker \n"
                       f"3. (output) output the language and translation in json format\n"
        },
            {
                "role": "user",
                "content": f"{text}"
            }
        ]

    def make_table_prompt(self, table: str, target_language: str) -> list:
        return [{
            "role": "system",
            "content": f"From the input text, output each of these data products:\n\n"
                       f"1. (language) Identify the language of input text \n"
                       f"2. (translation) Translate the input text to {target_language} as a native speaker, format and maintain spacing (spaces, separators), and return in tabular form\n"
                       f"3. (output) output the language and translation in json format"
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
