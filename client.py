import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Entry, messagebox, simpledialog, END
import random

class AplicacaoChat:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicativo de Mensagens / CHAT Socket")
        self.nome_usuario_destino = ""
        self.socket_servidor = None

        self.ip_servidor = '127.0.0.1'
        self.porta_servidor = 2000
        self.nome_usuario = ""
        self.ip_usuario = ""

        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_cliente.connect((self.ip_servidor, self.porta_servidor))

        self.criar_widgets()

    def criar_widgets(self):
        self.label_info = tk.Label(self.root, text="Digite seu nome de usuário")
        self.label_info.pack(pady=10)

        self.entrada_nome_usuario = Entry(self.root)
        self.entrada_nome_usuario.pack()

        self.botao_registro = tk.Button(self.root, text="Registrar", command=self.registrar_usuario, bg="#4CAF50", fg="white", borderwidth=0, padx=10, pady=5, activebackground="#45a049")
        self.botao_registro.pack(pady=10)

        self.label_acao = tk.Label(self.root, text="Escolha uma ação:")
        self.label_acao.pack()

        self.botao_lista = tk.Button(self.root, text="Listar Usuários", command=self.obter_lista_usuarios, bg="#008CBA", fg="white", borderwidth=0, padx=10, pady=5, activebackground="#0073a8")
        self.botao_lista.pack(pady=5)

        self.botao_chat = tk.Button(self.root, text="Iniciar Chat", command=self.iniciar_chat, bg="#f44336", fg="white", borderwidth=0, padx=10, pady=5, activebackground="#d32f2f")
        self.botao_chat.pack(pady=5)

        self.botao_sair = tk.Button(self.root, text="Sair", command=self.root.quit, bg="#555", fg="white", borderwidth=0, padx=10, pady=5, activebackground="#444")
        self.botao_sair.pack(pady=20)

        self.divisor = tk.Label(self.root, text="-------------------------------")
        self.divisor.pack()

        self.texto_chat = scrolledtext.ScrolledText(self.root, state="disabled", height=10, width=50)
        self.texto_chat.pack(pady=10)

        self.divisor2 = tk.Label(self.root, text="-------------------------------")
        self.divisor2.pack()

        self.entrada_mensagem = Entry(self.root, width=40)
        self.entrada_mensagem.pack(pady=10)

        self.botao_enviar = tk.Button(self.root, text="Enviar", command=self.enviar_mensagem, bg="#4CAF50", fg="white", borderwidth=0, padx=10, pady=5, activebackground="#45a049")
        self.botao_enviar.pack()

    def registrar_usuario(self):
        self.nome_usuario = self.entrada_nome_usuario.get()
        # Gerar IP de usuário aleatório
        self.ip_usuario = f"127.0.0.{random.randint(1, 255)}"

        thread_registro = threading.Thread(target=self.thread_registro)
        thread_registro.start()

    def thread_registro(self):
        try:
            socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_cliente.connect((self.ip_servidor, self.porta_servidor))
            socket_cliente.send(f"REGISTRAR|{self.nome_usuario}".encode('utf-8'))  # Não envie mais o endereço IP
            resposta = socket_cliente.recv(1024).decode('utf-8')
            socket_cliente.close()

            self.mostrar_mensagem(resposta)
        except Exception as e:
            self.mostrar_mensagem(f"Erro durante o registro: {str(e)}")

    def obter_lista_usuarios(self):
        thread_lista_usuarios = threading.Thread(target=self.thread_lista_usuarios)
        thread_lista_usuarios.start()

    def thread_lista_usuarios(self):
        try:
            socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_cliente.connect((self.ip_servidor, self.porta_servidor))
            socket_cliente.send("OBTER_USUARIOS".encode('utf-8'))
            lista_usuarios = socket_cliente.recv(1024).decode('utf-8')
            socket_cliente.close()

            self.mostrar_mensagem(f"Usuários disponíveis: {lista_usuarios}")
            self.mostrar_mensagem(f"Seu IP: {self.ip_usuario}")
        except Exception as e:
            self.mostrar_mensagem(f"Erro ao obter lista de usuários: {str(e)}")

    def iniciar_chat(self):
        if self.socket_servidor is not None:
            self.socket_servidor.close()  # Encerre o soquete do servidor anterior, se existir

        target_username = simpledialog.askstring("Iniciar Chat", "Digite o nome de usuário do usuário com quem deseja conversar:")
        if not target_username:
            return

        target_ip = self.obter_ip_usuario(target_username)
        if target_ip == "Usuário não encontrado.":
            self.mostrar_mensagem("Usuário não encontrado.")
            return

        self.nome_usuario_destino = target_username  # Atribua o nome do usuário de destino

        # Crie um novo soquete do servidor para o chat
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_servidor.bind((self.ip_usuario, 1997))
        self.socket_servidor.listen(1)

        threading.Thread(target=self.receber_mensagens, args=(target_ip,)).start()

        self.mostrar_mensagem(f"Iniciando chat com {target_username}")


    def obter_ip_usuario(self, nome_usuario_destino):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.ip_servidor, self.porta_servidor))
            client_socket.send(f"OBTER_IP|{nome_usuario_destino}".encode('utf-8'))
            target_ip = client_socket.recv(1024).decode('utf-8')
            client_socket.close()
            return target_ip
        except Exception as e:
            return None  # Retornar None em caso de erro


    def enviar_mensagem(self):
        mensagem = self.entrada_mensagem.get()
        self.entrada_mensagem.delete(0, END)

        thread_envio = threading.Thread(target=self.thread_envio, args=(self.nome_usuario_destino, mensagem))  
        thread_envio.start()

    def thread_envio(self, nome_usuario_destino, mensagem):  
        try:
            ip_destino = self.obter_ip_usuario(nome_usuario_destino)
            if ip_destino == "Usuário não encontrado.":
                self.mostrar_mensagem("Usuário não encontrado.")
                return

            # Use o soquete de cliente criado no início para enviar mensagens
            self.socket_cliente.send(f"MENSAGEM|{mensagem}".encode('utf-8'))
        except Exception as e:
            self.mostrar_mensagem(f"Erro ao enviar mensagem: {str(e)}")

    def receber_mensagens(self, meu_ip):
        socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        socket_servidor.bind((meu_ip, 2000))
        socket_servidor.listen(1)

        while True:
            socket_cliente, endereco_cliente = socket_servidor.accept()
            mensagem = socket_cliente.recv(1024).decode('utf-8')
            if not mensagem:
                break
            self.mostrar_mensagem(mensagem)
            socket_cliente.close()

    def mostrar_mensagem(self, mensagem):
        self.texto_chat.config(state="normal")
        self.texto_chat.insert("end", mensagem + "\n")
        self.texto_chat.config(state="disabled")

    def __del__(self):
        # Encerre o soquete de cliente ao sair do programa
        self.socket_cliente.close()

if __name__ == "__main__":
    raiz = tk.Tk()
    app = AplicacaoChat(raiz)
    raiz.mainloop()