import os, cv2, easyocr
from pdf_preprocessing2 import PDFConverter
from pdf_preprocessing2 import ImageProcessor
from pdf_preprocessing2 import Crop

if __name__ == "__main__":
    pdf_directory = r'C:\Users\BIG3-06\Documents\KDT_Bigdata_7\0614-0726_Final_project\preprocessing\test'
    output_directory_base = './test/'

    # reader = easyocr.Reader(['en'])

    for pdf_filename in os.listdir(pdf_directory):
        if pdf_filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, pdf_filename)
            output_directory = os.path.join(output_directory_base, os.path.splitext(pdf_filename)[0])

            # PDFConverter 클래스 인스턴스 생성 및 PDF를 이미지로 변환
            converter = PDFConverter(pdf_path, output_directory)
            converter.convert_to_images()

            image_directory = output_directory
            cropped_output_directory = os.path.join(output_directory, 'cropped')
            os.makedirs(cropped_output_directory, exist_ok=True)

            # 주어진 디렉토리에서 모든 PNG 이미지 파일을 읽어 크롭
            for filename in os.listdir(image_directory):
                if filename.endswith(".png"):
                    image_path = os.path.join(image_directory, filename)
                    processor = ImageProcessor(image_path)
                    processor.process_image()

                    left_image = processor.left_body
                    right_image = processor.right_body

                    base_filename = os.path.splitext(pdf_filename)[0]
                    output_path_left = os.path.join(cropped_output_directory, f"{base_filename}_left_{filename}")
                    output_path_right = os.path.join(cropped_output_directory, f"{base_filename}_right_{filename}")
                    processor.save_processed_images(output_path_left, output_path_right)

                    cropper = Crop()
                    cropper.contour(left_image, os.path.join(cropped_output_directory, f"{base_filename}_left_{filename}"))
                    cropper.contour(right_image, os.path.join(cropped_output_directory, f"{base_filename}_right_{filename}"))

    print("모든 PDF 파일에 대한 이미지 처리 완료")


