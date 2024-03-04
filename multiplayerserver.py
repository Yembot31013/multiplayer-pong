import socket
import threading
import pickle


class PongServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.game_state = {
            "player1_score": 0,
            "player2_score": 0,
            "ball_position": (0, 0),
            "ball_velocity": (0, 0),
            "player1_paddle_position": 0,
            "player2_paddle_position": 0,
            "gamestarted": False,
            "player1_ready": False,
            "player2_ready": False,
        }

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)
        print(f"Server is listening on {self.host}:{self.port}")
        while len(self.connections) < 2:
          self.accept_connections()
        else:
          self.game_state["gamestarted"] = True
          # Send updated game state to all clients
          self.broadcast_game_state()
          print("connected to two clients!!!")
          print("game started!!!")

    def accept_connections(self):       
      client_socket, client_address = self.server_socket.accept()
      print(f"Connection from {client_address}")
      self.connections.append(client_socket)
      client_socket.send(f"player{len(self.connections)}".encode())
      threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                client_data = pickle.loads(data)
                print("receieved data from client")
                # Update game state based on client data
                self.update_game_state(client_data)
                # Send updated game state to all clients
                self.broadcast_game_state()
        except Exception as e:
            print(f"Error handling client: {e}")
            self.connections.remove(client_data)
        finally:
            client_socket.close()
            self.connections.remove(client_socket)

    def update_game_state(self, client_data):
        # Update game state based on client data
        # Example: player1_score = client_data['player1_score']
        self.game_state["player1_score"] = client_data.get("player1_score", self.game_state["player1_score"])
        self.game_state["player2_score"] = client_data.get("player2_score", self.game_state["player2_score"])
        self.game_state["ball_position"] = client_data.get("ball_position", self.game_state["ball_position"])
        self.game_state["ball_velocity"] = client_data.get("ball_velocity", self.game_state["ball_velocity"])
        self.game_state["player1_paddle_position"] = client_data.get("player1_paddle_position", self.game_state["player1_paddle_position"])
        self.game_state["player2_paddle_position"] = client_data.get("player2_paddle_position", self.game_state["player2_paddle_position"])
        self.game_state["gamestarted"] = client_data.get("gamestarted", self.game_state["gamestarted"])
        self.game_state["player1_ready"] = client_data.get("player1_ready", self.game_state["player1_ready"])
        self.game_state["player2_ready"] = client_data.get("player2_ready", self.game_state["player2_ready"])

    def broadcast_game_state(self):
        serialized_data = pickle.dumps(self.game_state)
        for connection in self.connections:
            connection.send(serialized_data)


if __name__ == "__main__":
    # You can change the IP and port as needed
    server = PongServer('127.0.0.1', 5555)
    server.start()
