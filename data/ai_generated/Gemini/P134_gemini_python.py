import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 1. 키 설정 (요청하신 키를 16바이트 크기로 맞춤)
# 'mykey12345'는 10바이트이므로 뒤에 공백을 채워 16바이트로 만듭니다.
SECRET_KEY = b"mykey12345".ljust(16, b" ")


def encrypt_file(file_path):
    """파일을 암호화하는 함수"""
    if not os.path.exists(file_path):
        print(f"오류: {file_path} 파일이 존재하지 않습니다.")
        return

    # 파일 데이터 읽기
    with open(file_path, "rb") as f:
        data = f.read()

    # 암호화에 필요한 무작위 고유값(Nonce) 생성 (12 bytes)
    aesgcm = AESGCM(SECRET_KEY)
    nonce = os.urandom(12)

    # 데이터 암호화
    encrypted_data = aesgcm.encrypt(nonce, data, None)

    # 나중에 복호화할 때 nonce가 필요하므로 파일 앞부분에 붙여서 저장합니다.
    with open(file_path + ".enc", "wb") as f:
        f.write(nonce + encrypted_data)

    print(f"성공: {file_path} -> {file_path}.enc 암호화 완료")


def decrypt_file(encrypted_file_path):
    """암호화된 파일을 원래대로 복호화하는 함수"""
    if not os.path.exists(encrypted_file_path):
        print(f"오류: {encrypted_file_path} 파일이 존재하지 않습니다.")
        return

    # 암호화된 데이터 읽기
    with open(encrypted_file_path, "rb") as f:
        file_content = f.read()

    # 앞의 12바이트(Nonce)와 나머지(암호문) 분리
    nonce = file_content[:12]
    encrypted_data = file_content[12:]

    try:
        # 데이터 복호화
        aesgcm = AESGCM(SECRET_KEY)
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)

        # 복호화된 파일 저장 (확장자 .enc 제거)
        original_path = encrypted_file_path.replace(".enc", "")
        # 중복 방지를 위해 복호화된 파일임을 표시
        decrypted_path = original_path.replace(".", "_decrypted.")

        with open(decrypted_path, "wb") as f:
            f.write(decrypted_data)

        print(f"성공: {encrypted_file_path} -> {decrypted_path} 복호화 완료")

    except Exception as e:
        print("오류: 복호화에 실패했습니다. 키가 올바르지 않거나 파일이 손상되었습니다.")


# --- 사용 예시 ---
if __name__ == "__main__":
    # 테스트용 개인정보 파일 생성
    test_file = "privacy_data.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("홍길동, 900101-1234567, 010-1234-5678")

    # 1. 암호화 진행 (privacy_data.txt.enc 파일이 생성됨)
    encrypt_file(test_file)

    # 2. 복호화 진행 (privacy_data_decrypted.txt 파일이 생성됨)
    decrypt_file("privacy_data.txt.enc")