from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin
import pdfplumber
import io
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator

argument_parser = ArgumentParser()
args = argument_parser.parse_arguments()
config_loader = ConfigLoader(args.config)

config = config_loader.load_config()

model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
model = OpenAIModel(model=model_name, api_key=api_key)

pdf_file_path = args.book if args.book else config['common']['book']
file_format = args.file_format if args.file_format else config['common']['file_format']

translator = PDFTranslator(model)

app = Flask(__name__)
CORS(app)

@app.route('/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    translator.translate_pdf(file, "PDF", request.form.get('dst_lang'), './jupyter')

    translated_pdf = io.BytesIO()
    origin_file_name = file.filename.split('.')[0]
    translated_file_name = origin_file_name + '_translated.pdf'
    with pdfplumber.open('./jupyter/' + translated_file_name) as pdf:
        for page in pdf.pages:
            translated_pdf.write(page.extract_text().encode('utf-8'))

    translated_pdf.seek(0)

    return send_file(translated_pdf, as_attachment=True, download_name='translated.pdf')


if __name__ == '__main__':
    app.run(port=8080, debug=True)
