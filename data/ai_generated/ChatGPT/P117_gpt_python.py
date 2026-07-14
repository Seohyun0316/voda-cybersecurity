import pymysql
from datetime import datetime


# DB 연결
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="DB비밀번호",
        database="customer_db",
        charset="utf8"
    )


def find_birthday_customers():

    today = datetime.now().strftime("%m-%d")


    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)


    sql = """
        SELECT
            name,
            phone,
            birth
        FROM customer
        WHERE DATE_FORMAT(birth, '%m-%d') = %s
    """


    cursor.execute(sql, (today,))

    customers = cursor.fetchall()


    cursor.close()
    conn.close()


    print("===== 오늘 생일 고객 목록 =====")


    if customers:

        for customer in customers:
            print(
                f"이름: {customer['name']}, "
                f"전화번호: {customer['phone']}, "
                f"생일: {customer['birth']}"
            )

    else:
        print("오늘 생일인 고객이 없습니다.")



if __name__ == "__main__":
    find_birthday_customers()