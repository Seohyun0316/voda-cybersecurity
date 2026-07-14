import hashlib

def file_checksum(path):
    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)

    return sha256.hexdigest()

# ¿¹½Ã
print(file_checksum("example.txt"))