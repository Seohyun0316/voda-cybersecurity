student_id = input("학번을 입력하세요: ")

sql = "SELECT * FROM grades WHERE student_id = %s"
cursor.execute(sql, (student_id,))

result = cursor.fetchone()

if result:
    print("학번:", result[0])
    print("이름:", result[1])
    print("국어:", result[2])
    print("영어:", result[3])
    print("수학:", result[4])
else:
    print("해당 학번의 학생이 없습니다.")