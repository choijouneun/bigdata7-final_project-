import os, cv2, easyocr, re
from pdf_preprocessing_kor import PDFConverter_kor
from pdf_preprocessing_kor import ImageProcessor_kor
from pdf_preprocessing_kor import NumberDotImageProcessor
from pdf_preprocessing_kor import ImageProcessorG3_6_9_11_kor

# if __name__ == "__main__":
#     pdf_directory = r'C:\Users\BIG3-06\Documents\KDT_Bigdata_7\0614-0726_Final_project\preprocessing\kor_test'
#     output_directory_base = './kor_test/'
#     templates = ['template1.png', 'template2.png', 'template3.png']  # 템플릿 이미지 경로 리스트

#     for pdf_filename in os.listdir(pdf_directory):
#         if pdf_filename.endswith(".pdf"):
#             pdf_path = os.path.join(pdf_directory, pdf_filename)
#             output_directory = os.path.join(output_directory_base, os.path.splitext(pdf_filename)[0])
#             converter = PDFConverter_kor(pdf_path, output_directory)
#             converter.convert_to_images()
#             image_directory = output_directory
#             cropped_output_directory = os.path.join(output_directory, 'cropped')
#             os.makedirs(cropped_output_directory, exist_ok=True)
#             for filename in os.listdir(image_directory):
#                 if filename.endswith(".png"):
#                     image_path = os.path.join(image_directory, filename)
#                     reader = easyocr.Reader(['ko'])
#                     results = reader.readtext(image_path)
#                     keyword = '한국교육과정평가원'
#                     found_keyword = any(re.search(keyword, text) for _, text, _ in results)
#                     if found_keyword:
#                         processor = ImageProcessorG3_6_9_11_kor(image_path)
#                     else:
#                         processor = ImageProcessor_kor(image_path, templates)
#                     processor.process_image()
#                     if processor.left_body is None or processor.right_body is None:
#                         print(f"이미지 처리 중 문제가 발생했습니다: {image_path}")
#                         continue
#                     left_image = processor.left_body
#                     right_image = processor.right_body
#                     base_filename = os.path.splitext(pdf_filename)[0]
#                     output_path_left = os.path.join(cropped_output_directory, f"{base_filename}_left_{filename}")
#                     output_path_right = os.path.join(cropped_output_directory, f"{base_filename}_right_{filename}")
#                     processor.save_processed_images(output_path_left, output_path_right)
#                     image_processor = NumberDotImageProcessor(image_path)
#                     image_processor.process_image()
#                     image_processor.save_processed_image("output_images/MAHT_page0_processed.png")
#     print("모든 PDF 파일에 대한 이미지 처리 완료")




if __name__ == "__main__":
    pdf_directory = r'C:\Users\BIG3-06\Documents\KDT_Bigdata_7\0614-0726_Final_project\preprocessing\kor_test'
    output_directory_base = './kor_test/'

    for pdf_filename in os.listdir(pdf_directory):
        if pdf_filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, pdf_filename)
            output_directory = os.path.join(output_directory_base, os.path.splitext(pdf_filename)[0])

            # PDFConverter 클래스 인스턴스 생성 및 PDF를 이미지로 변환
            converter = PDFConverter_kor(pdf_path, output_directory)
            converter.convert_to_images()

            image_directory = output_directory
            cropped_output_directory = os.path.join(output_directory, 'cropped')
            os.makedirs(cropped_output_directory, exist_ok=True)

            # 주어진 디렉토리에서 모든 PNG 이미지 파일을 읽어 크롭
            for filename in os.listdir(image_directory):
                if filename.endswith(".png"):
                    image_path = os.path.join(image_directory, filename)
                    # processor = ImageProcessor(image_path)
                    # processor.process_image()

                    # easyocr로 텍스트 읽기
                    reader = easyocr.Reader(['ko'])
                    results = reader.readtext(image_path)

                   # 텍스트에서 특정 키워드 검색
                    keyword = '한국교육과정평가원'
                    found_keyword = any(re.search(keyword, text) for _, text, _ in results)

                    # '한국교육과정평가원'이 포함된 경우 ImageProcessorG3_6_9_11 사용
                    if found_keyword:
                        processor = ImageProcessorG3_6_9_11_kor(image_path)
                    else:
                        processor = ImageProcessor_kor(image_path)

                    processor.process_image()

                    # 이미지 처리 후에도 좌측과 우측 body가 None인지 체크
                    if processor.left_body is None or processor.right_body is None:
                        print(f"이미지 처리 중 문제가 발생했습니다: {image_path}")
                        continue

                    left_image = processor.left_body
                    right_image = processor.right_body

                    base_filename = os.path.splitext(pdf_filename)[0]
                    output_path_left = os.path.join(cropped_output_directory, f"{base_filename}_left_{filename}")
                    output_path_right = os.path.join(cropped_output_directory, f"{base_filename}_right_{filename}")
                    processor.save_processed_images(output_path_left, output_path_right)

                    cropper = Crop_kor()
                    cropper.contour(left_image, os.path.join(cropped_output_directory, f"{base_filename}_left_{filename}"))
                    cropper.contour(right_image, os.path.join(cropped_output_directory, f"{base_filename}_right_{filename}"))

    print("모든 PDF 파일에 대한 이미지 처리 완료")
