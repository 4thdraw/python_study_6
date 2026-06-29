import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib import font_manager, rc
import platform


import pandas as pd
from collections import Counter

file_path = './원본/한국언론진흥재단_뉴스빅데이터_메타데이터_노인_20011231.csv'  # 파일명을 여기에 적어주세요.


df = pd.read_csv(file_path, encoding='cp949')

df['일자'] = df['일자'].astype(str)
df_new_year = df[df['일자'].str.endswith('01-01') | df['일자'].str.endswith('0101')]

print(f"✨ 새해 첫날 데이터 총 개수: {len(df_new_year)}건")
print("-" * 50)

# 3. '키워드' 컬럼에서 단어 추출 및 빈도 계산
all_keywords = []

# 결측치(NaN) 제거 후 처리
keywords_series = df_new_year['키워드'].dropna()

for keywords in keywords_series:
    # 큰따옴표 제거 및 쉼표 기준으로 단어 분리
    cleaned_keywords = keywords.replace('"', '').split(',')
    # 공백 제거 후 리스트에 추가 (빈 문자열 제외)
    all_keywords.extend([kw.strip() for kw in cleaned_keywords if kw.strip()])

# 4. 단어 빈도수 계산 (상위 30개)
# 키, 값으로 묶어줌
keyword_counts = Counter(all_keywords)
top_keywords = keyword_counts.most_common(30)

# 1. 한글 폰트 깨짐 방지를 위한 시스템별 폰트 경로 설정
# 시스템 환경(Windows / Mac / Linux)에 따라 자동으로 폰트를 지정합니다.
os_name = platform.system()
if os_name == 'Windows':
    font_path = r'C:\Windows\Fonts\NanumGothic.ttf'  # 맑은 고딕
elif os_name == 'Darwin':  # Mac
    font_path = '/Library/Fonts/Arial Unicode.ttf'
else:  # Linux (Colab 등)
    font_path = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'


# === [★ 핵심: 이 부분을 추가하여 Matplotlib 전역 폰트 설정] ===
# 폰트 파일명으로 폰트 이름을 가져옵니다.
font_name = font_manager.FontProperties(fname=font_path).get_name()
# Matplotlib의 기본 폰트로 설정합니다.
rc('font', family=font_name)
# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False
# 2. 워드 클라우드 객체 생성 및 빈도수 데이터 주입
# keyword_counts는 앞서 만든 Counter({'단어': 빈도수}) 객체입니다.
wordcloud = WordCloud(
    font_path=font_path,          # 한글 폰트 지정
    width=800,                    # 이미지 가로 크기
    height=800,                   # 이미지 세로 크기
    background_color='white',     # 배경 색상
    max_words=100,                # 최대 시각화할 단어 수
    colormap='viridis'            # 글자 색상 테마 (Plasma, Inferno, Cool 등 변경 가능)
).generate_from_frequencies(keyword_counts)

# 3. Matplotlib를 사용하여 화면에 그래프 그리기
plt.figure(figsize=(10, 10))       # 그래프 창 크기 설정
plt.imshow(wordcloud, interpolation='bilinear') # 이미지를 부드럽게 출력
plt.axis('off')                   # 격자 및 축 눈금 숨기기
plt.title("📊 새해 첫날 핵심 키워드 워드클라우드", fontsize=20, pad=20)

# 4. 시각화 결과 보여주기
plt.show()