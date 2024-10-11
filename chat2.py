from pymongo import MongoClient
import bcrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import datetime

# Conexão com o MongoDB
client = MongoClient("mongodb+srv://leticia23205:senhasecreta123@pychat.ckboi.mongodb.net/")
db = client.pychat
users_collection = db.users
messages_collection = db.messages

# Função para login do usuário
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if not user:
        print("Usuário não encontrado!")
        return None  # Retorna None se o usuário não for encontrado
    
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        print("Login bem-sucedido!")
        return username  # Retorna o nome de usuário se o login for bem-sucedido
    else:
        print("Senha incorreta!")
        return None

# Função para criptografar mensagens
def encrypt_message(message, key):
    iv = os.urandom(16)  # IV de 16 bytes para AES
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(message.encode()) + encryptor.finalize()
    return encrypted_message, iv

# Função para enviar mensagem criptografada
def send_message(sender, recipient, message, key):
    encrypted_message, iv = encrypt_message(message, key)
    
    # Inserir a mensagem no banco de dados
    result = messages_collection.insert_one({
        "sender": sender,
        "recipient": recipient,
        "message": encrypted_message.hex(),
        "iv": iv.hex(),
        "timestamp": datetime.datetime.utcnow()
    })
    
    print("Mensagem enviada! ID:", result.inserted_id)

# Função para descriptografar mensagens
def decrypt_message(encrypted_message, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(bytes.fromhex(encrypted_message)) + decryptor.finalize()
    return decrypted_message.decode()

# Função para ler mensagens
def read_messages(username, key):
    messages = messages_collection.find({"recipient": username})
    message_list = list(messages)  # Converte o cursor para uma lista
    if len(message_list) == 0:
        print("Nenhuma mensagem encontrada.")
    else:
        for message in message_list:
            decrypted_message = decrypt_message(message["message"], key, bytes.fromhex(message["iv"]))
            print(f"{message['sender']} disse: {decrypted_message}")

# Interface principal
def main():
    print("Bem-vindo ao PyChat Criptografado!")
    
    current_user = None  # Variável para armazenar o usuário logado

    while True:
        if current_user is None:
            print("\n1. Login")
            print("2. Sair")
            choice = input("Escolha uma opção: ")
            
            if choice == "1":
                username = input("Digite seu nome de usuário: ")
                password = input("Digite sua senha: ")
                current_user = login_user(username, password)  # Tenta logar
            elif choice == "2":
                print("Saindo...")
                break
        else:
            print("\n1. Ler mensagens")
            print("2. Enviar mensagem")
            print("3. Sair")
            choice = input("Escolha uma opção: ")
            
            if choice == "1":
                key = input("Digite a chave secreta para descriptografar suas mensagens: ").encode()
                read_messages(current_user, key)
            elif choice == "2":
                recipient = input("Para quem você quer enviar a mensagem? ")
                message = input("Digite sua mensagem: ")
                key = input("Digite a chave secreta (16 bytes): ").encode()
                if len(key) != 16:
                    print("A chave deve ter exatamente 16 bytes!")
                    continue
                send_message(current_user, recipient, message, key)
            elif choice == "3":
                print("Saindo...")
                current_user = None  # Resetar o usuário logado

if __name__ == "__main__":
    main()
