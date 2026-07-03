# [상세지역, 키워드] 쌍으로 완전히 쪼개어 빈도수를 계산하는 시각화

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from collections import Counter

file_path = './원본/한국언론진흥재단_뉴스빅데이터_메타데이터_노인_20011231.csv' 
df = pd.read_csv(file_path, encoding='cp949')

plt.rcParams["font.family"] = "Malgun Gothic"  
plt.rcParams["axes.unicode_minus"] = False  

base_stop_words = {'노인', '참석', '일동', '주민', 
                   "지역", "마을", "노인들", "노인분들", "주민들","주민일동",
                   "이날" }

region_mask = df["통합 분류1"].notna() & df["통합 분류1"].str.contains("지역")

#################### 지역기사만 추출한 데이터프레임 ##########################

df_region = df[region_mask].copy() 

df_region['상세지역'] = df_region['통합 분류1'].apply(
    lambda x: x.split('-')[-1].strip() if '-' in str(x) else x.strip()
)

######## 정보량 0인 키워드 추출 준비 & 지역이름 만 수집하기 ########
# 판다스에서 데이터프레임의 특정 열을 수정할 때 가장 많이 쓰는 핵심 패턴
# 서로 다른 메모리 주소를 가진 별개의 객체
# 오른쪽은 시리즈이고 같은 이름이더라도 새로운 공간에 저장해서 가공
# 왼쪽은 데이터프레임의 열을 가리키는 참조(Reference) 객체 
df_region['키워드'] = df_region['키워드'].fillna('')
# 빈문자열이라도 삽입
all_region_names = list(df_region['상세지역'].dropna().unique())



def get_top_10_keywords(series):   
    all_text = " ".join(series.astype(str))
    #모두 빈칸을 두고 하나의 문자열로 결합 
    # (그렇다면 그전에 데이터들이 문자가 아니면 합해지지 못하므로 astype(str)로 변환) 
    #  결과물 예시 : "100, True, 사과"  
    words = [word.strip() for word in all_text.replace(',', ' ').split() if word.strip()]

        # 1. all_text.replace(',', ' ') 
        # -> 쉼표(,)를 모두 공백(' ')으로 바꿉니다. 
        # -> 예: "100, True, 사과" 였던 것이 "100   True   사과"처럼 공백이 여러 개 생길 수 있습니다.

        # 2. all_text.replace(',', ' ').split() 
        # -> 파이썬의 .split()은 괄호 안에 아무것도 안 넣으면 '연속된 모든 공백'을 하나로 취급해 잘라줍니다!
        # -> ❗ 중요: 빈 문자열([' ', ' '])이 생기지 않고, 깔끔하게 ['100', 'True', '사과']로 쪼개집니다.

        # 3. if word.strip()
        # -> 혹시라도 split 결과에 공백만 있는 문자열이 들어왔을 때를 대비한 안전장치(필터링)입니다.
        # -> 빈 문자열('')은 파이썬에서 False로 취급되므로 리스트에서 제외됩니다.

        # 4. word.strip()
        # -> ['100', 'True', '사과']에서 추출된 각 단어 좌우에 혹시 남아있을지 모를 미세한 공백을 완전히 제거합니다.
    
    top_10 = [item[0] for item in Counter(words).most_common(5)]
        # Counter(words) { '100': 1, 'True': 1, '사과': 1 } -> 빈도수가 높은 것부터 나열함 (저절로 내림차순이 일어남)
        # item '100': 1 item[0]이 키, item[1]이 빈도수입니다.
    return top_10 # 빈도수가 높은 키워드 순 5개만 내보내라

def get_clean_keywords(text):
    if not text: return [] # 문자열을 받았을때 비어있을 경우 빈리스트 반환 비어있는데 아래 작업을 진행할 이유가 없으니깐
    words = [word.strip() for word in str(text).replace(',', ' ').split() if word.strip()]    
    clean_words = []
    for word in words:
        #대조작업시작
        if word in base_stop_words: continue
        if any(region in word for region in all_region_names): continue
        #2개의 if문을 통과한 단어만 clean_words에 추가
        clean_words.append(word)
    return clean_words # 정제후 모여진 키워드

def merge_and_rank(series):
    merged_list = [word for sublist in series for word in sublist]
    return [item[0] for item in Counter(merged_list).most_common(10)]


df_region['정제된_리스트'] = df_region['키워드'].apply(get_clean_keywords)
# 키워드 한 행 마다 들어있던 노인, 무료, 시식, 참여, 지역... 이렇게 길게 되어있는 문자열을 5개로 줄여서 
# 다시 원래 데이터프레임의 새로운 컬럼 정제된_리스트라는 컬럼에 넣어주기
# apply(get_clean_keywords)로 각 행마다 함수를 적용



visual_df = df_region.groupby('상세지역').agg(
    뉴스건수=('상세지역', 'count'),
    키워드순=('정제된_리스트', merge_and_rank)
).sort_values(by='뉴스건수', ascending=False) # 뉴스 건수 많은 순 정렬

# 상세지역별로 뉴스 건수와 키워드순 컬럼  집계한 데이터프레임을 생성하고, 뉴스 건수 기준으로 내림차순 정렬


visual_df['상위3개키워드'] = visual_df['키워드순'].apply(lambda x: ', '.join(x[:3]))
# 상위3개키워드 컬럼 추가하고 키워드순 리스트로 값이 되어있는데 하나의 문자열로 쉽표가 포함된 3자리까지 합쳐서 넣어주기 (join)

plt.figure(figsize=(14, 7))


ax = sns.barplot(
    data=visual_df.reset_index(), 
    x='상세지역', 
    y='뉴스건수', 
    hue='상위3개키워드', 
    dodge=False,       # 지역별로 하나의 막대만 깔끔하게 노출되도록 설정
    palette='viridis'   # 직관적이고 세련된 컬러 맵 적용
)

# 5. 그래프 세부 디자인 및 레이블 설정
plt.title('지역 뉴스에 나타난 핵심 지역 분포 및 Top 3 키워드', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('상세 지역 (대분류 > 소분류 정제)', fontsize=12, labelpad=10)
plt.ylabel('뉴스 빈도수 (건)', fontsize=12, labelpad=10)
plt.xticks(rotation=45) # 지역명이 겹치지 않도록 45도 회전
plt.grid(axis='y', linestyle='--', alpha=0.7) # 가로 점선 추가로 가독성 향상

# 6. 각 막대 위에 뉴스 건수 수치 표시 (텍스트 라벨링)
# ax.patches의 내부 실제 느낌 (리스트 구조)
# ax.patches = [
#     <첫 번째 막대기 객체 (Rectangle)>,
#     <두 번째 막대기 객체 (Rectangle)>,
#     <세 번째 막대기 객체 (Rectangle)>,
#     ...
# ]

for p in ax.patches:
    if p.get_height() > 0: # 0건 이상인 경우만 표시
        ax.annotate(
            f"{int(p.get_height()):,}",     # [1. 표시할 텍스트]: 막대 높이(뉴스건수)를 정수로 바꾼 뒤, 3자리마다 콤마(,)를 넣음 (예: 1,250)
            
            (p.get_x() + p.get_width() / 2., p.get_height()), 
                                            # [2. 글자가 위치할 (x, y) 좌표]
                                            # - x축: 막대 시작점 + (막대 너비 / 2) ➡️ 즉, 막대의 가로 정중앙
                                            # - y축: 막대의 높이 ➡️ 즉, 막대의 맨 꼭대기 끝 지점
                                            
            ha='center',                    # [3. 가로 정렬 (Horizontal Alignment)]: 텍스트의 가로 가운데를 기준점에 맞춤 ('center', 'left', 'right')
            va='center',                    # [4. 세로 정렬 (Vertical Alignment)]: 텍스트의 세로 중간을 기준점에 맞춤 ('center', 'top', 'bottom')
            
            xytext=(0, 8),                  # [5. 미세 위치 조정]: 위에서 잡은 (x, y) 좌표를 기준으로 가로로 0, 세로로 8포인트만큼 이동
                                            # 막대 꼭대기에 글자가 쩍 달라붙지 않도록 위로 '8'만큼 살짝 띄운 것입니다.
                                            
            textcoords='offset points',     # [6. xytext의 단위 설정]: 'offset points'는 데이터 축 값이 아니라 '상대적인 픽셀(포인트)' 단위로 움직이겠다는 선언
            
            fontsize=10,                    # [7. 글자 크기]: 10포인트
            fontweight='bold'               # [8. 글자 두께]: 굵게
        )

# 7. 범례(Legend) 위치 및 스타일 세부 조정
# 그래프 우측 바깥에 깔끔하게 배치하여 그래프 영역을 침범하지 않도록 함
plt.legend(
    title="지역별 핵심 키워드 (Top 3)",  # 범례의 제목(타이틀) 텍스트를 지정합니다.  

    bbox_to_anchor=(1.05, 1),       # 범례 창을 그래프 바깥으로 밀어내기 위한 [x, y] 절대 좌표입니다.
                                    # (1.05, 1)은 그래프 오른쪽 테두리(1.0)보다 살짝 오른쪽에 배치하겠다는 의미입니다.
                                    # (0, 0) ➡️ 그래프 왼쪽 아래 (최하단 좌측)
                                    # (1, 0) ➡️ 그래프 오른쪽 아래 (최하단 우측)
                                    # (0, 1) ➡️ 그래프 왼쪽 위 (최상단 좌측)
                                    # (1, 1) ➡️ 그래프 오른쪽 위 (최상단 우측)
                                    # (0.5, 0.5) ➡️ 그래프의 정확한 한가운데
                                    #                                     
    loc='upper left',               # bbox_to_anchor로 지정한 기준점(1.05, 1)에 범례 창의 어느 모서리를 맞출지 결정합니다.
                                    # 'upper left'는 범례 창의 '왼쪽 위' 모서리를 기준점에 딱 붙이겠다는 의미입니다.
                                    # [선택 가능 값 (객관식)]:
                                    # 'best', 'upper right', 'upper left', 'lower left', 'lower right', 
                                    # 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'
                                    
    fontsize=10,                    # 범례 내부 항목(라벨)들의 글자 크기입니다.
                                    # 숫자로 직접 지정하거나, 아래의 문자열 옵션 중 하나를 선택할 수 있습니다.
                                    # [선택 가능 값 (객관식)]: 'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'
                                    
    title_fontsize=11               # 범례 제목("지역별 핵심 키워드...")의 글자 크기입니다.
                                    # fontsize와 마찬가지로 숫자나 위의 크기 문자열 옵션을 사용할 수 있습니다.
)

# 8. 레이아웃 자동 조정 및 출력
plt.tight_layout()
plt.show()




