import tkinter as tk
from tkinter import filedialog, messagebox  # 파일 열기 대화 상자 및 메시지 상자를 사용하기 위한 tkinter 서브 모듈
from PIL import Image, ImageTk  # 이미지 처리 및 Tkinter와의 호환을 위한 PIL 모듈
import fitz  # PDF 파일을 다루기 위한 PyMuPDF 라이브러리

class PDFViewer:
    def __init__(self, master):
        # 생성자에서는 PDF 뷰어의 기본 UI 및 상태를 초기화합니다.
        self.master = master  # Tkinter의 상위 위젯
        self.canvas = tk.Canvas(master, cursor="cross")  # PDF 페이지를 그릴 캔버스 생성
        self.canvas.pack(fill=tk.BOTH, expand=True)  # 캔버스를 화면에 배치
        self.current_page = 0  # 현재 표시되는 PDF 페이지 번호
        self.images = []  # PDF의 각 페이지를 이미지로 변환하여 저장할 리스트
        self.rect = None  # 사용자가 그린 사각형의 참조를 저장
        self.start_x = None  # 사각형 그리기 시작 X 좌표
        self.start_y = None  # 사각형 그리기 시작 Y 좌표

        # PDF 열기, 이전 페이지, 다음 페이지, 좌표 추출 버튼 생성 및 배치
        self.open_button = tk.Button(master, text="Open PDF", command=self.open_pdf)
        self.open_button.pack(side=tk.LEFT)

        self.prev_button = tk.Button(master, text="Previous", command=self.prev_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(master, text="Next", command=self.next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT)

        self.extract_button = tk.Button(master, text="Extract Coordinates", command=self.extract_coordinates)
        self.extract_button.pack(side=tk.LEFT)

        self.page_label = tk.Label(master, text="")  # 현재 페이지 번호를 표시할 레이블
        self.page_label.pack(side=tk.LEFT)

        # 마우스 이벤트 바인딩: 사각형 그리기 시작 및 이동 처리
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)

    def open_pdf(self):
        # PDF 파일 열기 대화 상자를 통해 파일 선택 및 열기
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.doc = fitz.open(file_path)  # 선택된 PDF 파일 열기
            # PDF의 각 페이지를 이미지로 변환하여 리스트에 저장
            self.images = [self.load_page_image(page) for page in range(len(self.doc))]
            self.current_page = 0  # 현재 페이지를 첫 페이지로 설정
            self.display_page(self.current_page)  # 첫 페이지 표시
            self.update_buttons()  # 버튼 상태 업데이트

    def load_page_image(self, page_number):
        # PDF 페이지를 이미지로 변환하는 함수
        page = self.doc.load_page(page_number)  # 주어진 번호의 페이지 로드
        pix = page.get_pixmap()  # 페이지를 pixmap으로 변환
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # pixmap을 PIL 이미지로 변환
        photo = ImageTk.PhotoImage(image=img)  # Tkinter에서 사용 가능한 이미지로 변환
        return photo

    def display_page(self, page_number):
        # 주어진 번호의 PDF 페이지를 캔버스에 표시
        self.canvas.delete("all")  # 이전에 캔버스에 그려진 모든 요소 제거
        self.canvas.create_image(0, 0, image=self.images[page_number], anchor=tk.NW)  # 새 페이지 이미지 캔버스에 추가
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))  # 스크롤 영역 설정
        # 페이지 레이블 업데이트
        self.page_label.config(text=f"Page {page_number + 1} of {len(self.doc)}")

    # 이하 함수들은 사용자 상호작용에 따른 이벤트 핸들러 및 페이지 네비게이션을 위한 로직을 포함합니다.
    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x + 1, self.start_y + 1, outline='red')

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    #버튼 클릭 시 messagebox 팝업 
    def extract_coordinates(self):
        if self.rect:
            #해당 네모박스 좌표
            coords = self.canvas.coords(self.rect)
            messagebox.showinfo("Coordinates", f"Rectangle coordinates: {coords}")
        else:
            messagebox.showerror("Error", "No rectangle has been drawn.")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page(self.current_page)
            self.update_buttons()

    def next_page(self):
        if self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.display_page(self.current_page)
            self.update_buttons()

    def update_buttons(self):
        self.prev_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < len(self.doc) - 1 else tk.DISABLED)

def main():
    root = tk.Tk()
    root.title("PDF Viewer with Coordinate Extraction")
    pdf_viewer = PDFViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
