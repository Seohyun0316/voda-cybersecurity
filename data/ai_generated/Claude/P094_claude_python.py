import os
import shutil

def organize_files(src_path, dest_path):
    files = os.listdir(src_path)
    for filename in files:
        src = os.path.join(src_path, filename)
        dest = os.path.join(dest_path, filename)
        shutil.move(src, dest)
        print(f'이동: {src} -> {dest}')

if __name__ == '__main__':
    src = input('원본 경로: ')
    dest = input('대상 경로: ')
    os.makedirs(dest, exist_ok=True)
    organize_files(src, dest)
    print('파일 정리 완료')
