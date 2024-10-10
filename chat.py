from pymongo import MongoClient
import bcrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import datetime

# Conexão com o MongoDB
try:
    client = MongoClient("mongodb+srv://leticia23205:senhasecreta123@pychat.ckboi.mongodb.net/")
    db = client.pychat
    users_collection = db.users
    messages_collection = db.messages
    print("Conexão com o MongoDB estabelecida com sucesso.")
except Exception as e:
    print("Erro ao conectar ao MongoDB:", e)

# Função para login do usuário
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if not user:
        print("Usuário não encontrado!")
        return False
    
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        print("Login bem-sucedido!")
        return True
    else:
        print("Senha incorreta!")
        return False

# Função para criptografar mensagens
def encrypt_message(message, key):
    iv = os.urandom(16)  # IV de 16 bytes para AES
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(message.encode()) + encryptor.finalize()
    return encrypted_message, iv

# Função para enviar mensagem criptografada
def send_message(sender, recipient, message, key):
    try:
        encrypted_message, iv = encrypt_message(message, key)
        
        # Inserir a mensagem no banco de dados
        result = messages_collection.insert_one({
            "sender": sender,
            "recipient": recipient,
            "message": encrypted_message.hex(),
            "iv": iv.hex(),
            "timestamp": datetime.datetime.utcnow()
        })
        
        print("Mensagem enviada! ID:", result.inserted_id)  # Exibe o ID do documento inserido
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

# Função para descriptografar mensagens
def decrypt_message(encrypted_message, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(bytes.fromhex(encrypted_message)) + decryptor.finalize()
    return decrypted_message.decode()

# Função para ler mensagens
def read_messages(username, key):
    try:
        messages = messages_collection.find({"recipient": username})
        for message in messages:
            decrypted_message = decrypt_message(message["message"], key, bytes.fromhex(message["iv"]))
            print(f"{message['sender']} disse: {decrypted_message}")
    except Exception as e:
        print("Erro ao ler mensagens:", e)

# Interface principal
def main():
    print("Bem-vindo ao PyChat Criptografado!")
    
    while True:
        print("\n1. Login")
        print("2. Enviar mensagem")
        print("3. Ler mensagens")
        print("4. Sair")
        
        choice = input("Escolha uma opção: ")
        
        if choice == "1":
            username = input("Digite seu nome de usuário: ")
            password = input("Digite sua senha: ")
            if login_user(username, password):
                print("Login realizado com sucesso!")
        
        elif choice == "2":
            sender = input("Quem está enviando a mensagem? ")
            recipient = input("Para quem você quer enviar a mensagem? ")
            message = input("Digite sua mensagem: ")
            key = input("Digite a chave secreta (16 bytes): ").encode()  # Chave compartilhada verbalmente
            
            if len(key) != 16:
                print("A chave deve ter exatamente 16 bytes!")
                continue
            
            send_message(sender, recipient, message, key)
        
        elif choice == "3":
            username = input("Digite seu nome de usuário: ")
            key = input("Digite a chave secreta para descriptografar suas mensagens: ").encode()
            
            if len(key) != 16:
                print("A chave deve ter exatamente 16 bytes!")
                continue
            
            read_messages(username, key)
        
        elif choice == "4":
            print("Saindo...")
            break

if __name__ == "__main__":
    main()
