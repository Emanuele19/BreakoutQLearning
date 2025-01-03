import pygame
import configs
from enum import Enum

from collisions.collidable import Collidable

VELOCITY = 16

class Slider(Collidable):
    def __init__(self):
        self.width = configs.WIDTH // configs.SAMPLING_RATE * 3
        self.height = 10
        self.x = configs.WIDTH // 2 - self.width // 2
        self.y = configs.HEIGHT - 30
        self.dx = VELOCITY
        self.color = configs.WHITE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    class Action(Enum):
        IDLE = 0
        LEFT = -VELOCITY
        RIGHT = VELOCITY

    def move(self, direction: Action):
        self.x += direction.value

        # Screen boundaries
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > configs.WIDTH:
            self.x = configs.WIDTH - self.width

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (0,0,0), (self.x, self.y, 2, 2))

    def reset(self):
        self.x = configs.WIDTH // 2 - self.width // 2

    def get_boundaries(self) -> [float, float, float, float]:
        return [self.x, self.y, self.width, self.height]

    def on_collision(self, other: 'Collidable') -> None:
        pass

    @property
    def discrete_position(self) -> int:
        dx = self.x // (configs.WIDTH // configs.SAMPLING_RATE)
        return dx
