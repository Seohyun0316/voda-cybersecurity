import pymysql

def get_student_scores(student_id):
    # 1. 데이터베이스 연결 설정
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='password',      # 본인의 DB 비밀번호 입력
        database='school_db',     # 본인의 DB 이름 입력
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor # 결과를 딕셔너리 형태로 받기 위함
    )

    try:
        with connection.cursor() as cursor:
            # 2. SQL 쿼리문 작성 (%s를 사용하여 파라미터 바인딩 처리)
            sql = """
                SELECT s.name AS '이름', g.subject AS '과목', g.score AS '점수', g.semester AS '학기'
                FROM students s
                JOIN scores g ON s.student_id = g.student_id
                WHERE s.student_id = %s
            """
            
            # 3. 쿼리 실행 (두 번째 인자로 학번을 튜플 형태로 전달)
            cursor.execute(sql, (student_id,))
            
            # 4. 결과 가져오기
            results = cursor.fetchall()
            
            # 5. 결과 출력
            if not results:
                print(f" 학번 [{student_id}]에 해당하는 성적 데이터가 없습니다.")
                return

            print(f"\n=== [{results[0]['이름']}] 학생의 성적 조회 결과 ===")
            for row in results:
                print(f"학기: {row['학기']} | 과목: {row['과목']} | 점수: {row['점수']}점")
                
    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {e}")
        
    finally:
        # 6. 연결 종료
        connection.close()

# --- 실행 예시 ---
if __name__ == "__main__":
    user_input = input("조회할 학번을 입력하세요: ")
    get_student_scores(user_input)