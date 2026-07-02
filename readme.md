# 🚀 아나콘다 기반 파이썬 시각화 프로젝트 GitLab 배포 가이드

로컬 PC(Anaconda)에서 개발한 파이썬 데이터 시각화 프로젝트를 **GitLab Pages**를 통해 웹에 자동으로 배포하는 가이드입니다. 

이 프로젝트는 코드를 푸시할 때마다 GitLab CI/CD가 원격 서버(Python 3.11 환경)에서 코드를 대신 실행하고, 생성된 HTML 시각화 파일을 무료 웹 호스팅 공간에 자동으로 빌드 및 배포합니다.

---

## 🛠️ 1. 배포를 위한 3단계 세팅

### 1단계: 아나콘다 환경 라이브러리 목록 추출 (`requirements.txt`)
GitLab 서버에게 로컬 가상환경과 동일한 패키지를 설치하도록 안내하는 설정 파일을 생성합니다.

1. **Anaconda Prompt(또는 사용 중인 터미널)**를 실행합니다.
2. 현재 프로젝트의 가상환경을 활성화(`conda activate 환경이름`)합니다.
3. 프로젝트 루트 디렉터리로 이동 후 아래 명령어를 입력합니다.

```bash
pip freeze > requirements.txt
```


### 2단계: 파이썬 실행 결과물을 index.html로 저장하도록 수정

시각화 라이브러리(Plotly, Folium, Bokeh 등)의 최종 출력 파일명이 반드시 index.html로 저장되도록 파이썬 스크립트(main.py)의 마지막 코드를 수정합니다.

Plotly 예시:

Python
fig.write_html("index.html")
Folium 예시:

Python
map.save("index.html")

### 3단계: GitLab 자동화 명세서 생성 (.gitlab-ci.yml)

프로젝트 루트 폴더에 .gitlab-ci.yml 파일을 새로 만들고 아래 내용을 그대로 붙여넣습니다. (파일명 맨 앞의 마침표.에 주의하세요.)

```YAML
# 1. GitLab 주자(Runner)에게 파이썬 3.11 환경을 준비하도록 지정
image: python:3.11-slim

pages:
  stage: deploy
  script:
    # 2. 로컬과 동일한 라이브러리 자동 설치
    - pip install -r requirements.txt
    
    # 3. 파이썬 시각화 스크립트 실행 (본인의 파일명으로 변경 가능)
    - python main.py
    
    # 4. GitLab Pages 규칙에 맞게 public 폴더 생성 후 index.html 이동
    - mkdir public
    - mv index.html public/
    
  artifacts:
    paths:
      - public
  only:
    - main  # main 브랜치에 코드가 push될 때만 자동 배포 파이프라인 작동
```

## 🛠️ 2. GitLab 저장소에 반영 (Push)

터미널 또는 코드 에디터(Cursor, VS Code 등)의 내장 터미널을 열고 아래 명령어를 순서대로 입력하여 원격 저장소에 코드를 올립니다.

```bash
# 변경된 모든 파일 스테이징
git add .

# 커밋 메시지 작성
git commit -m "feat: 시각화 파이썬 스크립트 및 GitLab CI/CD 설정 추가"


# 원격 저장소의 main 브랜치로 푸시
git push origin main
```

## 👀 3. 배포 결과 확인하기

GitLab 프로젝트 페이지에 접속합니다.

왼쪽 사이드바 메뉴에서 Build > Pipelines로 이동합니다.

현재 올린 커밋 항목 옆에 Running 표시가 뜨며 GitLab이 파이썬을 돌리는 모습을 확인할 수 있습니다.

잠시 후 초록색 체크 아이콘(Passed)으로 바뀌면 성공입니다.

왼쪽 사이드바 메뉴에서 Deploy > Pages로 이동하면 생성된 무료 웹 호스팅 URL 주소를 확인할 수 있습니다. 해당 주소로 접속하면 배포된 시각화 화면이 나타납니다.

## 💡 핵심 체크포인트
아나콘다 가상환경 폴더 전체를 Git에 올리는 것이 아닙니다!
오직 파이썬 소스 코드(.py), 패키지 목록(requirements.txt), 배포 명세서(.gitlab-ci.yml) 파일만 가볍게 공유하면 배포 과정은 GitLab이 알아서 처리합니다.