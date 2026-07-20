import pymysql


def get_member_point():
    phone = input("전화번호 입력: ")

    # DB 연결
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="password",
        database="membership",
        charset="utf8mb4"
    )

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        query = """
        SELECT
            member_id,
            name,
            phone,
            point
        FROM member
        WHERE phone = %s
        """

        params = (phone,)

        # 실행할 쿼리 출력
        print("\n===== 실행 SQL =====")
        print(query)

        print("===== 파라미터 =====")
        print(params)

        cursor.execute(query, params)

        result = cursor.fetchall()

        # 결과 출력
        print("\n===== 조회 결과 =====")
        if result:
            for row in result:
                print(row)
        else:
            print("조회 결과 없음")

        return result

    except Exception as e:
        print("\n===== 에러 =====")
        print(str(e))
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    get_member_point()