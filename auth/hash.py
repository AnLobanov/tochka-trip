from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"])

def hash(password: str) -> str:
    return context.hash(password)

def verify(password: str, hash: str) -> bool:
    return context.verify(password, hash)