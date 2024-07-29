# 빅데이터 7기 최종프로젝트 Quest-Genie 🧞
**❤️‍🔥 천재교육 빅데이터 7기 Quest-Genie🧞(퀘스트 지니) 팀입니다! ❤️‍🔥** 

현재 공교육에서 AI 디지털 교과서 도입이 큰 이슈로 떠오르고 있으며, 교육부는 2024년 관련 예산을 5333억 원 편성했다. AI 교과서는 연 구독료 6만~10만 원으로 예상되며, 조 단위 교과서 시장이 창출될 전망이다. 개별화 및 맞춤형 교육에 대한 기대가 커지고 있으며, 특히 고등학교에서는 킬러 문항 제거로 인해 다양한 문항 풀이가 중요해졌다. 그러나 교사들이 수작업으로 교육 콘텐츠를 제작해야 하는 한계가 있다. 경쟁사 분석 결과, 비상교육의 기출탭탭은 태블릿PC 기반의 수능 기출 학습 앱으로 유사 문항 제공 기능을 갖추고 있으며, 프리윌린의 매쓰플랫은 70만 개의 수학 문제를 제공해 교사 주도의 교육을 지원한다. 자사 분석 결과, 천재교과서의 지니아튜터는 자동채점과 AI유사학습 서비스를 제공하며, 닥터매쓰의 통합문항플랫폼은 맞춤 문항과 유사 문제를 제공한다. 이를 바탕으로 국어, 영어, 수학 교과를 중심으로 유사 문항 추천 서비스를 제공해 고등학생의 개별화 및 맞춤형 교육을 지원하는 것이 필요하다.

## 주요 기능

- ☝️**유사문항 추천**: 프롬프트 엔지니어링을 활용하여 외부문제의 텍스트와 이미지를 활용하여 수능 기출문제와의 유사도를 측정해 유사도가 높은 5개의 문항을 추천해줌.
- ✌️**버전관리**: 매 분기별 새로운 수능, 모평 기출이 새로 출제됨과 동시에 웹사이트 내에서 기출문제의 pdf와 정답지를 업로드 하면 그것을 기반으로 DB에 적재하여 유사문항 추천에 추가됨.


<br>

<br>
<p align="left">
  <img src=https://github.com/user-attachments/assets/4d180855-24b9-4029-9fd6-bb9519d56d9f width = "630px">
  
<p align="left">
  <img src=https://github.com/user-attachments/assets/a7b86868-b76d-4b4e-a3de-0ca915ca21e2 width = "630px">




## **🤍 소개**

<details>
<summary> <b>👨‍👨‍👧‍👦 Team Member</b></summary><br>
  


</br>
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/hanaSummer0701">
        <img src="https://github.com/hanaSummer0701.png" width="150px;" alt="하나"/>
        <br />
        <sub><b>🙋‍♀️장하나</b><br> - 데이터 정량화 및 전처리<br> - 문항시스템 개발 및 테스트<br> - 자동 태깅 모델 개발 및 테스트<br> - AWS S3 생성 및 설정, 관리<br> - 기획서 및 최종 보고서 작성</sub>
</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/choijouneun">
        <img src="https://github.com/choijouneun.png" width="150px;" alt="종은"/>
        <br />
        <sub><b>🙋‍♂️최종은</b><br>- 데이터 수집<br> - 데이터 정량화 및 전처리<br> - 문항시스템 개발 및 테스트<br> - 자동 태깅 모델 개발 및 테스트<br> - 멘토링 활동 보고서 작성<br> - Git 커밋 컨벤션/브렌치 전략<br> - 코드 컨벤션 정의</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/LeeMin-a">
        <img src="https://github.com/LeeMin-a.png" width="150px;" alt="민아"/>
        <br />
        <sub><b>🙋‍♀️이민아</b><br> - 데이터 수집<br> - AWS 서버 생성 및 환경 구축<br> - FastAPI 기본 서버 환경 구축<br> - 도커 웹 서버 빌드<br> - DB와 웹 서버 연결 및 관리<br> - Wire Frame 작성<br> - 노션 관리</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/sunny7319">
        <img src="https://github.com/sunny7319.png" width="150px;" alt="선영"/>
        <br />
        <sub><b>🙋‍♀️민선영</b><br> -데이터 수집<br> - DB 구축 및 관리<br> - 도커컴포즈 작성 및 서버 연결<br> - 파이프라인 설계<br> - ppt 제작<br> - 테이블 정의서 작성</sub>
      </a>
    </td>
  </tr>
</table>
</details>

<details>
<summary> <b>💻 Content</b></summary><br>

</br>

-  **📖 Korean** : 웹사이트에 접속하여 국어를 선택 한 후 사용자가 궁금한 외부문제를 첨부해 시작 버튼을 누르면 해당 문제와 유사한 문항 5개를 선별하여 보여줌. 

- **🔢 Math** : 웹사이트에 접속하여 수학를 선택 한 후 사용자가 궁금한 외부문제를 첨부해 시작 버튼을 누르면 해당 문제와 유사한 문항 5개를 선별하여 보여줌. 
  
- **🔠 English** : 웹사이트에 접속하여 영를 선택 한 후 사용자가 궁금한 외부문제를 첨부해 시작 버튼을 누르면 해당 문제와 유사한 문항 5개를 선별하여 보여줌. 
</details>


<details>
<summary> <b>⚙️ Used Tool/Stack</b></summary><br>

</br>
<p align="left">

<img alt="Python" src ="https://img.shields.io/badge/Python-3776AB.svg?&style=for-the-badge&logo=Python&logoColor=white"/>
<img alt="TensorFlow" src ="https://img.shields.io/badge/TensorFlow-1677FF.svg?&style=for-the-badge&logo=TensorFlow&logoColor=black"/>
<img alt="PyTorch" src ="https://img.shields.io/badge/PyTorch-EE4C2C.svg?&style=for-the-badge&logo=PyTorch&logoColor=white"/>
<img alt="OpenCV" src ="https://img.shields.io/badge/OpenCV-5C3EE8.svg?&style=for-the-badge&logo=OpenCV&logoColor=white"/>
<img alt="numpy" src ="https://img.shields.io/badge/numpy-013243.svg?&style=for-the-badge&logo=numpy&logoColor=white"/>
<img alt="OpenAI" src ="https://img.shields.io/badge/OpenAI-412991.svg?&style=for-the-badge&logo=OpenAI&logoColor=white"/>
<img alt="Anaconda" src ="https://img.shields.io/badge/Anaconda-44A833.svg?&style=for-the-badge&logo=Anaconda&logoColor=black"/>
<img alt="postgresql" src ="https://img.shields.io/badge/postgresql-4169E1.svg?&style=for-the-badge&logo=postgresql&logoColor=white"/>
<img alt="Keras" src ="https://img.shields.io/badge/Keras-D00000.svg?&style=for-the-badge&logo=Keras&logoColor=white"/>
<img alt="FastAPI" src ="https://img.shields.io/badge/FastAPI-009688.svg?&style=for-the-badge&logo=FastAPI&logoColor=white"/>
<img src = "https://img.shields.io/badge/visualstudiocode-007ACC.svg?&style=for-the-badge&logo=visualstudiocode&logoColor=white"/>
<img alt="Github" src = "https://img.shields.io/badge/github-181717.svg?&style=for-the-badge&logo=Github&logoColor=white"/>
<img alt="git" src = "https://img.shields.io/badge/git-F05032.svg?&style=for-the-badge&logo=Git&logoColor=white"/>

</p>
</details>




## **🩶 개발환경 및 실행 방법**

<details>
<summary><b>📄Requirements</b></summary>
  
  <br>
    - pdf2image==1.17.0
  <br>
    - opencv-python==4.9.0.80
  <br>
    - pandas==2.2.2
  <br>
    - numpy==1.26.4
  <br>
    - pillow==10.3.0 
  <br>
    - fastapi==0.111.0 
  <br>
    - easyocr==1.7.1
  <br>
    - pytesseract==0.3.10
  <br>
    - pymupdf 
  <br>
    - glob2==0.7
  <br>
    - pymysql==1.1.1
  <br>
    - uvicorn==0.30.1
  <br>
    - elasticsearch==8.14.0
  <br>
    - keras==3.4.1
  <br>
    - tensorflow==2.17.0
  <br>
    - torch==2.3.1
  <br>
    - torchvision==0.18.1
  <br>
  </details>

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
  
  ### 콘다 가상환경 만들기1 (가상환경 이름: Quest-Genie)
  CMD 창 열고 아래와 같이 입력, 설치 중간에 "y" 입력(엔터), 설치 완료 후 CMD 닫기
  ```cmd
  conda create -n Quest_Genie 
  ```
  다시 CMD 창 열고 아래와 같이 입력 후 완료 시 닫기
  ```cmd
  conda init
  ```

  ### 콘다 가상환경 만들기2 (패키지 설치)
  CMD 창 열고 아래와 같이 입력
  ```cmd
  conda activate Quest_Genie 
  ```
  ```cmd
  pip install -r requirements.txt

  ```

  ### 가상 환경에서 실행 시키기
  git pull, clone 등의 방법으로 main 브랜치 로컬에 저장 후  
  Hands_MediaPipe_project 폴더 들어가서 폴더 상단 주소창에 CMD 입력, CMD 창 띄운 후
  ```cmd
  conda activate Quest_Genie
  ```
  ```cmd
  python main.py
  ```

  #### ⚠️주의 사항⚠️
  - 첫 실행시 자동생성되는 user.json 등 json 파일을 임의 편집하면 오류가 발생할 수 있습니다.
  
  - 버전관리를 실행할 경우 version -> preprocess -> preprocessing.py에서 base_directory_1 = os.path.join(final_pdf_output_dir, "MATH_G3_2024_07_calculus") 이런식으로 파일명으로 경로설정!

  <br>

</details>

## **🖤 콘텐츠 미리보기**
<details>
  <summary><b>📖 Korean</b></summary>
  <p align='left'>
    <img src = "https://github.com/user-attachments/assets/97f2b281-993b-4053-b4f8-0a3ec5d56255" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/21c51771-70d5-465e-9b7e-dcb0a4692fee" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/b474b38a-f51b-41c2-90cd-80c731667e1b" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/ff65e4a5-0173-4a03-8bdb-fe7bf9191973" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/27fb5bd7-175e-4086-a74f-6dd0df34ca6c" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/03cc90fa-6158-4303-bbaa-c4ddb4f12284" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/3f0887de-fd3f-4084-a1be-b85d4260b16b" width="400px"><br>
  </p>
</details>
<br>
<details>
  <summary><b>🔢 Math</b></summary>
  <p align='left'>
    <img src = "https://github.com/user-attachments/assets/435dc7b3-1161-4dc1-b3f2-ee491ca75b9c" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/06950dd2-5f4a-4739-9590-2d299fd9e058" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/69d76b2a-ee8f-45f5-bbc0-12b5748da798" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/5703465d-9699-437b-96d0-68a6789684c2" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/0848ca3c-c32c-4a8c-93a7-1cf561a4e31b" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/0ad5a6dc-8346-4a5b-8a64-d4bf68f8059f" width="400px"><br>
  </p>
</details>
<br>
<details>
  <summary><b>🔠 English</b></summary>
  <p align='left'>
    <img src = "https://github.com/user-attachments/assets/435dc7b3-1161-4dc1-b3f2-ee491ca75b9c" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/06950dd2-5f4a-4739-9590-2d299fd9e058" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/69d76b2a-ee8f-45f5-bbc0-12b5748da798" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/5703465d-9699-437b-96d0-68a6789684c2" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/0848ca3c-c32c-4a8c-93a7-1cf561a4e31b" width="400px"><br>
    <img src = "https://github.com/user-attachments/assets/0ad5a6dc-8346-4a5b-8a64-d4bf68f8059f" width="400px"><br>
  </p>
</details>

- - -
## **📚 참고문헌**
<details>
<summary><b>💡Reference </b></summary>
<br>

- 한국경제) "내년 도입될 AI 디지털 교과서 선점하라"
https://n.news.naver.com/article/015/0004992468?sid=103
- 피앤피뉴스) 킬러문항 없앤 첫 수능...적정 난이도로 변별력 갖췄다
https://www.gosiweek.com/article/1065582631806593
- 내일신문) 비상교육 태블릿PC 전용 수능 학습 앱 ‘기출탭탭’ 활용법
https://www.naeil.com/news/read/455315
- 에듀동아) 프리윌린, ‘2024 인공지능 학습 플랫폼 매칭데이’에서 매쓰플랫과 풀리수학 선보여
http://m.edu.donga.com/news/view.php?at_no=20240223113015145830
- 에듀동아) 프리윌린, 학교 맞춤형 에듀테크 서비스 ‘스쿨플랫’ 오픈…AI 기술로 교실에 ‘초개인화
교육’ ‘학 습 격차 해소’ 지원
http://m.edu.donga.com/news/view.php?at_no=20240516151302535017
- 뉴스핌) 아티피셜소사이어티, 서울특별시교육청에 교육 콘텐츠 AI 솔루션 '젠큐' 공급
https://www.newspim.com/news/view/20240118000068
- 전자신문) 비상교육 '비바샘', AI 기반 수학 문항 자동 생성 서비스
https://n.news.naver.com/article/030/0003078902?sid=102
- QuestionWell 홈페이지 https://www.questionwell.org/
- 천재교과서 지니아튜터, 서울시교육청 주최 에듀테크 교원연수 참가
https://www.it-b.co.kr/news/articleView.html?idxno=76613
- 천재교과서, 최신형 AI 엔진 탑재 수학문제은행 ‘닥터매쓰2.0’ 그랜드 오픈
https://www.it-b.co.kr/news/articleView.html?idxno=69518
- 문제지 header, body영역 분리 참고 블로그 https://kagus2.tistory.com/50 
- 각 문항 컨투어영역 참고 블로그 https://iagreebut.tistory.com/74 
- ssh 연결 오류 해결 참고 블로그 https://lovflag.tistory.com/17 ssh 
- ElasticSearch-FastAPI 연결 참고 자료 https://medium.com/@pritam7798sonawane/building-a-text-search-application-with-elasticsearchand-fastapi-14ea78cf1890
</details>
