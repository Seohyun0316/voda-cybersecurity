import uuid

def generate_session_id():
    return str(uuid.uuid4())

print(generate_session_id())
# 출력 예시: "a3b1c2d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"