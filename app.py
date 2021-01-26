import numpy as np
import matplotlib.pyplot as plt
import time
from random import random, randint
import random
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.properties  import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line
from dqn import Dqn

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

last_x = 0
last_y = 0
n_points = 0
length = 0
brain = Dqn(5,3,0.9)
a_rotation = [0,20,-20]
last_reward = 0
scores = []
first_update = True

def init():
    global sand
    global goal_x
    global goal_y
    global first_update
    sand = np.zeros((longueur,largeur))
    goal_x = 20
    goal_y = largeur - 20
    first_update = False



class Car(Widget):
    angle = NumericProperty(0)
    rotation = NumericProperty(0)

    sensor1_x = NumericProperty(0)
    sensor1_y = NumericProperty(0)
    sensor1 = ReferenceListProperty(sensor1_x, sensor1_y)

    sensor2_x = NumericProperty(0)
    sensor2_y = NumericProperty(0)
    sensor2 = ReferenceListProperty(sensor2_x, sensor2_y)

    sensor3_x = NumericProperty(0)
    sensor3_y = NumericProperty(0)
    sensor3 = ReferenceListProperty(sensor3_x, sensor3_y)

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    signal1 = NumericProperty(0)
    signal2 = NumericProperty(0)
    signal3 = NumericProperty(0)

    def move(self, rotation):

        self.sensor1 = Vector(30, 0).rotate(self.angle) + self.pos
        self.sensor2 = Vector(30, 0).rotate((self.angle+30)%360) + self.pos
        self.sensor3 = Vector(30, 0).rotate((self.angle-30)%360) + self.pos

        self.signal1 = int(np.sum(sand[int(self.sensor1_x)-10:int(self.sensor1_x)+10, int(self.sensor1_y)-10:int(self.sensor1_y)+10]))/400.
        self.signal2 = int(np.sum(sand[int(self.sensor2_x)-10:int(self.sensor2_x)+10, int(self.sensor2_y)-10:int(self.sensor2_y)+10]))/400.
        self.signal3 = int(np.sum(sand[int(self.sensor3_x)-10:int(self.sensor3_x)+10, int(self.sensor3_y)-10:int(self.sensor3_y)+10]))/400.
        
        self.pos = Vector(*self.velocity) + self.pos
        self.rotation = rotation
        self.angle = self.angle + self.rotation
        
        if self.sensor1_x>longueur-10 or self.sensor1_x<10 or self.sensor1_y>largeur-10 or self.sensor1_y<10:
            self.signal1 = 2.
        if self.sensor2_x>longueur-10 or self.sensor2_x<10 or self.sensor2_y>largeur-10 or self.sensor2_y<10:
            self.signal2 = 2.
        if self.sensor3_x>longueur-10 or self.sensor3_x<10 or self.sensor3_y>largeur-10 or self.sensor3_y<10:
            self.signal3 = 2.

class Ball1(Widget):
    pass
class Ball2(Widget):
    pass
class Ball3(Widget):
    pass



last_distance = 0
class Game(Widget):

    car = Car()
    ball1 = Ball1()
    ball2 = Ball2()
    ball3 = Ball3()

    def serve_car(self):
        self.car.center = self.center
        self.car.velocity = Vector(3, 0)

    def update(self, dt):

        global goal_x
        global goal_y
        global longueur
        global largeur
        global brain
        global last_reward
        global scores
        global last_distance
       

        longueur = self.width
        largeur = self.height
        if first_update:
            self.steps = 0
            self.last_steps = 0
            init()

        xx = goal_x - self.car.x
        yy = goal_y - self.car.y
        orientation = Vector(*self.car.velocity).angle((xx,yy))/180.
        last_signal = [self.car.signal1, self.car.signal2, self.car.signal3, orientation, -orientation]
        action = brain.update(last_reward, last_signal)
        scores.append(brain.score())
        rotation = a_rotation[action]
        self.car.move(rotation)
        distance = np.sqrt((self.car.x - goal_x)**2 + (self.car.y - goal_y)**2)
        self.ball1.pos = self.car.sensor1
        self.ball2.pos = self.car.sensor2
        self.ball3.pos = self.car.sensor3
        self.steps += 1
        
        if sand[int(self.car.x),int(self.car.y)] > 0:
            self.car.velocity = Vector(1, 0).rotate(self.car.angle)
            last_reward = -8
        else: 
            self.car.velocity = Vector(6, 0).rotate(self.car.angle)
            last_reward = -0.3
            if distance < last_distance:
                last_reward = 0.3

        if self.car.x < 10:
            self.car.x = 10
            last_reward = -1.5
        if self.car.x > self.width - 10:
            self.car.x = self.width - 10
            last_reward = -1.5
        if self.car.y < 10:
            self.car.y = 10
            last_reward = -1.5
        if self.car.y > self.height - 10:
            self.car.y = self.height - 10
            last_reward = -1.5

        if distance < 100:
            goal_x = self.width-goal_x
            goal_y = self.height-goal_y
            last_reward = self.last_steps - self.steps 
            self.last_steps = self.steps 
            self.steps = 0
        last_distance = distance





class MyPaintWidget(Widget):
    def on_touch_down(self, touch):
        global length, n_points, last_x, last_y
        with self.canvas:
            Color(0.8,0.7,0)
            d = 10.
            touch.ud['line'] = Line(points = (touch.x, touch.y), width = 10)
            last_x = int(touch.x)
            last_y = int(touch.y)
            n_points = 0
            length = 0
            sand[int(touch.x),int(touch.y)] = 1

    def on_touch_move(self, touch):
        global length, n_points, last_x, last_y
        if touch.button == 'left':
            touch.ud['line'].points += [touch.x, touch.y]
            x = int(touch.x)
            y = int(touch.y)
            length += np.sqrt(max((x - last_x)**2 + (y - last_y)**2, 2))
            n_points += 1.
            density = n_points/(length)
            touch.ud['line'].width = int(20 * density + 1)
            sand[int(touch.x) - 10 : int(touch.x) + 10, int(touch.y) - 10 : int(touch.y) + 10] = 1
            last_x = x
            last_y = y



class CarApp(App):
    def build(self):
        game = Game()
        game.serve_car()

        Clock.schedule_interval(game.update, 1.0/120.0)
        self.painter = MyPaintWidget()

        save_btn = Button(text = 'save', pos = (game.width, 0))
        clear_btn = Button(text = 'clear')
        load_btn = Button(text = 'load', pos = (2 * game.width, 0))

        save_btn.bind(on_release = self.save)
        clear_btn.bind(on_release = self.clear_canvas)
        load_btn.bind(on_release = self.load)

        game.add_widget(self.painter)

        game.add_widget(clear_btn)
        game.add_widget(save_btn)
        game.add_widget(load_btn)
        return game

    def clear_canvas(self, obj):
        global sand
        self.painter.canvas.clear()
        sand = np.zeros((longueur,largeur))

    def save(self, obj):
        print("saving brain...")
        brain.save()
        plt.plot(scores)
        plt.show()

    def load(self, obj):
        print("loading last saved brain...")
        brain.load()

if __name__ == '__main__':
    CarApp().run()
