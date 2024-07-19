import os
import cv2, sys
import easyocr
import re
import logging
from pythonjsonlogger import jsonlogger
# from preprocess.pdf_preprocessing_math import PDFConverter_math, ImageProcessor_math, Crop_math, ImageProcessorG3_6_9_11_math, ImageTrimmer, TextCutter

# 로깅 설정
log_handler = logging.FileHandler('pdf2image_process.json')
log_handler.setFormatter(jsonlogger.JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler])

# preprocess 모듈 경로를 시스템 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
# preprocess_path = sys.path.append(os.path.join(current_dir, 'preprocess'))
sys.path.append('..')

from preprocess.pdf_preprocessing_math import PDFConverter_math, ImageProcessor_math, Crop_math, ImageProcessorG3_6_9_11_math, ImageTrimmer, TextCutter


def process_pdf_images(pdf_directory, output_directory_base):
    for pdf_filename in os.listdir(pdf_directory):
        if pdf_filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, pdf_filename)
            output_directory = os.path.join(output_directory_base, os.path.splitext(pdf_filename)[0])

            logging.info(f"Processing PDF: {pdf_path}")
            # PDFConverter 클래스 인스턴스 생성 및 PDF를 이미지로 변환
            converter = PDFConverter_math(pdf_path, output_directory)
            converter.convert_to_images()

            image_directory = output_directory
            processed_output_directory = output_directory  # 원본 PDF 폴더에 저장
            # processed_output_directory = os.path.join(output_directory, 'cropped')
            # os.makedirs(processed_output_directory, exist_ok=True)

            cropper = Crop_math()
            page_num = 1

            # 주어진 디렉토리에서 모든 PNG 이미지 파일을 읽어 좌우 크롭 후 크롭 실행
            for filename in os.listdir(image_directory):
                if filename.endswith(".png"):
                    image_path = os.path.join(image_directory, filename)
                    logging.info(f"Processing image: {image_path}")

                    # easyocr로 텍스트 읽기
                    reader = easyocr.Reader(['ko'])
                    results = reader.readtext(image_path)

                    # 텍스트에서 특정 키워드 검색
                    keyword = '한국교육과정평가원'
                    found_keyword = any(re.search(keyword, text) for _, text, _ in results)

                    # '한국교육과정평가원'이 포함된 경우 ImageProcessorG3_6_9_11 사용
                    if found_keyword:
                        processor = ImageProcessorG3_6_9_11_math(image_path, page_num)
                    else:
                        processor = ImageProcessor_math(image_path, page_num)

                    processor.process_image()

                    # 이미지 처리 후에도 좌측과 우측 body가 None인지 체크
                    if processor.left_body is None or processor.right_body is None:
                        logging.error(f"이미지 처리 중 문제가 발생했습니다: {image_path}")
                        continue

                    base_filename = os.path.splitext(filename)[0]
                    processor.save_processed_images(processed_output_directory, base_filename)

                    # 좌측 이미지 크롭 및 저장
                    cropper.contour(os.path.join(processed_output_directory, f"{base_filename}_left_{page_num:02d}.png"), f"{processed_output_directory}/{os.path.splitext(pdf_filename)[0]}")

                    # 우측 이미지 크롭 및 저장
                    cropper.contour(os.path.join(processed_output_directory, f"{base_filename}_right_{page_num:02d}.png"), f"{processed_output_directory}/{os.path.splitext(pdf_filename)[0]}")

                    page_num += 1

            # PDFConverter_math 및 ImageProcessor_math로 생성된 이미지 삭제
            for filename in os.listdir(image_directory):
                if filename.startswith("MAHT_page") and filename.endswith(".png"):
                    os.remove(os.path.join(image_directory, filename))

            for filename in os.listdir(processed_output_directory):
                if filename.endswith(".png") and ("_left_" in filename or "_right_" in filename):
                    os.remove(os.path.join(processed_output_directory, filename))

            # 불필요한 단어 자르기 실행
            text_cutter = TextCutter()
            text_cutter.process_images_in_directory(processed_output_directory, processed_output_directory)

            # 여백 자르기 실행
            trimmer = ImageTrimmer(processed_output_directory)
            trimmer.process_images()
            
    logging.info("모든 PDF 파일에 대한 이미지 처리 완료")
    return output_directory_base

if __name__ == "__main__":
    pdf_directory = r'D:\final_project\test'
    output_directory_base = r'D:\final_project\test\math_test'

    final_output_directory = process_pdf_images(pdf_directory, output_directory_base)
    print(f"최종 이미지가 저장된 경로: {final_output_directory}")

    # # 학년 정보를 추출하여 출력
    # grade = extract_grade_from_directory(os.path.basename(final_output_directory))
    # print(f"학년 정보: {grade}")