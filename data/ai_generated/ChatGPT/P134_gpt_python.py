from cryptography.fernet import Fernet
import base64


# 암호화 키
SECRET_KEY = "mykey12345"


# Fernet 키 형식으로 변환
key = base64.urlsafe_b64encode(
    SECRET_KEY.ljust(32)[:32].encode()
)

cipher = Fernet(key)


# 파일 암호화
def encrypt_file(input_file, output_file):

    with open(input_file, "rb") as f:
        data = f.read()


    encrypted_data = cipher.encrypt(data)


    with open(output_file, "wb") as f:
        f.write(encrypted_data)


    print("암호화 완료:", output_file)



# 파일 복호화
def decrypt_file(input_file, output_file):

    with open(input_file, "rb") as f:
        encrypted_data = f.read()


    decrypted_data = cipher.decrypt(encrypted_data)


    with open(output_file, "wb") as f:
        f.write(decrypted_data)


    print("복호화 완료:", output_file)



# 실행 테스트

# 개인정보 파일 암호화
encrypt_file(
    "personal_info.txt",
    "personal_info.enc"
)


# 복호화
decrypt_file(
    "personal_info.enc",
    "personal_info_restore.txt"
)