# import os
# import cv2
# import numpy as np
# from pdf2image import convert_from_path
# from PIL import Image
# import easyocr
# import re

# class PDFConverter_kor:
#     def __init__(self, pdf_path, output_dir):
#         self.pdf_path = pdf_path
#         self.output_dir = output_dir
    
#     def convert_to_images(self):
#         os.makedirs(self.output_dir, exist_ok=True)
#         pages = convert_from_path(self.pdf_path)
#         for i, page in enumerate(pages):
#             image_path = os.path.join(self.output_dir, f"MAHT_page{(i)}.png")
#             page.save(image_path, "PNG")
#         print('저장완료')

# class ImageProcessor_kor:
#     def __init__(self, image_path, templates):
#         self.image_path = image_path
#         self.templates = templates
#         self.header = None
#         self.body = None
#         self.left_body = None
#         self.right_body = None

#     def process_image(self):
#         src = cv2.imread(self.image_path)
#         gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#         edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

#         # 이진화
#         _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

#          # 윤곽선 찾기
#         contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         # 가로선 찾기
#         horizontal_lines = []
#         for contour in contours:
#             x, y, w, h = cv2.boundingRect(contour)
#             if w > 700 and h < 50:  # 너비가 특정 값 이상이고 높이가 작은 가로선 찾기
#                 horizontal_lines.append((x, y, w, h))

#         # 제일 작은 y값을 가진 가로선 찾기
#         if horizontal_lines:
#             horizontal_lines.sort(key=lambda line: line[1])  # y 값을 기준으로 정렬
#             smallest_y_line = horizontal_lines[0]  # y 값이 제일 작은 가로선
#             x, y, w, h = smallest_y_line
#             cut_line = y + h // 2  # 가로선의 중심 위치 계산

#             # 상단과 하단 부분 분리
#             header = src[:cut_line, :]
#             body = src[cut_line:, :]

#             self.header = header
#             self.body = body

#             # 좌우로 나누기
#             height, width, _ = self.body.shape
#             center = width // 2
#             self.left_body = self.body[:, :center-5]
#             self.right_body = self.body[:, center+5:]
#         else:
#             print("가로로 긴 선을 찾을 수 없습니다.")

#     def match_template(self, src, template):
#         gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
#         template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
#         result = cv2.matchTemplate(gray, template_gray, cv2.TM_CCOEFF_NORMED)
#         _, max_val, _, _ = cv2.minMaxLoc(result)
#         return max_val

#     def process_template_image(self):
#         src = cv2.imread(self.image_path)
#         best_template = None
#         best_match_val = 0
#         for template_path in self.templates:
#             template = cv2.imread(template_path)
#             match_val = self.match_template(src, template)
#             if match_val > best_match_val:
#                 best_match_val = match_val
#                 best_template = template

#         if best_template is not None:
#             gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
#             template_gray = cv2.cvtColor(best_template, cv2.COLOR_BGR2GRAY)
#             result = cv2.matchTemplate(gray, template_gray, cv2.TM_CCOEFF_NORMED)
#             _, _, min_loc, _ = cv2.minMaxLoc(result)
#             th, tw = template_gray.shape[:2]
#             cut_line = min_loc[1] + th // 2
#             self.header = src[:cut_line, :]
#             self.body = src[cut_line:, :]
#             height, width, _ = self.body.shape
#             center = width // 2
#             self.left_body = self.body[:, :center-5]
#             self.right_body = self.body[:, center+5:]
#         else:
#             print("적합한 템플릿을 찾을 수 없습니다.")

#     def save_processed_images(self, output_path_left, output_path_right):
#         if self.left_body is None or self.right_body is None:
#             print("이미지가 처리되지 않았습니다. process_image() 메서드를 호출하여 이미지를 처리하세요.")
#             return
#         cv2.imwrite(output_path_left, self.left_body)
#         cv2.imwrite(output_path_right, self.right_body)

# # G3인 경우 평가원에 해당하는(6,9,11월에 대한 전처리 따로 진행)
# class ImageProcessorG3_6_9_11_math:
#     def __init__(self, image_path):
#         self.image_path = image_path
#         self.header = None
#         self.left_header = None
#         self.right_header = None
#         self.body = None  # 추가: 이미지 body를 저장할 변수
#         self.left_body = None  # 좌측 이미지 body 변수
#         self.right_body = None  # 우측 이미지 body 변수

#     def process_image(self):
#         src = cv2.imread(self.image_path)
#         gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#         edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

#         # 이진화
#         _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

#          # 윤곽선 찾기
#         contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         # 가로선 찾기
#         horizontal_lines = []
#         for contour in contours:
#             x, y, w, h = cv2.boundingRect(contour)
#             horizontal_lines.append((x, y, w, h))

#         # h 값이 가장 큰 가로선 찾기
#         if horizontal_lines:
#             largest_h_line = max(horizontal_lines, key=lambda line: line[3])  
#             x, y, w, h = largest_h_line           
#             cut_line = y 

#             # 상단과 하단 부분 분리
#             header = src[:cut_line, :]
#             body = src[cut_line:, :]

#             self.header = header
#             self.body = body

#             # 좌우로 나누기
#             height, width, _ = self.body.shape
#             center = width // 2
#             self.left_body = self.body[:, :center-5]
#             self.right_body = self.body[:, center+5:]
#         else:
#             print("가로로 긴 선을 찾을 수 없습니다.")

#         # # 좌우로 나누기
#         # height, width, _ = self.body.shape
#         # center = width // 2
#         # self.left_body = self.body[:, :center-5]
#         # self.right_body = self.body[:, center+5:]

#         # 안 잘릴 때 (left:center / right:center)

#     def match_template(self, src, template):
#         gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
#         template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
#         result = cv2.matchTemplate(gray, template_gray, cv2.TM_CCOEFF_NORMED)
#         _, max_val, _, _ = cv2.minMaxLoc(result)
#         return max_val

#     def process_template_image(self):
#         src = cv2.imread(self.image_path)
#         best_template = None
#         best_match_val = 0
#         for template_path in self.templates:
#             template = cv2.imread(template_path)
#             match_val = self.match_template(src, template)
#             if match_val > best_match_val:
#                 best_match_val = match_val
#                 best_template = template

#         if best_template is not None:
#             gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
#             template_gray = cv2.cvtColor(best_template, cv2.COLOR_BGR2GRAY)
#             result = cv2.matchTemplate(gray, template_gray, cv2.TM_CCOEFF_NORMED)
#             _, _, min_loc, _ = cv2.minMaxLoc(result)
#             th, tw = template_gray.shape[:2]
#             cut_line = min_loc[1] + th // 2
#             self.header = src[:cut_line, :]
#             self.body = src[cut_line:, :]
#             height, width, _ = self.body.shape
#             center = width // 2
#             self.left_body = self.body[:, :center-5]
#             self.right_body = self.body[:, center+5:]
#         else:
#             print("적합한 템플릿을 찾을 수 없습니다.")

#     def save_processed_images(self, output_path_left, output_path_right):
#         if self.left_body is None or self.right_body is None:
#             print("이미지가 처리되지 않았습니다. process_image() 메서드를 호출하여 이미지를 처리하세요.")
#             return
#         cv2.imwrite(output_path_left, self.left_body)
#         cv2.imwrite(output_path_right, self.right_body)
    

# class Crop_kor:
#     def __init__(self):
#         self.counter  = 0

#     def contour(self, page_rl, base_filename):
#         imgray = cv2.cvtColor(page_rl, cv2.COLOR_RGB2GRAY)
#         img2 = imgray.copy()
#         blur = cv2.GaussianBlur(imgray, (3,3), sigmaX=0)
#         thresh = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
#         edge = cv2.Canny(imgray, 100, 200)
#         kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1000, 200))
#         closed = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel)
#         contours, hierarchy = cv2.findContours(closed.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#         contours_xy = np.array(contours, dtype=object)
#         contours = reversed(contours)
#         top = []
#         for c in contours:
#             x, y, w, h = cv2.boundingRect(c)
#             top.append(y)
#             total = len(top)-1
#         for i in range(total):
#             if i==0:
#                 img_trim = page_rl[top[i] : top[i+1]-5, :]
#             else:
#                 img_trim = page_rl[top[i]-10 : top[i+1]-5, :]
#             if img_trim.size == 0:
#                 print(f"Empty cropped image for {base_filename}")
#                 continue
#             output_path = f"{base_filename}_cropped_{self.counter}.png"
#             print(f"Saving cropped image to: {output_path}")
#             cv2.imwrite(output_path, img_trim)
#             self.counter += 1







import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import easyocr
import re

class PDFConverter_kor:
    def __init__(self, pdf_path, output_dir):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
    
    def convert_to_images(self):
        os.makedirs(self.output_dir, exist_ok=True)
        pages = convert_from_path(self.pdf_path)
        for i, page in enumerate(pages):
            image_path = os.path.join(self.output_dir, f"_page{(i)}.png")
            page.save(image_path, "PNG")
        print('저장완료')

class ImageProcessor_kor:
    def __init__(self, image_path, templates):
        self.image_path = image_path
        self.templates = templates
        self.header = None
        self.body = None
        self.left_body = None
        self.right_body = None

    def process_image(self):
        src = cv2.imread(self.image_path)
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

        # 이진화
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

         # 윤곽선 찾기
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 가로선 찾기
        horizontal_lines = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 700 and h < 50:  # 너비가 특정 값 이상이고 높이가 작은 가로선 찾기
                horizontal_lines.append((x, y, w, h))

        # 제일 작은 y값을 가진 가로선 찾기
        if horizontal_lines:
            horizontal_lines.sort(key=lambda line: line[1])  # y 값을 기준으로 정렬
            smallest_y_line = horizontal_lines[0]  # y 값이 제일 작은 가로선
            x, y, w, h = smallest_y_line
            cut_line = y + h // 2  # 가로선의 중심 위치 계산

            # 상단과 하단 부분 분리
            header = src[:cut_line, :]
            body = src[cut_line:, :]

            self.header = header
            self.body = body

            # 좌우로 나누기
            height, width, _ = self.body.shape
            center = width // 2
            self.left_body = self.body[:, :center-5]
            self.right_body = self.body[:, center+5:]
        else:
            print("가로로 긴 선을 찾을 수 없습니다.")

    def save_processed_images(self, output_path_left, output_path_right):
        if self.left_body is None or self.right_body is None:
            print("이미지가 처리되지 않았습니다. process_image() 메서드를 호출하여 이미지를 처리하세요.")
            return
        cv2.imwrite(output_path_left, self.left_body)
        cv2.imwrite(output_path_right, self.right_body)

# G3인 경우 평가원에 해당하는(6,9,11월에 대한 전처리 따로 진행)
class ImageProcessorG3_6_9_11_kor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.header = None
        self.left_header = None
        self.right_header = None
        self.body = None  # 추가: 이미지 body를 저장할 변수
        self.left_body = None  # 좌측 이미지 body 변수
        self.right_body = None  # 우측 이미지 body 변수

    def process_image(self):
        src = cv2.imread(self.image_path)
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

        # 이진화
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

         # 윤곽선 찾기
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 가로선 찾기
        horizontal_lines = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            horizontal_lines.append((x, y, w, h))

        # h 값이 가장 큰 가로선 찾기
        if horizontal_lines:
            largest_h_line = max(horizontal_lines, key=lambda line: line[3])  
            x, y, w, h = largest_h_line           
            cut_line = y 

            # 상단과 하단 부분 분리
            header = src[:cut_line, :]
            body = src[cut_line:, :]

            self.header = header
            self.body = body

            # 좌우로 나누기
            height, width, _ = self.body.shape
            center = width // 2
            self.left_body = self.body[:, :center-5]
            self.right_body = self.body[:, center+5:]
        else:
            print("가로로 긴 선을 찾을 수 없습니다.")

        # # 좌우로 나누기
        # height, width, _ = self.body.shape
        # center = width // 2
        # self.left_body = self.body[:, :center-5]
        # self.right_body = self.body[:, center+5:]

        # 안 잘릴 때 (left:center / right:center)


    def save_processed_images(self, output_path_left, output_path_right):
        if self.left_body is None or self.right_body is None:
            print("이미지가 처리되지 않았습니다. process_image() 메서드를 호출하여 이미지를 처리하세요.")
            return
        cv2.imwrite(output_path_left, self.left_body)
        cv2.imwrite(output_path_right, self.right_body)
    

class NumberDotImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.header = None
        self.left_header = None
        self.right_header = None
        self.body = None
        self.left_body = None
        self.right_body = None

    def process_image(self):
        src = cv2.imread(self.image_path)
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

        # EasyOCR을 사용하여 숫자와 점을 인식하고 좌표를 얻습니다.
        reader = easyocr.Reader(['ko'])
        results = reader.readtext(self.image_path)

        # 숫자와 점 다음 영역을 자를 때 사용할 좌표 초기화
        start_x = 0
        start_y = 0
        end_x = src.shape[1]
        end_y = src.shape[0]

        # 숫자와 점 다음 영역의 시작점 찾기
        for (bbox, text, prob) in results:
            if re.match(r'^[\d.]+$', text):  # 숫자와 점으로 시작하는 텍스트 패턴
                start_x = bbox[0][0]  # 첫 번째 점의 x 좌표로 시작점 설정
                break  # 첫 번째로 발견된 숫자와 점 다음 영역으로 설정

        # 시작점 이후에 나오는 텍스트의 높이를 기준으로 끝점 설정
        for (bbox, text, prob) in results:
            if bbox[0][1] > start_y and re.match(r'^[\d.]+$', text):
                end_y = bbox[0][1]  # 첫 번째 점보다 y 좌표가 클 경우 끝점 설정
                break  # 첫 번째로 발견된 숫자와 점 다음 영역으로 설정

        # 이미지를 자릅니다.
        self.body = src[start_y:end_y, start_x:end_x]

    def save_processed_image(self, output_path):
        if self.body is None:
            print("이미지가 처리되지 않았습니다. process_image() 메서드를 호출하여 이미지를 처리하세요.")
            return
        cv2.imwrite(output_path, self.body)