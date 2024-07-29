import os, easyocr
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np

# pdf to image
class PDFConverter_math:
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
            image_path = os.path.join(self.output_dir, f"MATH_page{str(i+1).zfill(2)}.png")
            page.save(image_path, "PNG")
        
        print('저장완료')

class ImageProcessor_math:
    def __init__(self, image_path, page_num):
        self.image_path = image_path
        self.page_num = page_num
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
            
        # self.left_body = self.body[:, :center-5]
        # self.right_body = self.body[:, center+5:]

        # self.left_body = self.body[:, :center-35]
        # self.right_body = self.body[:, center-20:]
    
    def save_processed_images(self, output_dir, base_filename):
        if self.left_body is None or self.right_body is None:
            print("이미지가 처리되지 않았습니다. process_image() 메서드를 호출하여 이미지를 처리하세요.")
            return
        
        left_output_path = os.path.join(output_dir, f"{base_filename}_left_{self.page_num:02d}.png")
        right_output_path = os.path.join(output_dir, f"{base_filename}_right_{self.page_num:02d}.png")

        cv2.imwrite(left_output_path, self.left_body)
        cv2.imwrite(right_output_path, self.right_body)


# G3인 경우 평가원에 해당하는(6,9,11월에 대한 전처리 따로 진행)
class ImageProcessorG3_6_9_11_math:
    def __init__(self, image_path, page_num):
        self.image_path = image_path
        self.page_num = page_num
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

        # self.left_body = self.body[:, :center-5]
        # self.right_body = self.body[:, center+5:]

        # 안 잘릴 때 (left:center / right:center)
    
    def save_processed_images(self, output_dir, base_filename):
        if self.left_body is None or self.right_body is None:
            print("이미지가 처리되지 않았습니다. process_image() 메서드를 호출하여 이미지를 처리하세요.")
            return
        
        left_output_path = os.path.join(output_dir, f"{base_filename}_left_{self.page_num:02d}.png")
        right_output_path = os.path.join(output_dir, f"{base_filename}_right_{self.page_num:02d}.png")

        cv2.imwrite(left_output_path, self.left_body)
        cv2.imwrite(right_output_path, self.right_body)

class Crop_math:
    def __init__(self):
        self.counter = 1

    def contour(self, image_path, base_filename):
        print("contour")

        page_rl = cv2.imread(image_path)
        if page_rl is None:
            print(f"Could not read the image: {image_path}")
            return

        # 이미지 흑백화
        imgray = cv2.cvtColor(page_rl, cv2.COLOR_RGB2GRAY)
        img2 = imgray.copy()

        # 이미지 이진화
        blur = cv2.GaussianBlur(imgray, (3, 3), sigmaX=0)
        thresh = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Morph operations
        edge = cv2.Canny(imgray, 100, 200)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1000, 120))  # 영역 수정
        closed = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel)

        # 문제영역 윤곽 잡기 - contours가 찾은 경계의 배열
        contours, hierarchy = cv2.findContours(closed.copy(),
                                               cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        contours_xy = np.array(contours, dtype=object)

        # 한 페이지 내에서 문제 순서대로 불러오기
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])  # y 값을 기준으로 정렬

        if not contours:
            print(f"No contours found in {base_filename}")
            return

        # 한 페이지 내의 모든 폐곡선 범위에 대해 실행
        top = []  # 폐곡선의 맨 위 y값을 담아놓는 배열

        for c in contours:
            # 폐곡선 바운더리
            x, y, w, h = cv2.boundingRect(c)
            top.append(y)

        total = len(top) - 1

        for i in range(total):
            # 맨 위 문제 제외 위쪽 여백 추가
            if i == 0:
                img_trim = page_rl[top[i]: top[i + 1] - 5, :]
            else:
                img_trim = page_rl[top[i] - 10: top[i + 1] - 5, :]

            # 크롭된 이미지가 비어 있는지 확인
            if img_trim.size == 0:
                print(f"Empty cropped image for {base_filename}")
                continue

            # 크롭 이미지 저장
            output_path = os.path.join(os.path.dirname(base_filename), f"{os.path.basename(os.path.dirname(base_filename))}_{self.counter:02d}.png")
            print(f"Saving cropped image to: {output_path}")
            cv2.imwrite(output_path, img_trim)
            self.counter += 1

class ImageTrimmer:
    def __init__(self, folder):
        self.folder = folder

    def trim_whitespace(self, image_path, output_path):
        # 이미지 열기
        image = Image.open(image_path)
        
        # 이미지를 numpy 배열로 변환
        np_image = np.array(image)
        
        # 흰색이 아닌 픽셀의 경계를 찾기
        mask = np_image[:, :, :3] != 255  # RGB 채널에서 흰색(255, 255, 255)이 아닌 부분을 찾기
        coords = np.argwhere(mask)

        if coords.size == 0:  # 만약 흰색이 아닌 픽셀이 없다면
            print(f"No non-white pixels found in {image_path}")
            return
        
        # 경계 좌표 가져오기
        x0, y0 = coords.min(axis=0)[:2]
        x1, y1 = coords.max(axis=0)[:2] + 1  # max 좌표는 포함되지 않으므로 +1
        
        # 이미지를 자르기
        cropped_image = image.crop((y0, x0, y1, x1))
        
        # 결과 이미지 저장
        cropped_image.save(output_path)
        print(f"Cropped image saved to {output_path}")

    def process_images(self):
        # 입력 폴더 내의 모든 파일을 확인
        for filename in os.listdir(self.folder):
            if filename.endswith(".png"):  # PNG 파일만 처리
                image_path = os.path.join(self.folder, filename)
                
                # 여백 자르기 함수 호출
                self.trim_whitespace(image_path, image_path)

class TextCutter:
    def __init__(self, keywords=None, offset=20):
        self.reader = easyocr.Reader(['ko'])
        self.keywords = keywords if keywords else ["5지선다형", "5 지선다 형", "5지 선다형", "5 지선다형", "5지 선다형( ~ 21)", "단답형", "단답 형", "단 답 형"]
        self.offset = offset

    def cut_image_below_text(self, image_path, output_dir):
        # 이미지 로드
        image = cv2.imread(image_path)

        # 이미지에서 텍스트 인식
        results = self.reader.readtext(image)

        # 키워드 위치 찾기
        for (bbox, text, prob) in results:
            for keyword in self.keywords:
                if keyword in text:
                    # bbox는 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)] 형태의 4개의 좌표
                    x1, y1 = bbox[0]
                    x2, y2 = bbox[2]

                    # 텍스트 아래 부분에서 offset 만큼 더 아래에서 이미지 잘라내기
                    crop_y = min(int(y2) + self.offset, image.shape[0])
                    cropped_image = image[crop_y:, :]

                    # 저장 경로 설정
                    filename = os.path.basename(image_path)
                    output_path = os.path.join(output_dir, filename)
                    
                    # 잘라낸 이미지 저장
                    cv2.imwrite(output_path, cropped_image)
                    
                    return True
                    
        return False

    def process_images_in_directory(self, directory_path, output_dir):
        for filename in os.listdir(directory_path):
            if filename.endswith(".png"):  # PNG 파일만 처리
                input_image_path = os.path.join(directory_path, filename)
                
                if self.cut_image_below_text(input_image_path, output_dir):
                    print(f"{filename}에서 키워드를 찾았고, 이미지를 잘라냈습니다.")
                else:
                    print(f"{filename}에서 키워드를 찾을 수 없습니다.")