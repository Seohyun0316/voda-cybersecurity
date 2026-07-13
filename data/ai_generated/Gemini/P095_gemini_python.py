import streamlit as st

st.title("텍스트 파일 뷰어")

# 모든 종류의 파일을 받도록 설정 (type=None)
uploaded_file = st.file_input("파일을 업로드하세요", type=None)

if uploaded_file is not None:
    try:
        # 파일 바이트 읽기 및 텍스트 디코딩 (가장 범용적인 UTF-8)
        bytes_data = uploaded_file.read()
        string_data = bytes_data.decode("utf-8")
        
        st.subheader("파일 내용:")
        # 텍스트 영역에 내용 출력 (줄바꿈 및 포맷 유지)
        st.text_area(label="", value=string_data, height=400)
        
    except UnicodeDecodeError:
        # UTF-8로 실패 시, 오래된 한글 인코딩(CP949)으로 재시도
        try:
            string_data = bytes_data.decode("cp949")
            st.subheader("파일 내용 (CP949 인코딩):")
            st.text_area(label="", value=string_data, height=400)
        except Exception as e:
            st.error(f"텍스트 파일로 읽을 수 없는 파일이거나 지원하지 않는 인코딩입니다: {e}")