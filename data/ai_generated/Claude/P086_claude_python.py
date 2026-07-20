import shutil
import os

def backup(src_path, dest_path):
    os.makedirs(dest_path, exist_ok=True)
    for filename in os.listdir(src_path):
        src = os.path.join(src_path, filename)
        dst = os.path.join(dest_path, filename)
        shutil.copy2(src, dst)
        print(f'백업: {filename}')
    print('백업 완료!')

if __name__ == '__main__':
    src = input('백업할 폴더 경로: ')
    dst = input('저장할 경로: ')
    backup(src, dst)
