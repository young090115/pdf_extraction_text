# 필요한 모듈과 패키지를 임포트합니다.
import csv
import os
from flask import Flask, request, render_template, redirect, url_for
import fitz  # PyMuPDF를 사용하기 위해 fitz를 임포트합니다.

# Flask 애플리케이션 인스턴스를 생성합니다.
app = Flask(__name__)

# 파일 업로드를 위한 폴더 경로를 설정합니다.
UPLOAD_FOLDER = 'uploads'
# 파일 다운로드를 위한 폴더 경로를 설정합니다.
DOWNLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# 설정한 폴더 경로가 없으면 생성합니다. 이미 있으면 그대로 유지합니다.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 웹 애플리케이션의 루트 경로에 접근할 때 호출됩니다.
@app.route('/')
def index():
    # index.html을 렌더링하여 사용자에게 보여줍니다.
    return render_template('index.html')

# 파일 업로드를 처리하는 경로 및 함수입니다. POST 메소드를 사용합니다.
@app.route('/upload', methods=['POST'])
def upload_file():
    # 요청에서 'pdf_files[]' 이름의 파일이 있는지 확인합니다.
    if 'pdf_files[]' not in request.files:
        return 'No file part'
    files = request.files.getlist('pdf_files[]')
    # 선택된 파일이 없으면 메시지를 반환합니다.
    if not files or files[0].filename == '':
        return 'No selected file'
    for file in files:
        if file:
            # 파일을 저장할 경로를 설정합니다.
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            # 파일을 설정한 경로에 저장합니다.
            file.save(pdf_path)
            # PDF 파일을 CSV 파일로 변환하는 함수를 호출합니다.
            convert_pdf_to_csv(pdf_path)
    # 파일 업로드 후에는 index 페이지로 리다이렉트합니다.
    return redirect(url_for('index'))

# 이전 코드에서 사용된 `extract` 함수는 Flask 웹 애플리케이션에서는 사용되지 않습니다. 
# PDFRectExtractor의 기능은 웹 인터페이스를 통해서는 직접적으로 사용되지 않으며, 
# 대신 사용자가 업로드한 PDF 파일을 처리하는 데 필요한 로직을 `convert_pdf_to_csv` 함수 내에 직접 구현해야 합니다.

# PDF 파일을 CSV 파일로 변환하는 함수입니다.
def convert_pdf_to_csv(pdf_path):
    # PDF 파일을 엽니다.
    doc = fitz.open(pdf_path)
    # 생성될 CSV 파일의 이름을 설정합니다.
    csv_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.csv'
    # CSV 파일을 저장할 경로를 설정합니다.
    csv_path = os.path.join(app.config['DOWNLOAD_FOLDER'], csv_filename)
    
    # CSV 파일을 작성합니다.
    with open(csv_path, 'w', newline='', encoding='ANSI') as csv_file:  # 인코딩을 'ANSI'에서 'utf-8'로 변경
        writer = csv.writer(csv_file)
        # CSV 파일의 헤더를 작성합니다.
        writer.writerow(['key', 'value'])

        for page in doc:
            # 여기서 사각형 좌표를 동적으로 받아올 수 있는 방법은 현재 웹 기반 구조에서 직접적으로 구현하기 어렵습니다.
            rect = fitz.Rect(103.0,141.0,325.0,163.0)  # 예시 좌표, 실제로는 사용자 입력을 통해 동적으로 받아와야 합니다.
            # 설정한 영역에서 텍스트를 추출합니다.
            text = page.get_text("text", clip=rect)
            # CSV 파일에 데이터를 추가합니다.
            writer.writerow(["소재지", text])
            # 이 부분은 사용자가 직접 좌표를 입력하는 방식으로 수정이 필요합니다.

# Flask 애플리케이션을 실행합니다.
if __name__ == '__main__':
    app.run(debug=True)
