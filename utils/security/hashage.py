import bcrypt

def hash_password(plain: str) -> bytes:
    pw_bytes = plain.encode("utf-8")[:72]
    salt = bcrypt.gensalt()

    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def check_password(plain: str, hashed: str) -> bool:
    pw_bytes = plain.encode("utf-8")[:72]

    return bcrypt.checkpw(pw_bytes, hashed.encode("utf-8"))