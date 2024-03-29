# 필요한 라이브러리를 임포트합니다.
from flask import Flask, request, render_template_string, redirect, url_for
import fitz  # PyMuPDF를 위한 라이브러리, PDF 파일 처리에 사용
import csv  # CSV 파일 작업을 위한 라이브러리
import os  # 파일 시스템 경로와 관련된 작업을 위한 라이브러리
from PIL import Image  # 이미지 처리를 위한 라이브러리
import io  # 입출력 스트림을 다루는 라이브러리
import easyocr  # OCR(광학 문자 인식) 작업을 위한 라이브러리
import numpy as np  # 수치 계산을 위한 라이브러리

app = Flask(__name__)  # Flask 애플리케이션을 생성합니다.`
UPLOAD_FOLDER = 'uploads'  # 업로드된 파일을 저장할 폴더 이름을 정의합니다.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 앱 설정에 업로드 폴더 경로를 추가합니다.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 업로드 폴더를 생성합니다. 이미 존재하는 경우 생성하지 않습니다.

# HTML 템플릿을 문자열로 정의합니다. 이 템플릿은 PDF 파일을 업로드할 수 있는 간단한 폼을 포함합니다.
HTML_TEMPLATE = '''
<!doctype html>
<html>
<head><title>PDF to CSV Converter</title></head>
<body>
    <h1>PDF to CSV Converter</h1>
    <form method="post" action="/upload" enctype="multipart/form-data">
        <input type="file" name="pdf_file">
        <input type="submit" value="Convert to CSV">
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    # 루트 URL에 접속했을 때 HTML 템플릿을 렌더링하여 반환합니다.
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    # 파일 업로드를 처리하는 뷰 함수입니다.
    if 'pdf_file' not in request.files:
        # 업로드된 파일이 없을 경우, 에러 메시지를 반환합니다.
        return 'No file part'
    file = request.files['pdf_file']
    if file.filename == '':
        # 파일 이름이 없을 경우, 에러 메시지를 반환합니다.
        return 'No selected file'
    if file:
        # 파일이 존재하는 경우, 파일을 저장하고 PDF를 CSV로 변환하는 함수를 호출합니다.
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)
        convert_pdf_to_csv(pdf_path)
        # 파일 처리가 끝난 후 사용자를 홈페이지로 리디렉션합니다.
        return redirect(url_for('index'))

def convert_pdf_to_csv(pdf_path):
    # PDF 파일을 열고, 각 페이지에서 이미지를 추출하여 OCR을 수행한 뒤, 결과를 CSV 파일로 저장하는 함수입니다.
    doc = fitz.open(pdf_path)
    csv_path = os.path.splitext(pdf_path)[0] + '.csv'
    reader = easyocr.Reader(['ko','en'])  # 한국어와 영어를 인식하도록 설정
    image_paths = []

    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for page_num, page in enumerate(doc):
            img_list = page.get_images(full=True)
            if img_list:  # 페이지에 이미지가 존재하면 처리
                img = img_list[0]  # 첫 번째 이미지를 사용
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                image = Image.open(io.BytesIO(image_bytes))
                # 이미지를 저장하고 경로를 리스트에 추가
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"page_{page_num+1}_img.png")
                image.save(image_path)
                image_paths.append(image_path)

                np_image = np.array(image)  # OCR을 위해 NumPy 배열로 변환
                results = reader.readtext(np_image, detail=0)  # OCR 수행
                if results:
                    text = ' '.join(results)  # 인식된 텍스트를 합침
                    writer.writerow([text])  # CSV 파일에 텍스트를 씁니다.
    return csv_path, image_paths  # 생성된 CSV 파일 경로와 이미지 경로들을 반환합니다.

if __name__ == "__main__":
    app.run(debug=True)  # 애플리케이션을 디버그 모드로 실행합니다.
