import secrets
import string

def generate_temp_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

# ¿¹½Ã
print(generate_temp_password())