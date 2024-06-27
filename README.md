# bigdata7-final_project
빅데이터 7기 3조 최종 프로젝트
<details>
<summary><b>🏃 How-to-Run</b></summary>

  ### 가상환경 설정을 위한 콘다 설치
  미니콘다(혹은 아나콘다) 설치
  링크: https://docs.anaconda.com/free/miniconda/
  설치 시 Just me 선택

  ### 윈도우 시스템 환경변수 편집
  > WIN 키 -> "시스템 환경 변수 편집" 검색 -> 시스템 속성 창 하단 "환경 변수(N)"
  > -> 하단 시스템 변수(S) 중 "Path" 더블클릭 -> 새로만들기
  > -> "C:\Users\USER\miniconda3\Scripts" & "C:\Users\USER\miniconda3\Library\bin"
  > 입력 후 모든 창 "확인" 눌러 닫기
  
  ### 콘다 가상환경 만들기1 (가상환경 이름: myenv)
  CMD 창 열고 아래와 같이 입력, 설치 중간에 "y" 입력(엔터), 설치 완료 후 CMD 닫기
  ```cmd
  conda create --name myenv python=3.12.3
  ```
  Conda 가상환경 활성화
  ```cmd
  conda activate myenv
  ```

  ### 콘다 가상환경 만들기2 (나머지 패키지 설치)
  CMD 창 열고 아래와 같이 입력
  ```cmd
  pip install pdf2image==1.17.0 opencv-python==4.9.0.80 numpy==1.26.4 pillow==10.3.0 fastapi==0.111.0 easyocr==1.7.1 pytesseract==0.3.10 pymupdf glob2==0.7 pymysql==1.1.1
  ```

  <br>

</details>
