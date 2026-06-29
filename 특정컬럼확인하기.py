
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

print(top_keywords, type(top_keywords))

# 5. 콘솔에 결과 출력
print("📊 [새해 첫날] 가장 많이 언급된 핵심 키워드 Top 30")
print(f"{'순위':<5} | {'키워드':<15} | {'언급 빈도':<10}")
print("-" * 50)

# enumerate(반복가능한객체, 시작할_숫자)
# 튜플(Tuple)들이 담긴 리스트 top_keywords
for rank, (word, count) in enumerate(top_keywords, 1):
    print(f"{rank:<5} | {word:<15} | {count:<10}")