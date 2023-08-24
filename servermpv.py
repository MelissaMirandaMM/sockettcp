import socket
import threading

usuarios_registrados = {}
trava = threading.Lock()

def lidar_com_cliente(socket_cliente, endereco):
    try:
        while True:
            dados = socket_cliente.recv(1024).decode('utf-8')
            if not dados:
                break

            partes = dados.split('|')
            comando = partes[0]

            if comando == 'REGISTRAR':
                with trava:
                    nome_usuario = partes[1]
                    ip = partes[2]
                    usuarios_registrados[nome_usuario] = ip
                    socket_cliente.send("Registrado com sucesso.".encode('utf-8'))

            elif comando == 'OBTER_USUARIOS':
                with trava:
                    lista_usuarios = ", ".join(usuarios_registrados.keys())
                    socket_cliente.send(lista_usuarios.encode('utf-8'))

            elif comando == 'OBTER_IP':
                with trava:
                    usuario_alvo = partes[1]
                    ip_alvo = usuarios_registrados.get(usuario_alvo, "Usuário não encontrado.")
                    socket_cliente.send(ip_alvo.encode('utf-8'))

            elif comando == 'MENSAGEM':
                usuario_alvo = partes[1]
                mensagem = partes[2]
                ip_alvo = usuarios_registrados.get(usuario_alvo)
                if ip_alvo:
                    socket_alvo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket_alvo.connect((ip_alvo, 1997))
                    socket_alvo.send(mensagem.encode('utf-8'))
                    socket_alvo.close()
    except:
        pass
    finally:
        socket_cliente.close()

def principal():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('0.0.0.0', 2000))
    servidor.listen(5)

    print("Servidor conectado na porta 2000")

    while True:
        socket_cliente, endereco = servidor.accept()
        manipulador_cliente = threading.Thread(target=lidar_com_cliente, args=(socket_cliente, endereco))
        manipulador_cliente.start()

if __name__ == '__main__':
    principal()
