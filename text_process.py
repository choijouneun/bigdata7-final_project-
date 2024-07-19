import sys
import os, logging
from pythonjsonlogger import jsonlogger

# 로깅 설정
log_handler = logging.FileHandler('text_process_log.json')
log_handler.setFormatter(jsonlogger.JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler])

# preprocess 및 model 경로를 시스템 경로에 추가
sys.path.append('..')

# 필요한 모듈 임포트
from preprocess.math_text_preprocessing import OpenAIImageQuestioner
from preprocess.question_preprocessing import QuestionProcessor
from preprocess.choice_preprocessing import ProcessorG1G2, ProcessorG3
from preprocess.basic_info import BasicInfoProcessor
from preprocess.answer_parsing import AnswerProcessor
from preprocess.merge_json import JSONMerger

# 기본 정보 처리 함수
def process_basic_info(base_directory_path, save_directory_path):
    processor = BasicInfoProcessor(base_directory_path, save_directory_path)
    processor.process_directories()


def extract_grade_from_directory(directory):
    if 'G1' in directory:
        return '1'
    elif 'G2' in directory:
        return '2'
    elif 'G3' in directory:
        return '3'
    else:
        return None

def process_choices(pdf_output_directory, output_json_directory):
    """
    최종 이미지 저장 경로에서 학년 정보를 추출하여 선택지를 처리합니다.
    """
    grade = os.getenv('GRADE')  # 환경 변수에서 학년 정보 가져오기

    logging.info(f"Extracted grade: {grade}")  # 학년 정보 로그 출력
    
    if not grade:
        print("유효한 학년을 추출할 수 없습니다.")
        logging.error("유효한 학년을 추출할 수 없습니다.")
        exit()
    
    if grade == '1' or grade == '2':
        processor = ProcessorG1G2(pdf_output_directory, output_json_directory)
        logging.info("Using ProcessorG1G2")  # G1, G2 프로세서 사용 로그 출력
    elif grade == '3':
        processor = ProcessorG3(pdf_output_directory, output_json_directory)
        logging.info("Using ProcessorG3")  # G3 프로세서 사용 로그 출력
    else:
        print("유효한 학년을 입력하세요.")
        logging.error("유효한 학년을 입력하세요.")
        exit()
    processor.process_json_files()

# 질문 처리 함수
def process_questions(input_question_directory, output_question_directory):
    question_processor = QuestionProcessor(input_question_directory, output_question_directory)
    question_processor.clean_and_save_json_files()

# 정답 처리 함수
def process_answers(input_directory, output_directory):
    processor = AnswerProcessor(input_directory, output_directory)
    processor.process_all_files()

# JSON 파일 병합 함수
def merge_json_files(input_dir_1, input_dir_2, input_dir_3, input_dir_4, output_dir):
    json_merger = JSONMerger(input_dir_1, input_dir_2, input_dir_3, input_dir_4, output_dir)
    json_merger.process_files()

# 텍스트 임베딩 처리 함수
def process_embeddings(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

# 새로운 함수로 정답 디렉토리 생성
def new_func(current_dir):
    output_directory = os.path.join(current_dir, '정답')
    return output_directory

if __name__ == "__main__":

    # main.py에서 전달받은 경로 사용
    pdf_output_directory = os.getenv('PDF_OUTPUT_DIRECTORY')

    # 현재 작업 디렉토리 설정
    # main.py에서 전달받은 경로 사용
    current_dir = os.path.abspath(r'D:\final_project\test') # 현재 작업 디렉토리
    # pdf_output_directory = os.getenv('PDF_OUTPUT_DIRECTORY', os.path.join(current_dir))

    # 기본 정보를 처리할 디렉토리 경로 설정
    base_directory_path = os.path.join(current_dir, 'math_test')
    save_directory_path = os.path.join(current_dir,'basic_info')

    # 기본 정보 처리
    process_basic_info(base_directory_path, save_directory_path)

    # OpenAI API 키 설정
    api_key = "sk-proj-3JUo4EwKOKPcoterMJVST3BlbkFJlrgUmwrvlEKN9Nlv3uik"

    # 디렉토리 경로 설정
    base_directory_1 = pdf_output_directory  # 최종 이미지 저장 경로
    # base_directory_1 = os.path.join(pdf_output_directory, 'MATH_G3_2024_06_calculus') # 다른 폴더 생성 경로
    base_directory_2 = os.path.join(current_dir, 'MATH_G3_2024_06_calculus') # 답안 이미지 저장졍로
    output_base_directory_1 = os.path.join(current_dir, '문제')
    output_base_directory_2 = os.path.join(current_dir, '보기')
    output_base_directory_3 = os.path.join(current_dir, '정답(프롬)')

    # OpenAIImageQuestioner 클래스 인스턴스 생성
    questioner_1 = OpenAIImageQuestioner(api_key, base_directory_1, output_base_directory_1)
    questioner_2 = OpenAIImageQuestioner(api_key, base_directory_1, output_base_directory_2)
    questioner_3 = OpenAIImageQuestioner(api_key, base_directory_2, output_base_directory_3)

    # 질문 설정
    questions_1 = [
        "문제만 추출해줘 예시를 보여줄게- **문제:** \\(\\sqrt{20} + \\sqrt{5}\\) 의 값은? [2점]\n- **보기1:** \\(2\\sqrt{5}\\)\n- **보기2:** \\(3\\sqrt{5}\\)\n- **보기3:** \\(4\\sqrt{5}\\)\n- **보기4:** \\(5\\sqrt{5}\\)\n- **보기5:** \\(6\\sqrt{5}\\) 에서 **문제:** \\(\\sqrt{20} + \\sqrt{5}\\) 의 값은? [2점] 이게 문제야 문제를 출력해주고 수학기호는 letex수식 형식으로 출력해줘"
    ]

    questions_2 = [
        "보기만 추출해줘 예시를 보여줄게- **문제:** \\(\\sqrt{20} + \\sqrt{5}\\) 의 값은? [2점]\n- **보기1:** \\(2\\sqrt{5}\\)\n- **보기2:** \\(3\\sqrt{5}\\)\n- **보기3:** \\(4\\sqrt{5}\\)\n- **보기4:** \\(5\\sqrt{5}\\)\n- **보기5:** \\(6\\sqrt{5}\\) 에서  **보기1:** \\(2\\sqrt{5}\\)\n- **보기2:** \\(3\\sqrt{5}\\)\n- **보기3:** \\(4\\sqrt{5}\\)\n- **보기4:** \\(5\\sqrt{5}\\)\n- **보기5:** \\(6\\sqrt{5}\\) 이게 보기야 보기를 출력해주고 수학기호는 letex수식 형식으로 출력해줘"
    ]

    questions_3 = [
         "문제 순서대로 답을 추출해줘 객관식답도 있고 주관식 답도 있어 객관식(1-15번,23-28번)은 객관식답으로 주관식(16-22번,29,30번)은 주관식답으로 파싱해주고  객관식 주관식 상관없이 합쳐서 문제 번호 순서대로 정렬해서 추출해줘"
    ]

    # 이미지 처리 및 질문 추출
    for question in questions_1:
        questioner_1.process_images(question)

    for question in questions_2:
        questioner_2.process_images(question)
        
    for question in questions_3:
        questioner_3.process_images(question)

    # 학년을 입력받아 선택지 처리
    # grade = input("학년을 입력하세요 (1, 2, 3): ")
    input_json_directory = os.path.join(current_dir, '보기')
    output_json_directory = os.path.join(current_dir, '보기전처리')
    process_choices(input_json_directory, output_json_directory)

    # 정답 처리
    input_directory = os.path.join(current_dir, '정답(프롬)')
    output_directory = new_func(current_dir)
    process_answers(input_directory, output_directory)

    # 질문 처리
    input_question_directory = os.path.join(current_dir, '문제')
    output_question_directory = os.path.join(current_dir, '문제전처리')
    process_questions(input_question_directory, output_question_directory)

    # JSON 파일 병합
    final_output_directory = os.path.join(current_dir, '결과')
    merge_json_files(output_question_directory, output_json_directory, save_directory_path, output_directory, final_output_directory)
    
    # # # 임베딩 처리
    embedding_output_directory = os.path.join(current_dir, '결과(임베딩)')
    process_embeddings(final_output_directory, embedding_output_directory)
    