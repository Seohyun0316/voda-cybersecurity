import bcrypt

# 가상의 DB 역할 (실제로는 데이터베이스 조회/수정 로직이 들어갑니다)
class FakeDB:
    @staticmethod
    def get_password_hash(user_id):
        # DB에 저장되어 있던 기존의 '암호화된' 비밀번호 해시값 (예시)
        # 실제 DB에는 문자열이나 bytes 형태로 저장됩니다.
        return b'$2b$12$KIXv8S1W8P7g8Z.YV7cMeeV9lA3C6M8B4L2xG3j8K9l0m1n2o3p4q'

    @staticmethod
    def update_password(user_id, new_password_hash):
        print(f"[DB 반영] 유저 {user_id}의 비밀번호를 {new_password_hash}로 업데이트했습니다.")


def change_password(user_id, current_password, new_password):
    # 1. DB에서 해당 유저의 기존 암호화된 비밀번호(해시) 가져오기
    hashed_password_in_db = FakeDB.get_password_hash(user_id)
    
    # 2. 사용자가 입력한 '현재 비밀번호'가 맞는지 검증
    # bcrypt.checkpw(바이트_문자열, 바이트_해시값) 형태로 비교해야 합니다.
    is_match = bcrypt.checkpw(current_password.encode('utf-8'), hashed_password_in_db)
    
    if not is_match:
        print("❌ 오류: 현재 비밀번호가 일치하지 않습니다.")
        return False

    # 3. 새 비밀번호 안전하게 해싱 (Salt 자동 생성 및 적용)
    # gensalt()의 인자(기본값 12)가 높을수록 연산이 복잡해져 보안이 강해지지만 속도가 느려집니다.
    salt = bcrypt.gensalt()
    new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)

    # 4. DB에는 새로 해싱된 비밀번호를 저장
    FakeDB.update_password(user_id, new_hashed_password)
    print("✅ 성공: 비밀번호가 안전하게 변경되었습니다.")
    return True


# --- 실행 테스트 ---
# 유저가 웹 폼에 입력한 데이터라고 가정합니다.
user_id = "user123"
input_current_pw = "my_old_password_123"  # 현재 비밀번호 입력
input_new_pw = "super_secure_new_pw!@"    # 새 비밀번호 입력

change_password(user_id, input_current_pw, input_new_pw)