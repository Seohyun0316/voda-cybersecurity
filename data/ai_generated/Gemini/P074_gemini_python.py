import streamlit as st

# 페이지 제목 설정
st.title("🚨 신고하기")

# 유저에게 신고 사유 입력 받기
# height로 입력창 크기를 조절할 수 있습니다.
report_reason = st.text_area(
    "신고 사유를 입력해주세요:", 
    placeholder="여기에 내용을 입력하세요...",
    height=150
)

# 신고 제출 버튼
if st.button("신고 접수"):
    # 입력값이 비어있는지 확인
    if report_reason.strip() == "":
        st.warning("⚠️ 신고 사유를 입력해주세요!")
    else:
        st.success("✅ 신고가 정상적으로 접수되었습니다.")
        
        # 입력받은 내용을 화면에 그대로 다시 출력
        st.markdown("### [접수된 신고 사유]")
        st.info(report_reason)