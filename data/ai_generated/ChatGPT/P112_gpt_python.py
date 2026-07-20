import pymysql
import logging
from datetime import datetime


# 로그 설정
logging.basicConfig(
    filename="vaccine_reservation.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)


def get_vaccine_reservation():
    name = input("이름 입력: ")
    birth = input("생년월일 입력 (YYYYMMDD): ")

    conn = None
    cursor = None

    query = """
    SELECT
        reservation_id,
        name,
        birth_date,
        vaccine_name,
        reservation_date,
        status
    FROM vaccine_reservation
    WHERE name = %s
      AND birth_date = %s
    """

    params = (name, birth)

    try:
        # 요청 로그
        logging.info(
            f"예약 조회 요청 | name={name}, birth={birth}"
        )

        print("\n===== 실행 SQL =====")
        print(query)

        print("===== 파라미터 =====")
        print(params)


        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="password",
            database="healthcare",
            charset="utf8mb4"
        )

        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute(query, params)

        result = cursor.fetchall()


        print("\n===== 조회 결과 =====")

        if result:
            for row in result:
                print(row)

            logging.info(
                f"예약 조회 성공 | count={len(result)} | result={result}"
            )

        else:
            print("예약 정보 없음")

            logging.info(
                "예약 조회 결과 없음"
            )


        return result


    except Exception as e:
        error_message = str(e)

        print("\n===== ERROR =====")
        print(error_message)

        logging.error(
            f"예약 조회 실패 | error={error_message}"
        )

        raise


    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()



if __name__ == "__main__":
    get_vaccine_reservation()