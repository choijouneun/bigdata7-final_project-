import os, sys
import subprocess, logging
from pythonjsonlogger import jsonlogger

# 로깅 설정
log_handler = logging.FileHandler('main_log.json')
log_handler.setFormatter(jsonlogger.JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler])

# preprocess 모듈 경로를 시스템 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
# preprocess_path = sys.path.append(os.path.join(current_dir, 'preprocess'))
sys.path.append('..')

from model.embedding import TextSimilarityProcessor

def extract_grade_from_directory(directory):
    if 'G1' in directory:
        return '1'
    elif 'G2' in directory:
        return '2'
    elif 'G3' in directory:
        return '3'
    else:
        return None

def run_pdf2image_process():
    """
    pdf2image_process.py 파일을 실행하고, 최종 이미지가 저장된 경로를 반환합니다.
    """


    logging.info("Checking for existing images in the output directory")
    output_directory = os.path.abspath(r'D:\final_project\test\math_test\MATH_G3_2024_06_calculus')

    # 이미 처리된 이미지가 있는지 확인

    if any(fname.endswith('.png') for fname in os.listdir(output_directory)):
        logging.info("Existing images found. Skipping pdf_main_math.py execution.")
        return output_directory
    


    logging.info("Running pdf2image_process.py")
    result = subprocess.run(["python", "pdf2image_process.py"], capture_output=True, text=True)
    
    # 표준 출력과 표준 오류 출력
    stdout = result.stdout
    stderr = result.stderr
    
    if result.returncode != 0:
        logging.error(f"pdf2image_process.py 실행 중 오류가 발생했습니다.\n{stderr}")
        return None
    
    for line in stdout.split('\n'):
        if "최종 이미지가 저장된 경로" in line:
            return line.split(": ")[1].strip()
    return None


def run_text_process(output_directory):
    """
    text_main.py 파일을 실행하고, 최종 이미지가 저장된 경로를 환경 변수로 전달합니다.
    """
    logging.info(f"Running text_process.py with output directory: {output_directory}")
    grade = extract_grade_from_directory(output_directory)
    if grade:
        os.environ['GRADE'] = grade
    os.environ['PDF_OUTPUT_DIRECTORY'] = output_directory
    subprocess.run(["python", "text_process.py"])

# def run_text_similarity_processor(input_directory, output_directory):
#     """
#     TextSimilarityProcessor를 실행하여 텍스트 유사도 계산 및 결과 저장
#     """
#     logging.info(f"Running TextSimilarityProcessor with input directory: {input_directory} and output directory: {output_directory}")
#     processor = TextSimilarityProcessor(input_directory, output_directory)
#     processor.process_all_files()

def run_text_similarity_processor(input_directory, output_directory):
    """
    TextSimilarityProcessor를 실행하여 텍스트 유사도 계산 및 결과 저장
    """
    logging.info(f"Running TextSimilarityProcessor with input directory: {input_directory} and output directory: {output_directory}")
    processor = TextSimilarityProcessor(input_directory, output_directory)
    
    try:
        processor.process_all_files()
        logging.info("TextSimilarityProcessor 실행 완료")
    except Exception as e:
        logging.error(f"TextSimilarityProcessor 실행 중 오류가 발생했습니다: {str(e)}")


def main():
    # 단계 1: pdf_main_math.py 실행
    pdf_output_directory = run_pdf2image_process()
    
    # # 단계 2: text_main.py 실행
    # if pdf_output_directory:
    #     run_text_process(pdf_output_directory)
    # else:
    #     logging.error("pdf_main_math.py 실행 중 오류가 발생했습니다.")

    # # 단계 3: TextSimilarityProcessor 실행
    # final_output_directory = os.path.join(pdf_output_directory, '결과')
    # embedding_output_directory = os.path.join(final_output_directory, '결과(임베딩)')
    # run_text_similarity_processor(final_output_directory, embedding_output_directory)


     # 단계 2: text_main.py 실행
    logging.info("단계 2: text_process.py 실행")
    run_text_process(pdf_output_directory)

    # # 단계 3: TextSimilarityProcessor 실행
    # final_output_directory = os.path.join(current_dir, '결과')
    # embedding_output_directory = os.path.join(final_output_directory, '결과(임베딩)')
    
    # logging.info("단계 3: TextSimilarityProcessor 실행")
    # run_text_similarity_processor(final_output_directory, embedding_output_directory)

    # 단계 2: text_main.py 실행
    # if pdf_output_directory and run_text_process(pdf_output_directory):
    #     # text_main.py 실행이 완료된 후 TextSimilarityProcessor 실행
    #     final_output_directory = os.path.join(pdf_output_directory, '결과')
    #     embedding_output_directory = os.path.join(final_output_directory, '결과(임베딩)')
    #     run_text_similarity_processor(final_output_directory, embedding_output_directory)
    # else:
    #     logging.error("text_main.py 실행 중 오류가 발생했습니다.")

    # # 단계 2: text_main.py 실행
    # if pdf_output_directory and run_text_process(pdf_output_directory):
    #     # text_main.py 실행이 완료된 후 TextSimilarityProcessor 실행
    #     final_output_directory = os.path.join(pdf_output_directory, '결과')
    #     embedding_output_directory = os.path.join(final_output_directory, '결과(임베딩)')
    #     logging.info(f"Final output directory: {final_output_directory}")
    #     logging.info(f"Embedding output directory: {embedding_output_directory}")

    #     run_text_similarity_processor(final_output_directory, embedding_output_directory)
    # else:
    #     logging.error("text_main.py 실행 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main()
