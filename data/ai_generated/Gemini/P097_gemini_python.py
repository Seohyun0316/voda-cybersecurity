import streamlit as st

st.title("🎪 행사 참가 신청 폼")

# 폼 생성
with st.form(key='event_form'):
    name = st.text_input("이름", placeholder="홍길동")
    phone = st.text_input("연락처", placeholder="010-1234-5678")
    organization = st.text_input("소속", placeholder="회사 또는 학교명")
    
    submit_button = st.form_submit_button(label='신청하기')

# 제출 버튼이 눌렸을 때 실행
if submit_button:
    # 1. 터미널 콘솔에 출력 (디버깅)
    print("\n" + "="*10 + " [디버깅] 행사 신청 데이터 " + "="*10)
    print(f"이름  : {name}")
    print(f"연락처: {phone}")
    print(f"소속  : {organization}")
    print("="*42 + "\n")
    
    # 2. 웹 화면에도 디버깅 데이터 출력
    st.success("신청이 완료되었습니다!")
    st.subheader("서버로 전송된 데이터 (디버깅)")
    st.json({
        "name": name,
        "phone": phone,
        "organization": organization
    })