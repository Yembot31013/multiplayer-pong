from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.label import Label

import socket
import threading
import pickle
import time
import os

import numpy as np

game_state = {
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

server_state = {
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

playerProfile = None
client_socket = None
updating_state = False
start_in_center = False

class PongPaddle(Widget):
    score = NumericProperty(0)
    sources = ObjectProperty(None)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    
    old_pos_state = server_state["ball_position"]
    time_inbetween = 0
    
    def move(self):
        global last_state_changed
        
        self.pos = Vector(*self.velocity) + self.pos

        if playerProfile == "player1":
            game_state["ball_position"] = list(self.pos)
            game_state["ball_velocity"] = list(self.velocity)

        if server_state["ball_position"] != (0, 0) and self.old_pos_state != server_state["ball_position"]:
            self.pos = server_state["ball_position"]
            self.velocity = server_state["ball_velocity"]
            

        # server_pos = server_state["ball_position"] if server_state["ball_position"] != (
        #     0, 0) else self.center
        # pos_np = np.array(pos)
        # server_pos_np = np.array(server_pos)

        # difference = np.abs(pos_np - server_pos_np)
        # # difference = np.subtract(pos, server_pos)
        # print("position", list(pos_np))
        # print("server position", list(server_pos_np))
        # print("difference", list(difference))
        # if server_state["ball_position"] != (0, 0) and (difference > (200, 200)).any():
        #     print("update from server because:", list(difference))
        #     self.pos = server_state["ball_position"]
        #     # self.velocity = server_state["ball_velocity"]
        # else:
        #     self.pos = pos
        # self.pos = pos


class PongGame(Widget):
    def __init__(self, player_profile: str, client_socket, **kwargs):
        super().__init__(**kwargs)
        self.player_profile = player_profile
        self.client_socket = client_socket

    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    game_ended = False
    # player1_ready = False
    # player2_ready = False

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel
        
        # game_state["ball_position"] = list(self.center)
        # game_state["ball_velocity"] = vel

    def update(self, dt):
        label_text1 = "Nigeria Not Ready" if self.player_profile == "player2" else "We are waiting for you!!!"
        ready_label1 = Label(text=label_text1, font_size='20sp', pos=(
            self.center_x - 250, self.center_y), color="orange")

        label_text2 = "Cote d'ivoire Not Ready" if self.player_profile == "player1" else "We are waiting for you!!!"
        ready_label2 = Label(text=label_text2, font_size='20sp', pos=(
            self.center_x + 150, self.center_y), color="orange")

        # print("update")
        if game_state["gamestarted"] == True:
            self.game_ended = False
            if game_state["player1_ready"] and game_state["player2_ready"]:
                # self.remove_widget(ready_label1)
                # self.remove_widget(ready_label2)
                try:
                    self.ball.move()
                except TypeError:
                    print("error moving ball")
                    pass

        else:
            self.game_ended = True
            self.player1.center_y = self.center_y
            self.player2.center_y = self.center_y

            if game_state["player1_paddle_position"] != self.center_y:
                game_state["player1_paddle_position"] = self.center_y

            if game_state["player2_paddle_position"] != self.center_y:
                game_state["player2_paddle_position"] = self.center_y

        if self.player_profile == "player1":
            self.player2.center_y = game_state["player2_paddle_position"]
        elif self.player_profile == "player2":
            self.player1.center_y = game_state["player1_paddle_position"]

        if self.player1.score >= 10:
            # PLAYER 1 WINS
            self.serve_ball(vel=(0, 0))
            self.ball.center = self.center
            self.ball.velocity = (0, 0)
            self.ball.velocity_x = 0
            self.ball.velocity_y = 0
            self.player1.center_y = self.center_y
            self.player2.center_y = self.center_y
            self.game_ended = True
            # self.ball.pos = self.center

            # display the winner
            label = Label(text="Nigeria wins!", font_size='70sp', pos=(
                self.center_x, self.center_y + 20), color="green")
            self.add_widget(label)

        elif self.player2.score >= 10:
            # PLAYER 2 WINS
            self.serve_ball(vel=(0, 0))
            self.ball.center = self.center
            self.ball.velocity = (0, 0)
            self.ball.velocity_x = 0
            self.ball.velocity_y = 0
            self.player1.center_y = self.center_y
            self.player2.center_y = self.center_y
            self.game_ended = True
            # self.ball.pos = self.center

            # display the winner
            label = Label(text="Cote d'ivoire wins!",
                          font_size='70sp', pos=(self.center_x, self.center_y + 20), color="orange")
            self.add_widget(label)

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # went off to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.right > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))

    def on_touch_move(self, touch):

        if touch.x < self.width / 3 and not self.game_ended and self.player_profile == "player1":
            self.player1.center_y = touch.y
            game_state["player1_paddle_position"] = touch.y
            game_state["player1_ready"] = True
            # print("inside touch move 1", game_state["player1_paddle_position"])
            # print("no change", game_state==server_state)
        if touch.x > self.width - self.width / 3 and not self.game_ended and self.player_profile == "player2":
            self.player2.center_y = touch.y
            game_state["player2_paddle_position"] = touch.y
            game_state["player2_ready"] = True
            # print("inside touch move 2", game_state["player2_paddle_position"])

        # # send updated game state to server
        # self.client_socket.send(pickle.dumps(game_state))


class PongApp(App):
    def __init__(self, host, port, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.port = port
        self.player_profile = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            playerProfile = self.client_socket.recv(1024)
            self.player_profile = playerProfile.decode()
            print("Connected to server successfully as player", self.player_profile)
            threading.Thread(target=self.send_updates, daemon=True).start()
            threading.Thread(target=self.receive_updates, daemon=True).start()
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.client_socket.close()

    def receive_updates(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                game_state = pickle.loads(data, encoding="utf-8")
                # Update game state on client side
                self.update_game_state(game_state)
        except Exception as e:
            print(f"Error receiving updates from server: {e}")
            # self.client_socket.close()
            # exit()

    def send_updates(self):
        global updating_state
        try:
            while True:
                if server_state != game_state and not updating_state and game_state["gamestarted"] == True:
                    print("sending to server...")
                    new_data = game_state.copy()
                    if server_state["ball_position"] != game_state["ball_position"]:
                        new_data["player_profile"] = None
                    else:
                        new_data["player_profile"] = playerProfile

                    try:
                        self.client_socket.send(pickle.dumps(new_data))
                    except TypeError as e:
                        print(f"Error sending serialized data to client: {e}")
                        continue
                    self.update_game_state(game_state)
        except Exception as e:
            print(f"Error sending updates to server: {e}")

    def update_game_state(self, game_state_para: dict):
        global game_state, server_state, updating_state

        if game_state != game_state_para or server_state != game_state_para:
            updating_state = True
            # print(playerProfile, ":", game_state_para)

            if playerProfile == "player1":
                game_state["player2_paddle_position"] = game_state_para["player2_paddle_position"]
                game_state["player2_ready"] = game_state_para["player2_ready"]
            elif playerProfile == "player2":
                game_state["player1_paddle_position"] = game_state_para["player1_paddle_position"]
                game_state["player1_ready"] = game_state_para["player1_ready"]

            game_state["ball_position"] = game_state_para["ball_position"]
            game_state["ball_velocity"] = game_state_para["ball_velocity"]
            game_state["gamestarted"] = game_state_para["gamestarted"]

            server_state = game_state_para.copy()

            print("from receiving side:", server_state == game_state)
            # print(playerProfile, ":", game_state)
            # print(playerProfile, ":", server_state)
        time.sleep(0.2)
        updating_state = False

    def build(self):
        global playerProfile, client_socket, game_state
        self.connect_to_server()

        player_profile = self.player_profile
        client_socket = self.client_socket
        playerProfile = player_profile

        game = PongGame(player_profile, client_socket)
        game.serve_ball()

        Clock.schedule_interval(game.update, 1.0 / 600.0)
        # print(game_state)
        # if not os.path.exists("screenshot.png"):
        #     game.export_to_png("screenshot.png")

        self.title = "Nigeria" if playerProfile == "player1" else "Cote d'ivoire"
        return game


if __name__ == '__main__':
    PongApp('127.0.0.1', 5555).run()
