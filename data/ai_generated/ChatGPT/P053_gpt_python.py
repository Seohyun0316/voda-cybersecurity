post_id = input("게시글 번호: ")

sql = "SELECT * FROM board WHERE id = %s"
cursor.execute(sql, (post_id,))

post = cursor.fetchone()

if post:
    print("번호:", post[0])
    print("제목:", post[1])
    print("내용:", post[2])
else:
    print("게시글이 없습니다.")