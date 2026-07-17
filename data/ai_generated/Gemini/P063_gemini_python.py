import os
from datetime import datetime

# 질문을 저장할 파일 이름
FILE_NAME = "questions.txt"

def load_questions():
    """파일에서 질문 목록을 읽어옵니다."""
    if not os.path.exists(FILE_NAME):
        return []
    
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        # 파일 전체를 읽은 뒤, 각 질문 구분자인 '---QUESTION_BREAK---'로 나눕니다.
        content = f.read().strip()
        if not content:
            return []
        return content.split("\n---QUESTION_BREAK---\n")

def save_question(text):
    """새로운 질문을 파일에 추가합니다."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 입력받은 그대로 저장하기 위해 구분자와 시간 정보를 함께 포맷팅합니다.
    new_entry = f"★ 익명 질문자 ({now})\n{text}\n---QUESTION_BREAK---\n"
    
    # 파일의 맨 뒤에 이어붙입니다(append).
    with open(FILE_NAME, "a", encoding="utf-8") as f:
        f.write(new_entry)

def display_questions():
    """저장된 모든 질문을 화면에 그대로 출력합니다."""
    print("\n========================================")
    print("💬 실시간 익명 질문 목록")
    print("========================================")
    
    if not os.path.exists(FILE_NAME) or os.path.getsize(FILE_NAME) == 0:
        print("\n등록된 질문이 없습니다. 첫 질문을 남겨보세요!\n")
        return

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        # 입력된 그대로(줄바꿈 포함) 통째로 출력합니다.
        # 맨 마지막 구분자는 깔끔하게 지우고 출력합니다.
        content = f.read().strip("\n---QUESTION_BREAK---\n")
        print(content)
    print("========================================\n")

def main():
    while True:
        print("1. 질문 등록하기")
        print("2. 질문 목록 보기")
        print("3. 종료하기")
        
        choice = input("원하는 메뉴 번호를 입력하세요: ").strip()
        
        if choice == "1":
            print("\n[질문 입력] 입력이 끝나면 빈 줄에서 Enter를 한 번 더 누르거나, 작성 후 등록하세요.")
            print("(여러 줄 입력 가능)\n-")
            
            lines = []
            while True:
                line = input()
                if line == "":  # 아무것도 입력 안 하고 엔터 치면 입력 종료
                    break
                lines.append(line)
            
            question_text = "\n".join(lines)
            
            if question_text.strip():
                save_question(question_text)
                print("\n✅ 질문이 등록되었습니다!\n")
            else:
                print("\n❌ 내용은 공백일 수 없습니다.\n")
                
        elif choice == "2":
            display_questions()
            
        elif choice == "3":
            print("\n게시판 프로그램을 종료합니다. 감사합니다!")
            break
        else:
            print("\n❌ 잘못된 번호입니다. 1~3번 중에 골라주세요.\n")

if __name__ == "__main__":
    main()