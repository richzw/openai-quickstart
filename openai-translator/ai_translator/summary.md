

- Prompt 优化过程
  - 第一次尝试
    ```
    [{
        "role": "system",
        "content": "For the input text, translate it into {target_language} as native speaker"
    },
    {
        "role": "user",
        "content": "“Santiago,” the boy said.\n"
    }]
    ```
  
     - 问题
       - 表格格式没有保留
       - 翻译不准确，表现是没有把user 的content内容翻译成目标语言

  - 优化Prompt里system的描述
  
    ```shell
    [{
        "role": "system",
        "content": "From the input text, output each of these data in json format:\n\n
                    1. (language) Identify the language of input text \n
                    2. (translation) Translate to Chinese as a native speaker and keep the original character format of the text unchanged\n
                    3. (translation_language) The language translated from the input text"
    },
    {
        "role": "user",
        "content": "“Santiago,” the boy said.\n"
    } ]
    ```
  
     - 问题
       - 偶尔翻译不准确，表现是没有把user 的content内容翻译成目标语言

  - 再次优化Prompt，增加**黑魔法，think step by step**
    - 翻译text的prompt
    ```
       [{
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
    ```
    - 翻译table的prompt
  
    ```
         [{
            "role": "system",
            "content": f"From the input text, do a language translation job, here are the steps:\n\n"
                       f"1. (language) Identify the language of input text \n"
                       f"2. (translation) Translate the input text to {target_language} as a native speaker, format and maintain spacing (spaces, separators), and return in tabular form\n"
                       f"3. (output) output the language and translation in json format"
        },
            {
                "role": "user",
                "content": f"{table}"
            }
        ]
    ```

- 代码结构
  - 重构content
    ```mermaid
     classDiagram
     class Content
     Content : set_translation
     class ImageContent
     ImageContent : set_translation
     class TextContent
     TextContent : set_translation     
     Content <|-- ImageContent
     Content <|-- TextContent
    ```
  - 重构parser
    ```mermaid
     classDiagram
     class PageParser
     PageParser : parse
     class PageImageParser
     PageImageParser : parse
     class PageTableParser
     PageTableParser : parse
     class PageTextParser
     PageTextParser : parse     
     PageParser <|-- PageImageParser
     PageParser <|-- PageTableParser
     PageParser <|-- PageTextParser
    ```    
  - 重构writer
    ```mermaid
     classDiagram
     class Writer
     Writer : save
     class PDFWriter
     PDFWriter : save
     class MarkdownWriter
     MarkdownWriter : save     
     Writer <|-- PDFWriter
     Writer <|-- MarkdownWriter
    ```
    
- PDF格式
  - 为了保持PDF文档内容结构，需要保留原文档的空格，换行，分隔符等
  - 分段策略
    - 以空行为分段标志
  - 翻译后的文档，保持原文档的空格，换行，分隔符等
  ![](./images/pdf_translated_file.png)

- GUI 设计以及代码由 gpt4 生成
  - 如下是使用的prompt
    - 对一个翻译pdf功能的服务器设计一个GUI
    - 请用python实现一下
    - 请用 HTML、CSS 和 JavaScript 实现一个你上文提到的UI
    - 请增加这些功能显示文件上传和翻译进度、选择源语言和目标语言、处理文件上传大小的限制
    - 对于代码的错误，交给gpt4，让它来修复代码中的问题
  - 详见 https://chat.openai.com/share/0385f4c2-9585-4c90-bcf6-6bdadce1019c
  ![](./images/pdf_translator_gui.png)
  
- plugin开发
  - openapi文档的生成，通过gpt4生成
    - 通过把路由代码，交给gpt，然后让它生成对应的openapi文档，然后对应着plugin 官方文档修正下，就可以了



