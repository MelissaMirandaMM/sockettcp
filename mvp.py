import socket
import threading

def registrar_usuario(ip_servidor, porta_servidor, nome_usuario, ip_usuario):
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_cliente.connect((ip_servidor, porta_servidor))
    socket_cliente.send(f"REGISTRAR|{nome_usuario}|{ip_usuario}".encode('utf-8'))
    resposta = socket_cliente.recv(1024).decode('utf-8')
    print(resposta)
    socket_cliente.close()

def obter_lista_usuarios(ip_servidor, porta_servidor):
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_cliente.connect((ip_servidor, porta_servidor))
    socket_cliente.send("OBTER_USUARIOS".encode('utf-8'))
    lista_usuarios = socket_cliente.recv(1024).decode('utf-8')
    print(f"Usuários disponíveis: {lista_usuarios}")
    socket_cliente.close()

def obter_ip_usuario(ip_servidor, porta_servidor, nome_usuario_destino):
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_cliente.connect((ip_servidor, porta_servidor))
    socket_cliente.send(f"OBTER_IP|{nome_usuario_destino}".encode('utf-8'))
    ip_destino = socket_cliente.recv(1024).decode('utf-8')
    socket_cliente.close()
    return ip_destino

def enviar_mensagem(ip_destino, mensagem):
    socket_destino = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_destino.connect((ip_destino, 1997))
    socket_destino.send(f"MENSAGEM|{mensagem}".encode('utf-8'))
    socket_destino.close()

def receber_mensagens(ip_usuario):
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_servidor.bind((ip_usuario, 1997))
    socket_servidor.listen(1)

    while True:
        socket_cliente, endereco_cliente = socket_servidor.accept()
        mensagem = socket_cliente.recv(1024).decode('utf-8')
        if not mensagem:
            break
        print(mensagem)
        socket_cliente.close()

def principal():
    ip_servidor = '127.0.0.1'
    porta_servidor = 1997

    nome_usuario = input("Digite seu nome de usuário: ")
    ip_usuario = input("Digite seu endereço IP: ")

    registrar_usuario(ip_servidor, porta_servidor, nome_usuario, ip_usuario)

    while True:
        acao = input("Digite 'lista' para ver os usuários disponíveis, 'chat' para iniciar um chat ou 'sair' para sair: ")

        if acao == 'lista':
            obter_lista_usuarios(ip_servidor, porta_servidor)
        elif acao == 'chat':
            nome_usuario_destino = input("Digite o nome de usuário do usuário com quem deseja conversar: ")
            ip_destino = obter_ip_usuario(ip_servidor, porta_servidor, nome_usuario_destino)
            if ip_destino == "Usuário não encontrado.":
                print("Usuário não encontrado.")
                continue

            print(f"Iniciando chat com {nome_usuario_destino}")
            threading.Thread(target=receber_mensagens, args=(ip_usuario,)).start()

            while True:
                mensagem = input(f"{nome_usuario}: ")
                if mensagem.lower() == 'sair':
                    break
                enviar_mensagem(ip_destino, f"{nome_usuario}: {mensagem}")
        elif acao == 'sair':
            break

if __name__ == '__main__':
    principal()
