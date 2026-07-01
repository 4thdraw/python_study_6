from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd

# 1. 데이터 로드 및 폰트 설정
file_path = "./원본/한국언론진흥재단_뉴스빅데이터_메타데이터_노인_20011231.csv"
df = pd.read_csv(file_path, encoding="cp949")

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 2. 불용어 및 지역 필터링 설정
base_stop_words = {
    "노인",
    "참석",
    "일동",
    "주민",
    "지역",
    "마을",
    "노인들",
    "노인분들",
    "주민들",
    "주민일동",
    "이날",
}

region_mask = df["통합 분류1"].notna() & df["통합 분류1"].str.contains("지역")
df_region = df[region_mask].copy()

df_region["상세지역"] = df_region["통합 분류1"].apply(
    lambda x: x.split('-')[-1].strip() if "-" in str(x) else x.strip()
)

df_region["키워드"] = df_region["키워드"].fillna("")
all_region_names = set(df_region["상세지역"].dropna().unique())


# 3. 키워드 정제 함수
def get_clean_keywords(text):
    if not text:
        return []
    words = [
        word.strip() for word in str(text).replace(",", " ").split() if word.strip()
    ]
    return [
        word
        for word in words
        if word not in base_stop_words
        and not any(region in word for region in all_region_names)
    ]


df_region["정제된_리스트"] = df_region["키워드"].apply(get_clean_keywords)

# 4. 데이터 쪼개기 및 빈도수 집계
df_exploded = df_region[["상세지역", "정제된_리스트"]].explode("정제된_리스트")
df_exploded.columns = ["상세지역", "키워드"]
df_exploded = df_exploded.dropna()

df_word_counts = (
    df_exploded.groupby(["상세지역", "키워드"])
    .size()
    .reset_index(name="뉴스건수")
)

# 5. 순위 매기기 및 상위 3개 추출
df_word_counts["순위"] = (
    df_word_counts.groupby("상세지역")["뉴스건수"]
    .rank(method="first", ascending=False)
    .astype(int)
)
visual_df = df_word_counts[df_word_counts["순위"] <= 3].copy()

# 6. [정렬] 상위 3개 키워드 총합이 많은 상세지역 순서 정의
region_order = (
    visual_df.groupby("상세지역")["뉴스건수"]
    .sum()
    .sort_values(ascending=False)
    .index
)

# ------------------------------------------------------------------
# 📊 [시각화 구현] 범례 키워드 유지 + 막대 내부 고유 번호 매핑
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(16, 9))

# 데이터셋에 등장하는 모든 고유 키워드 추출 및 최신 버전 colormap 적용
unique_keywords = visual_df["키워드"].unique()
cmap = plt.get_cmap("tab20")

# 모든 키워드에 대해 1부터 시작하는 고유 번호(Row Number)와 색상 딕셔너리 생성
keyword_colors = {}
keyword_numbers = {}
for i, kw in enumerate(unique_keywords):
    keyword_colors[kw] = cmap(i % 20)
    keyword_numbers[kw] = i + 1  # 1, 2, 3... 고유 Row Number 부여

bar_width = 0.28  # 막대 두께
indices = range(len(region_order))

# 범례 핸들 관리를 위한 딕셔너리 (중복 방지용)
legend_dict = {}

# 지역별로 순회하며 막대 그리기
for i, region in enumerate(region_order):
    region_data = visual_df[visual_df["상세지역"] == region].sort_values("순위")

    for _, row in region_data.iterrows():
        rank = row["순위"]  # 지역 내 등수 (1, 2, 3)
        count = row["뉴스건수"]
        keyword = row["키워드"]
        kw_num = keyword_numbers[keyword]  # 키워드 자체의 고유 번호 (Row Number)

        # 1위, 2위, 3위 막대를 빈 공간 없이 촘촘하게 붙여 배치
        offset = (rank - 2) * bar_width
        bar_pos = i + offset

        # 막대 출력
        rect = ax.bar(
            bar_pos,
            count,
            width=bar_width,
            color=keyword_colors[keyword],
            edgecolor="gray",
            linewidth=0.5,
        )

        # ① 막대 내부: 지역 내 등수(rank) 대신, 키워드의 고유 번호(kw_num)를 삽입
        ax.text(
            bar_pos,
            count / 2,
            str(kw_num),
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="black",
        )

        # ② 막대 상단: 뉴스 건수 수치 표시
        ax.text(
            bar_pos,
            count + (max(visual_df["뉴스건수"]) * 0.005),
            f"{count:,}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="semibold",
        )

        # ③ 범례용 라벨 가공: 키워드 이름 앞에 고유 번호(Row Number) 부착
        legend_label = f"{kw_num}. {keyword}"
        if legend_label not in legend_dict:
            legend_dict[legend_label] = rect[0]

# 그래프 기본 디자인
ax.set_title(
    "상세지역별 상위 핵심 키워드(Top 3) 빈도수 분포",
    fontsize=18,
    fontweight="bold",
    pad=20,
)
ax.set_xlabel("상세 지역", fontsize=13, labelpad=10)
ax.set_ylabel("뉴스 빈도수 (건)", fontsize=13, labelpad=10)

ax.set_xticks(indices)
ax.set_xticklabels(region_order, rotation=45, fontsize=11)
ax.grid(axis="y", linestyle="--", alpha=0.4)

# ④ 범례 설정: 번호 순서(1, 2, 3...)대로 이쁘게 정렬하여 우측에 배치
sorted_legend_labels = sorted(
    legend_dict.keys(), key=lambda x: int(x.split(".")[0])
)
sorted_handles = [legend_dict[label] for label in sorted_legend_labels]

ax.legend(
    sorted_handles,
    sorted_legend_labels,
    title="핵심 키워드 (번호매칭)",
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    fontsize=10,
    title_fontsize=11,
)

plt.tight_layout()
plt.show()