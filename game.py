from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.label import Label

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

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    
    game_ended = False

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        # print("update")
        self.ball.move()
        
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
            label = Label(text="Nigeria wins!", font_size='70sp', pos=(self.center_x, self.center_y + 20), color="green")
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
        if touch.x < self.width / 3 and not self.game_ended:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3 and not self.game_ended:
            self.player2.center_y = touch.y


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
