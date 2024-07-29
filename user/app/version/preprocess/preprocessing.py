import os, logging, re, time, sys
import pandas as pd
# from pythonjsonlogger import jsonlogger

# 로깅 설정
log_handler = logging.FileHandler('preprocessing_main.log')
# log_handler.setFormatter(jsonlogger.JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler])

from .img_preprocessing import *
from .text_preprocessing import *
from config import openai
sys.path.append('/app/version')

api_key = openai()

def extract_grade_from_filename(filename):
    match = re.search(r'G(\d)', filename)
    if match:
        groups = match.groups()
        grade = int(groups[0])
        logging.info(f"Extracted grade: {grade} from filename: {filename}")
        return grade
    logging.error(f"Cannot extract grade information from filename: {filename}")
    return None

def process_pdf_images(pdf_directory, output_directory_base):
    grade_info = {}
    print(f"PDF Directory: {pdf_directory}")
    print(f"Output Directory Base: {output_directory_base}")
    for pdf_filename in os.listdir(pdf_directory):
        print(pdf_filename)
        if pdf_filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, pdf_filename)
            grade = extract_grade_from_filename(pdf_filename)
            if grade is None:
                logging.error(f"Cannot extract grade information from filename: {pdf_filename}")
                continue
            output_directory = os.path.join(output_directory_base, os.path.splitext(pdf_filename)[0])
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            grade_info[output_directory] = grade

            # 이미지 파일이 이미 존재하는 경우 처리 건너뛰기
            if any(fname.endswith('.png') for fname in os.listdir(output_directory)):
                logging.info(f"Already exist. Skipping: {output_directory}")
                continue

            logging.info(f"Processing PDF: {pdf_path}")
            converter = PDFConverter_math(pdf_path, output_directory)
            converter.convert_to_images()
            image_directory = output_directory
            processed_output_directory = output_directory
            cropper = Crop_math()
            page_num = 1
            # for filename in os.listdir(image_directory):
            #     if filename.endswith(".png"):
            #         image_path = os.path.join(image_directory, filename)
            #         logging.info(f"Processing image: {image_path}")
            #         reader = easyocr.Reader(['ko'])
            #         results = reader.readtext(image_path)

            image_filenames = sorted([f for f in os.listdir(image_directory) if f.endswith(".png")])
            for filename in image_filenames:
                image_path = os.path.join(image_directory, filename)
                logging.info(f"Processing image: {image_path}")
                reader = easyocr.Reader(['ko'])
                results = reader.readtext(image_path)


                    # keyword = '한국교육과정평가원'
                    # found_keyword = any(re.search(keyword, text) for _, text, _ in results)
                    # if found_keyword:
                    #     processor = ImageProcessorG3_6_9_11_math(image_path, page_num)
                    # else:
                    #     processor = ImageProcessor_math(image_path, page_num)
                    # processor.process_image()


                keyword = '한국교육과정평가원'
                filename_conditions = ['06', '09', '11']

                found_keyword = any(re.search(keyword, text) for _, text, _ in results)
                filename = os.path.basename(os.path.dirname(image_path))  # Assuming image_path contains the filename
                print(f'filename{filename}')

                found_filename_condition = 'G3' in filename and any(cond in filename for cond in filename_conditions)

                if found_keyword or found_filename_condition:
                    processor = ImageProcessorG3_6_9_11_math(image_path, page_num)
                else:
                    processor = ImageProcessor_math(image_path, page_num)
                processor.process_image()

                if processor.left_body is None or processor.right_body is None:
                    logging.error(f"Error processing image: {image_path}")
                    continue
                base_filename = os.path.splitext(filename)[0]
                processor.save_processed_images(processed_output_directory, base_filename)
                cropper.contour(os.path.join(processed_output_directory, f"{base_filename}_left_{page_num:02d}.png"), f"{processed_output_directory}/{os.path.splitext(pdf_filename)[0]}")
                cropper.contour(os.path.join(processed_output_directory, f"{base_filename}_right_{page_num:02d}.png"), f"{processed_output_directory}/{os.path.splitext(pdf_filename)[0]}")
                page_num += 1
            for filename in os.listdir(image_directory):
                if filename.startswith("MATH_page") and filename.endswith(".png"):
                    os.remove(os.path.join(image_directory, filename))
            for filename in os.listdir(processed_output_directory):
                if filename.endswith(".png") and ("_left_" in filename or "_right_" in filename):
                    os.remove(os.path.join(processed_output_directory, filename))
            text_cutter = TextCutter()
            text_cutter.process_images_in_directory(processed_output_directory, processed_output_directory)
            trimmer = ImageTrimmer(processed_output_directory)
            trimmer.process_images()
    logging.info("Image processing for all PDF files completed")
    return output_directory_base, grade_info

def process_basic_info(base_directory_path):
    processor = BasicInfoProcessor(base_directory_path)
    return processor.process_directories()

def process_choices(grade, input_json_data):
    if grade == '1' or grade == '2':
        processor = ProcessorG1G2()
    elif grade == '3':
        processor = ProcessorG3()
    else:
        logging.error("Please enter a valid grade.")
        exit()
    return processor.process_data(input_json_data)

def process_questions(input_json_data):
    question_processor = QuestionProcessor()
    return question_processor.clean_and_process_json_data(input_json_data)

def process_answers(input_data):
    processor = AnswerProcessor()
    return processor.process_all_files(input_data)

def merge_and_save_json_files(df1, df2, df3, df4, output_dir):
    json_merger = JSONMerger(output_dir)
    json_merger.process_dataframes(df1, df2, df3, df4)
    
def preprocess_main():
    start_time = time.time()
    logging.info("Script started")
    base_directory = "/app/temp_pdf"  # 경로 ------------------------------------------------------------
    logging.info(f"Base directory set: {base_directory}")
    pdf_directory = "/app/temp_pdf"  # 경로 ------------------------------------------------------------------------------
    pdf_output_base_dir = "/app/temp_pdf/pdf_images"  # 경로 -------------------------------------------------------------

    if not os.path.exists(pdf_output_base_dir):
        os.makedirs(pdf_output_base_dir)
    logging.info(f"PDF output base directory set: {pdf_output_base_dir}")
    final_pdf_output_dir, grade_info = process_pdf_images(pdf_directory, pdf_output_base_dir)
    print("Grade Info Dictionary:")
    print(grade_info)
    logging.info(f"PDF processing completed. Output directory: {final_pdf_output_dir}")
    logging.info("Starting basic info processing")
    basic_info_result = process_basic_info(final_pdf_output_dir)
    logging.info("Basic info processing completed")
    print("Basic Info Result:")
    print(basic_info_result)
    base_directory_1 = os.path.join(final_pdf_output_dir, "MATH_G3_2024_07_calculus")
    base_directory_2 = os.path.join(pdf_directory, "MATH_G3_2024_07_calculus")
    logging.info("Starting OpenAIImageQuestioner setup")
    questioner_1 = OpenAIImageQuestioner(api_key, base_directory_1)
    questioner_2 = OpenAIImageQuestioner(api_key, base_directory_1)
    questioner_3 = OpenAIImageQuestioner(api_key, base_directory_2)
    logging.info("Starting question extraction")
    questions_1 = [
        "문제만 추출해줘 예시를 보여줄게- **문제:** \\(\\sqrt{20} + \\sqrt{5}\\) 의 값은? [2점]\n- **보기1:** \\(2\\sqrt{5}\\)\n- **보기2:** \\(3\\sqrt{5}\\)\n- **보기3:** \\(4\\sqrt{5}\\)\n- **보기4:** \\(5\\sqrt{5}\\)\n- **보기5:** \\(6\\sqrt{5}\\) 에서 **문제:** \\(\\sqrt{20} + \\sqrt{5}\\) 의 값은? [2점] 이게 문제야 문제를 출력해주고 수학기호는 letex수식 형식으로 출력해줘"
    ]
    questions_2 = [
        "보기만 추출해줘 예시를 보여줄게- **문제:** \\(\\sqrt{20} + \\sqrt{5}\\) 의 값은? [2점]\n- **보기1:** \\(2\\sqrt{5}\\)\n- **보기2:** \\(3\\sqrt{5}\\)\n- **보기3:** \\(4\\sqrt{5}\\)\n- **보기4:** \\(5\\sqrt{5}\\)\n- **보기5:** \\(6\\sqrt{5}\\) 에서  **보기1:** \\(2\\sqrt{5}\\)\n- **보기2:** \\(3\\sqrt{5}\\)\n- **보기3:** \\(4\\sqrt{5}\\)\n- **보기4:** \\(5\\sqrt{5}\\)\n- **보기5:** \\(6\\sqrt{5}\\) 이게 보기야 보기를 출력해주고 수학기호는 letex수식 형식으로 출력해줘"
    ]
    questions_3 = [
         "문제 순서대로 답을 추출해줘 객관식답도 있고 주관식 답도 있어 객관식(1-15번,23-28번)은 객관식답으로 주관식(16-22번,29,30번)은 주관식답으로 파싱해주고  객관식 주관식 상관없이 합쳐서 문제 번호 순서대로 정렬해서 추출해줘"
    ]
    results_1 = []
    for question in questions_1:
        results_1.extend(questioner_1.process_images(question))
    results_2 = []
    for question in questions_2:
        results_2.extend(questioner_2.process_images(question))
    results_3 = []
    for question in questions_3:
        results_3.extend(questioner_3.process_images(question))
    logging.info("Question extraction completed")
    df_choices = pd.DataFrame(results_2)
    df_questions = pd.DataFrame(results_1)
    df_texts = pd.DataFrame(results_3)
    print(df_texts)
    print("df_choices DataFrame:")
    print(df_choices)
    processed_questions = process_questions(df_questions)
    print("Processed Questions:")
    print(processed_questions)
    print("Grade Info Dictionary:")
    print(grade_info)
    processed_choices = None
    for grade, data in grade_info.items():
        print(f"Processing choices for grade {grade} with data {data}")
        processed_choices = process_choices(str(data), df_choices)
        print(f"Processed Choices for Grade {grade}:")
        print(processed_choices)
    processed_answers = process_answers(df_texts)
    print("Processed Answers:")
    print(processed_answers)
    merge_and_save_json_files(processed_questions, basic_info_result, processed_choices, processed_answers, base_directory)
    logging.info("Data merging completed")
    print("Data merging completed")
    end_time = time.time()
    return f"PDF 전처리 완료했습니다.\n걸린시간 : {end_time - start_time}"
    
