from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# [문항관리 시트 구조 반영] 인덱스 스캔 성능 향상을 위한 Value 매핑 구조 적용
QUESTIONS = {
    "Q0": {
        "section": 1,
        "type": "radio",
        "title": "시작하기 전 확인: 현재 반려동물(강아지, 고양이 등)을 키우고 계십니까?",
        "choices": [
            {"text": "예, 있습니다.", "value": "1"},
            {"text": "아니오, 없습니다. (설문 종료)", "value": "2"}
        ],
        "required": True
    },
    "Q1": {
        "section": 2,
        "type": "radio",
        "title": "Q1. 귀하는 반려동물이 무지개다리를 건넜을 때(사후)의 대처 방안이나 장례 절차에 대해 생각해 보신 적이 있습니까?",
        "choices": [
            {"text": "구체적인 계획과 방법을 알아본 적이 있다.", "value": "1"},
            {"text": "막연하게 생각만 해보았다.", "value": "2"},
            {"text": "아직 한 번도 생각해 본 적이 없다.", "value": "3"}
        ],
        "required": True
    },
    "Q2": {
        "section": 2,
        "type": "checkbox",
        "title": "Q2. 반려동물 장례 서비스(화장, 장례식 등)를 이용할 때 가장 염려되거나 부담스러운 부분은 무엇입니까? (중복 선택 가능)",
        "choices": [
            {"text": "갑작스러운 이별로 인한 정신적 충격(정서적 대처 어려움)", "value": "1"},
            {"text": "일시에 발생하는 장례 비용에 대한 경제적 부담", "value": "2"},
            {"text": "믿을 만한 합법적 장례 업체 정보를 찾는 것의 어려움", "value": "3"},
            {"text": "장례 절차 및 행정 처리(사망신고 등)에 대한 무지", "value": "4"}
        ],
        "required": True,
        "has_other": True
    },
    "Q3": {
        "section": 2,
        "type": "radio",
        "title": "Q3. 매달 일정 금액을 지불하고, 추후 반려동물 장례 시 필요한 비용과 서비스를 보장받는 '펫장례 구독(상조) 서비스'를 들어보신 적이 있습니까?",
        "choices": [
            {"text": "잘 알고 있으며, 필요성을 느낀다.", "value": "1"},
            {"text": "들어본 적은 있으나 구체적인 내용은 모른다.", "value": "2"},
            {"text": "이번에 처음 알게 되었다.", "value": "3"}
        ],
        "required": True
    },
    "Q4": {
        "section": 2,
        "type": "radio",
        "title": "Q4. 만약 펫장례 구독서비스를 이용한다면, '장례(화장/수목장 등)' 외에 가장 포함되었으면 하는 연계 서비스는 무엇입니까?",
        "choices": [
            {"text": "펫로스 증후군 케어 (심리 상담, 치유 프로그램 등)", "value": "1"},
            {"text": "노령견/노령묘를 위한 사전 헬스케어 상담 및 건강 검진 연계", "value": "2"},
            {"text": "메모리얼 스톤, 유골함, 초상화 등 추모 굿즈 제작 지원", "value": "3"},
            {"text": "정기 펫 스튜디오 사진 촬영 (영정사진 또는 추억 소장용)", "value": "4"},
            {"text": "유산 상속 및 법률/행정 절차 대행 지원", "value": "5"}
        ],
        "required": True
    },
    "Q5": {
        "section": 2,
        "type": "radio",
        "title": "Q5. 펫장례 구독서비스 선택 시 가장 중요하게 고려할 기준은 무엇입니까?",
        "choices": [
            {"text": "서비스 제공 업체의 신뢰도 및 규모", "value": "1"},
            {"text": "월 구독료 및 총 납입 금액의 가성비", "value": "2"},
            {"text": "장례 시설의 위치 및 접근성", "value": "3"},
            {"text": "장례 지도사의 전문성과 친절도", "value": "4"},
            {"text": "중도 해지 시 환불 규정 및 안정성", "value": "5"}
        ],
        "required": True
    },
    "Q6": {
        "section": 2,
        "type": "radio",
        "title": "Q6. 반려동물의 장례를 미리 준비하기 위해 지불할 수 있는 '적정 월 구독료'는 얼마라고 생각하십니까?",
        "choices": [
            {"text": "5,000원 미만", "value": "1"},
            {"text": "5,000원 이상 ~ 10,000원 미만", "value": "2"},
            {"text": "10,000원 이상 ~ 20,000원 미만", "value": "3"},
            {"text": "20,000원 이상 ~ 30,000원 미만", "value": "4"},
            {"text": "30,000원 이상", "value": "5"}
        ],
        "required": True
    },
    "Q7": {
        "section": 2,
        "type": "radio",
        "title": "Q7. 위에서 선택하신 금액대나 혜택이 만족스럽다면, 해당 펫장례 구독서비스를 이용(가입)하실 의향이 있으십니까?",
        "choices": [
            {"text": "매우 있다 (바로 가입 고려)", "value": "1"},
            {"text": "약간 있다 (조건이 맞으면 가입 고려)", "value": "2"},
            {"text": "보통이다 (잘 모르겠다)", "value": "3"},
            {"text": "별로 없다 (필요할 때 일시불로 결제하겠다)", "value": "4"},
            {"text": "전혀 없다 (장례 서비스 자체를 이용할 생각이 없다)", "value": "5"}
        ],
        "required": True
    },
    "Q8": {
        "section": 2,
        "type": "radio",
        "title": "Q8. 현재 함께 거주하고 계신 반려동물의 종류는 무엇입니까? (다수일 경우 주 반려동물 기준)",
        "choices": [
            {"text": "반려견 (강아지)", "value": "1"},
            {"text": "반려묘 (고양이)", "value": "3"} # 원본 데이터 코딩값 3 유지
        ],
        "required": True
    },
    "Q9": {
        "section": 2,
        "type": "radio",
        "title": "Q9. 현재 키우고 계신 반려동물의 나이는 어떻게 됩니까? (다수일 경우 가장 나이가 많은 아이 기준)",
        "choices": [
            {"text": "1세 ~ 3세 (성장기/청년기)", "value": "1"},
            {"text": "4세 ~ 7세 (성숙기)", "value": "2"},
            {"text": "8세 ~ 12세 (노령기 진입)", "value": "3"},
            {"text": "13세 이상 (초고령기)", "value": "4"}
        ],
        "required": True
    },
    "Q10": {
        "section": 2,
        "type": "radio",
        "title": "Q10. 귀하의 연령대는 어떻게 되십니까?",
        "choices": [
            {"text": "20대 이하", "value": "1"},
            {"text": "30대", "value": "2"},
            {"text": "40대", "value": "3"},
            {"text": "50대", "value": "4"},
            {"text": "60대 이상", "value": "5"}
        ],
        "required": True
    }
}

@app.route('/')
def index():
    # 설문 작성 페이지 렌더링
    return render_template('survey.html', questions=QUESTIONS)

@app.route('/submit', methods=['POST'])
def submit():
    response_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 전달받은 form 데이터를 맵핑 테이블 규칙(Q0~Q10)에 맞춰 수집
    for q_id, q_info in QUESTIONS.items():
        if q_info["type"] == "checkbox":
            # 체크박스 중복 선택 처리 (예: '1,3')
            selected_values = request.form.getlist(q_id)
            
            # '기타 의견' 텍스트 주관식 입력이 활성화된 경우 데이터 병합
            other_val = request.form.get(f"{q_id}_other", "").strip()
            if other_val:
                selected_values.append(other_val)
                
            response_data[q_id] = ",".join(selected_values)
        else:
            # 라디오 버튼 단일 선택 처리 (숫자 값만 추출)
            response_data[q_id] = request.form.get(q_id, "")
            
    # 정형화된 정수 인덱스 구조로 백엔드 수집 데이터 출력 (스캔 최적화 완료 형태)
    print("🎯 수집된 데이터 패킷:", response_data)
    
    # TODO: 여기에서 추출된 response_data를 DB(MySQL, SQLite) 혹은 구글 시트에 인서트 하시면 됩니다.
    return jsonify({"status": "success", "received": response_data})

if __name__ == '__main__':
    app.run(debug=True)