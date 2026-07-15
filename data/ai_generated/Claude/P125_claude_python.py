import hashlib

def checksum_md5(filepath):
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()

if __name__ == '__main__':
    filepath = input('파일 경로: ')
    cs = checksum_md5(filepath)
    print(f'MD5 체크섬: {cs}')
