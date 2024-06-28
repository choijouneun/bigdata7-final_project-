import os
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np

# pdf to image
class PDFConverter:
    def __init__(self, pdf_path, output_dir):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
    
    def convert_to_images(self):
        # 출력 디렉토리 생성 (없으면)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # PDF를 이미지로 변환
        pages = convert_from_path(self.pdf_path)
        
        # Save each page as a PNG image
        for i, page in enumerate(pages):
            image_path = os.path.join(self.output_dir, f"math_page{(i)}.png")
            page.save(image_path, "PNG")
        
        print('저장완료')

class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.header = None
        self.left_header = None
        self.right_header = None

    # def process_image(self):
    #     src = cv2.imread(self.image_path)
    #     dst = src.copy()

    #     gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    #     edges = cv2.Canny(gray, 5000, 1500, apertureSize=5, L2gradient=True)

    #     lines = cv2.HoughLines(edges, 0.8, np.pi / 180, 220,
    #                         srn=100, stn=200, min_theta=89, max_theta=91)

    #     min_y = 700

    #     for i in lines:
    #         rho, theta = i[0][0], i[0][1]
    #         a, b = np.cos(theta), np.sin(theta)
    #         x0, y0 = a * rho, b * rho

    #         scale = src.shape[0] + src.shape[1]

    #         x1 = int(x0 + scale * -b)
    #         y1 = int(y0 + scale * a)
    #         x2 = int(x0 - scale * -b)
    #         y2 = int(y0 - scale * a)

    #         if y2 < min_y:
    #             min_y = y2

    #         cv2.line(dst, (x1, y1), (x2, y2), (0, 0, 255), 2)



    def process_image(self):
        src = cv2.imread(self.image_path)
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

        # HoughLines 파라미터
        min_y = 460 # 기본값으로 설정 (필요에 따라 조정 가능)    

        # 찾은 가로 직선 기준으로 위쪽은 header, 아래쪽은 body로 자르기
        header = src[:min_y, :]
        body = src[min_y + 5:, :]

        self.header = header
        self.body = body

        # 좌우로 나누기
        height, width, _ = self.body.shape
        center = width // 2
        self.left_body = self.body[:, :center-5]
        self.right_body = self.body[:, center+5:]

    def save_processed_images(self, output_path_left, output_path_right):
        cv2.imwrite(output_path_left, self.left_body)
        cv2.imwrite(output_path_right, self.right_body)

# 빈 페이지를 입력받고 크롭
class Crop:
    def __init__(self):
        self.counter  = 0

    def contour(self, page_rl, base_filename):
        print("contour")
    
        # 이미지 흑백화
        imgray = cv2.cvtColor(page_rl, cv2.COLOR_RGB2GRAY)
        img2=imgray.copy()

        # 이미지 이진화
        blur = cv2.GaussianBlur(imgray, (3,3), sigmaX=0)
        thresh = cv2.threshold(blur, 70, 255,
                               cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        
        # Morph operations
        edge = cv2.Canny(imgray, 100, 200)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1000, 200)) # 영역 수정
        closed = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel)

        # 문제영역 윤곽 잡기 - contours가 찾은 경계의 배열
        contours, hierarchy = cv2.findContours(closed.copy(), 
                                               cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        contours_xy = np.array(contours, dtype=object)

        # largest_contour = max(contours, key=cv2.contourArea)
        contours_xy.shape

        # 한 페이지 내에서 문제 순서대로 불러오기
        contours = reversed(contours)

        # 한 페이지 내의 모든 폐곡선 범위에 대해 실행
        top=[] # 폐곡선의 맨 위 x값을 담아놓는 배열

        for c in contours:
            # 폐곡선 바운더리
            x, y, w, h =cv2.boundingRect(c)
            top.append(y)

            # 시각화 위한 컨투어 그리기
            cv2.rectangle(page_rl, (x, y), (x + w, y + h), (0, 255, 0), 2)
            total = len(top)-1

        for i in range(total):
            # 맨 위 문제 제외 위쪽 여백 추가
            if i==0:
                img_trim = page_rl[top[i] : top[i+1]-5,:]
            else:
                img_trim = page_rl[top[i]-10 : top[i+1]-5, :]

            # 크롭된 이미지가 비어 있는지 확인
            if img_trim.size == 0:
                print(f"Empty cropped image for {base_filename}")
                continue

            # 크롭 이미지 저장
            output_path = f"{base_filename}_cropped_{self.counter}.png"
            print(f"Saving cropped image to: {output_path}")
            cv2.imwrite(output_path, img_trim)
            self.counter += 1







