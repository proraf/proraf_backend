from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "testpass123"
print("Senha em texto puro:", password)
print("Tamanho em bytes:", len(password.encode()))

hashed = pwd_context.hash(password)
print("Hash gerado com sucesso:", hashed)
