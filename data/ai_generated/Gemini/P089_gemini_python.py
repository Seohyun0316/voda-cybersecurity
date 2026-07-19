import pandas as pd

def read_csv_file(file_path):
    try:
        # utf-8로 먼저 시도하고, 실패하면 한국어 엑셀 파일용 cp949/euc-kr로 읽습니다.
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')
        
        # 데이터프레임을 딕셔너리(JSON 구조) 리스트로 변환
        data = df.to_dict(orient='records')
        return data

    except Exception as e:
        print(f"파일을 읽는 중 에러가 발생했습니다: {e}")
        return None

# 사용 예시 (로컬 파일 경로 입력)
file_path = "example.csv"
parsed_data = read_csv_file(file_path)

if parsed_data:
    # 상위 2개 데이터만 예쁘게 출력해보는 예시
    import json
    print(json.dumps(parsed_data[:2], indent=4, ensure_ascii=False))