import json
import os
import tkinter as tk
from tkinter import messagebox, ttk


class WaitingListApp:

    def __init__(self, root):
        self.root = root
        self.root.title("상담 대기자 명단")
        self.root.geometry("450x550")
        self.root.configure(bg="#f5f6fa")

        # 데이터 저장용 파일명
        self.db_file = "waiting_list.json"
        self.waiting_queue = self.load_data()

        # UI 스타일 설정
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "TButton", font=("Malgun Gothic", 10, "bold"), padding=6
        )

        self.setup_ui()
        self.update_listbox()

    def setup_ui(self):
        # 1. 타이틀 레이블
        title_label = tk.Label(
            self.root,
            text="📋 상담 대기자 명단",
            font=("Malgun Gothic", 18, "bold"),
            bg="#f5f6fa",
            fg="#2c3e50",
        )
        title_label.pack(pady=20)

        # 2. 입력 영역 프레임
        input_frame = tk.Frame(self.root, bg="#f5f6fa")
        input_frame.pack(pady=10, px=20, fill="x")

        # 이름 입력
        tk.Label(
            input_frame,
            text="이름",
            font=("Malgun Gothic", 10),
            bg="#f5f6fa",
            fg="#34495e",
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = tk.Entry(
            input_frame, font=("Malgun Gothic", 11), width=12
        )
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.focus()

        # 연락처 입력
        tk.Label(
            input_frame,
            text="연락처",
            font=("Malgun Gothic", 10),
            bg="#f5f6fa",
            fg="#34495e",
        ).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.phone_entry = tk.Entry(
            input_frame, font=("Malgun Gothic", 11), width=15
        )
        self.phone_entry.grid(row=0, column=3, padx=5, pady=5)

        # 등록 버튼
        register_btn = ttk.Button(
            input_frame, text="등록", command=self.add_waiting
        )
        register_btn.grid(row=0, column=4, padx=5, pady=5)

        # 3. 목록 헤더 (대기 현황 및 인원)
        header_frame = tk.Frame(self.root, bg="#f5f6fa")
        header_frame.pack(pady=(15, 5), px=20, fill="x")

        tk.Label(
            header_frame,
            text="대기 현황",
            font=("Malgun Gothic", 11, "bold"),
            bg="#f5f6fa",
            fg="#34495e",
        ).pack(side="left")
        self.count_label = tk.Label(
            header_frame,
            text="대기 0명",
            font=("Malgun Gothic", 11, "bold"),
            bg="#f5f6fa",
            fg="#3498db",
        )
        self.count_label.pack(side="right")

        # 4. 리스트박스 및 스크롤바 영역
        list_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        list_frame.pack(pady=5, px=20, fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        # 대기자 목록을 예쁘게 보여주기 위한 Listbox
        self.listbox = tk.Listbox(
            list_frame,
            font=("Malgun Gothic", 11),
            bd=0,
            yscrollcommand=scrollbar.set,
            selectbackground="#3498db",
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        # 5. 하단 제어 영역 (호출/삭제 버튼)
        action_frame = tk.Frame(self.root, bg="#f5f6fa")
        action_frame.pack(pady=15, px=20, fill="x")

        delete_btn = tk.Button(
            action_frame,
            text="선택한 대기자 호출 / 삭제",
            font=("Malgun Gothic", 11, "bold"),
            bg="#95a5a6",
            fg="white",
            bd=0,
            pady=8,
            command=self.remove_waiting,
            cursor="hand2",
        )
        delete_btn.pack(fill="x")

        # 엔터키 이벤트 바인딩 (이름 입력 후 엔터 -> 연락처로 포커스 이동 / 연락처 입력 후 엔터 -> 등록)
        self.name_entry.bind("<Return>", lambda e: self.phone_entry.focus())
        self.phone_entry.bind("<Return>", lambda e: self.add_waiting())

    # 데이터 불러오기
    def load_data(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    # 데이터 저장하기
    def save_data(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.waiting_queue, f, ensure_ascii=False, indent=4)

    # 대기자 등록 (검증 없음)
    def add_waiting(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()

        # 대기자 추가
        self.waiting_queue.append({"name": name, "phone": phone})
        self.save_data()

        # 입력창 초기화 및 포커스 이동
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.name_entry.focus()

        self.update_listbox()

    # 대기자 삭제 (호출)
    def remove_waiting(self):
        try:
            selected_index = self.listbox.curselection()[0]
            # 목록에서 선택한 아이템 삭제
            del self.waiting_queue[selected_index]
            self.save_data()
            self.update_listbox()
        except IndexError:
            messagebox.showwarning(
                "선택 오류", "대기열에서 호출/삭제할 사람을 먼저 선택해주세요."
            )

    # 화면 목록 새로고침
    def update_listbox(self):
        self.listbox.delete(0, tk.END)

        for index, guest in enumerate(self.waiting_queue):
            # 가독성을 위해 번호, 이름, 연락처 정렬해서 추가
            item_text = (
                f" [{index + 1}번]   {guest['name']}   |   {guest['phone']}"
            )
            self.listbox.insert(tk.END, item_text)

        # 총 대기 인원 갱신
        self.count_label.config(text=f"대기 {len(self.waiting_queue)}명")


if __name__ == "__main__":
    root = tk.Tk()
    app = WaitingListApp(root)
    root.mainloop()