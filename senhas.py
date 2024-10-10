import bcrypt

# Novas senhas para Alice e Bob
alice_password = "senha123"
bob_password = "bob456"

# Gerar hash das senhas
alice_hash = bcrypt.hashpw(alice_password.encode(), bcrypt.gensalt())
bob_hash = bcrypt.hashpw(bob_password.encode(), bcrypt.gensalt())

print("Hash da senha da Alice:", alice_hash.decode())
print("Hash da senha do Bob:", bob_hash.decode())
