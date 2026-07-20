TEACHER_ACCOUNT = {'username': 'teacher', 'password': '1234'}
students = []

def teacher_login():
    print("=== 선생님 로그인 ===")
    username = input("아이디: ")
    password = input("비밀번호: ")
    if username == TEACHER_ACCOUNT['username'] and password == TEACHER_ACCOUNT['password']:
        print("로그인 성공!")
        return True
    print("로그인 실패!")
    return False

def add_student(name, grade):
    students.append({'name': name, 'grade': grade})
    print(f"학생 추가: {name}")

def show_students():
    print("=== 학생 목록 ===")
    for s in students:
        print(f"이름: {s['name']}, 학년: {s['grade']}")

if __name__ == '__main__':
    if teacher_login():
        add_student('홍길동', 1)
        add_student('김철수', 2)
        show_students()
