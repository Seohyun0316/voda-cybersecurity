import secrets

def generate_session_id():
    return secrets.token_hex(16)

# ¿¹½Ã
session_id = generate_session_id()
print(session_id)