import os
import json

class BasicInfoProcessor:
    def __init__(self, base_directory_path, save_directory_path):
        self.base_directory_path = base_directory_path
        self.save_directory_path = save_directory_path
        self.create_save_directory(self.save_directory_path)

    def create_save_directory(self, path):
        # 저장 디렉토리가 존재하지 않으면 생성
        os.makedirs(path, exist_ok=True)

    def parse_filename(self, filename):
        parts = filename.split('_')
        if len(parts) < 4:
            return None
        elif len(parts) < 6:
            yyyy = parts[2]
            grade = parts[1]
            mm = parts[3]
            mm = int(mm)
            subject = parts[0]
        else:
            yyyy = parts[2]
            grade = parts[1]
            mm = parts[3]
            mm = int(mm)
            subject = parts[4]
            
        if 'G3' in grade:
            grade = 3
        elif 'G2' in grade:
            grade = 2
        elif 'G1' in grade:
            grade = 1
        else:
            grade = grade.upper()
        
        if 'A' in subject:
            subject = 2
        elif 'B' in subject:
            subject = 3
        elif 'geometry' in subject:
            subject = 6
        elif 'calculus' in subject:
            subject = 5
        elif 'statistics' in subject:
            subject = 4
        elif 'MATH' in subject:
            subject = 1
        else:
            subject = subject.upper()
            
        if mm in [6, 9]:
            a = 1
        elif mm == 11:
            a = 0
        else:
            a = 2      
        
        return {'yyyy': int(yyyy), 'grade': grade, 'mm': mm, 'subject_cat': subject ,'host' : a ,'text_exp': "",'question_exp':"","text_title":"","text_yn":0,"paragraph": ""}

    def process_directories(self):
        # 모든 서브디렉토리를 순회하며 JSON 파일 생성
        for root, dirs, files in os.walk(self.base_directory_path):
            for dir_name in dirs:
                directory_path = os.path.join(root, dir_name)
                
                json_data = []
                file_count = 0
                
                # 디렉토리 내 파일을 검색하고 정보 추출
                for sub_root, sub_dirs, sub_files in os.walk(directory_path):
                    for file in sub_files:
                        if file.endswith(".jpg") or file.endswith(".png"):  # 이미지 파일 확장자에 따라 필터링
                            file_info = self.parse_filename(file)
                            if file_info:
                                file_count += 1
                                file_info['question_num'] = file_count
                                json_data.append(file_info)
                
                # JSON 파일로 저장
                output_file = os.path.join(self.save_directory_path, f"{dir_name}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)
                
                print(f"총 {file_count}개의 파일이 {directory_path}에서 처리되었습니다.")
                print(f"JSON 데이터는 {output_file} 파일로 저장되었습니다.")
