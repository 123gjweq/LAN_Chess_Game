import socket
from threaded_client import ThreadedClient
from server_data import ServerData


TEMPIP = "192.168.1.121"
PORT = 24635



#initializes a server using TCP, listens for any clients connecting
def main():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
		tcp_socket.bind((TEMPIP, PORT))
		data = ServerData()

		while True:
			tcp_socket.listen()
			ThreadedClient(tcp_socket.accept(), data)

if __name__ == "__main__":
	main()