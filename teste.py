from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["argon2"], deprecated="auto")

senha = "teste123"
hash_gerado = bcrypt_context.hash(senha)
print("Hash:", hash_gerado)
print("Verifica:", bcrypt_context.verify("teste123", hash_gerado))
