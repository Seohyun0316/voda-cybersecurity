import secrets

def generate_reset_token():
    return secrets.token_urlsafe(32)

# ¿¹½Ã
token = generate_reset_token()
print(token)