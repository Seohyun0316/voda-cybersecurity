from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

KEY = b'mykey12345000000'  # 16바이트로 맞춤

def encrypt(plaintext):
    cipher = AES.new(KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode()
    ct = base64.b64encode(ct_bytes).decode()
    return iv + ':' + ct

def decrypt(encrypted):
    iv_b64, ct_b64 = encrypted.split(':')
    iv = base64.b64decode(iv_b64)
    ct = base64.b64decode(ct_b64)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

if __name__ == '__main__':
    text = input('암호화할 텍스트: ')
    encrypted = encrypt(text)
    print(f'암호화: {encrypted}')
    print(f'복호화: {decrypt(encrypted)}')
