# teacher_login.py

# 고정 계정
TEACHER_ID = "teacher"
TEACHER_PASSWORD = "1234"

teacher_id = input("아이디: ")
teacher_pw = input("비밀번호: ")

if teacher_id == TEACHER_ID and teacher_pw == TEACHER_PASSWORD:
    print("로그인 성공!")
    print("학생 관리 프로그램에 오신 것을 환영합니다.")
else:
    print("아이디 또는 비밀번호가 올바르지 않습니다.")