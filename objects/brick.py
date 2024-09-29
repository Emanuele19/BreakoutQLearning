import pygame

import configs
from collisions.collidable import Collidable


class Brick(Collidable):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = configs.BLUE
        self.is_broken = False

    def draw(self, screen):
        if not self.is_broken:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))

    def reset(self):
        self.is_broken = False

    def brake(self):
        self.is_broken = True

    def get_boundaries(self) -> [float, float, float, float]:
        if not self.is_broken:
            return [self.x, self.y, self.w, self.h]
        else:
            return [-100, -100, 0, 0]

    def on_collision(self, other: 'Collidable') -> None:
        pass  # "brake" method called from "ball.py" to avoid circular imports