import pygame
import configs
import random

from collisions.collidable import Collidable
from objects.brick import Brick
from objects.ceiling import Ceiling
from objects.sideWall import SideWall
from objects.slider import Slider


class Ball(Collidable):
    def __init__(self):
        # Basic properties
        self.radius = 10
        self.x = configs.WIDTH // 2
        self.y = configs.HEIGHT // 2
        self.velocity = 8
        self.color = configs.RED

        # The ball can hit the slider in 5 different sections that determine the ball bouncing angle
        self.bouncing_comps = [(-0.7, 0.7), (-0.2, 0.9), (0, 1), (0.2, 0.9), (0.7, 0.7)]
        self.starting_bouncing_comps = [(-0.7, 0.7), (-0.2, 0.9), (0.2, 0.9), (0.7, 0.7)]
        velocity_vector = random.choice(self.starting_bouncing_comps)
        self.dx = self.velocity * velocity_vector[0]
        self.dy = -self.velocity * velocity_vector[1]


    '''
    Manages the ball movement and bouncing. It is to be called every frame
    :return False if the ball falls out of the screen, True otherwise as the first boolean and whether it is hitting the slider in that instant
    '''
    def move(self) -> None:
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def get_boundaries(self) -> [float, float, float, float]:
        return [self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2]

    def on_collision(self, other: 'Collidable') -> None:
        if isinstance(other, SideWall):
            if self.x < configs.HEIGHT // 2:
                self.dx = -self.dx
                self.x = self.radius + 1
            else:
                self.dx = -self.dx
                self.x = configs.WIDTH - 1 - self.radius
        elif isinstance(other, Slider):
            if other.x <= self.x <= other.x + other.width:
                normalized_ball_x = self.x - other.x
                collision_section = int(normalized_ball_x // (other.width // 5))
                if collision_section < 0: collision_section = 0
                comps = self.bouncing_comps[collision_section]
                self.dx = self.velocity * comps[0]
                self.dy = self.velocity * comps[1] * -1
                self.y = other.y - self.radius - 1
            else:
                self.dx = -self.dx
        elif isinstance(other, Ceiling):
            self.dy = -self.dy
            self.y = self.radius + 1
        elif isinstance(other, Brick):
            if not other.is_broken:
                if other.x <= self.x <= other.x + other.w:
                    self.dy = -self.dy
                    self.y += 1
                else:
                    self.dx = -self.dx
                other.brake()

    # To make the Q-Learning algorithm work in a contiguous space, coordinates and direction are sampled.
    # Thus, the Q-table will contain a discrete number of "ranges" of coordinates and 4 possible values for direction
    # Note: actually neither position nor direction values belong to a contiguous space because floating point
    #       have a limited precision. This is one of the main limitations of Q-Learning

    @property
    def discrete_position(self) -> (int, int):
        if self.x < 0: self.x = 0
        if self.y < 0: self.y = 0
        if self.x > configs.WIDTH: self.x = configs.WIDTH
        if self.y > configs.HEIGHT: self.y = configs.HEIGHT

        dx = self.x // (configs.WIDTH // configs.SAMPLING_RATE)
        dy = self.y // (configs.HEIGHT // configs.SAMPLING_RATE)

        # Boundary escape prevention
        if dx >= 30:
            dx = 29

        if dy >= 30:
            dy = 29

        if dy < 0:
            dy = 1

        if dx < 0:
            dx = 0

        return dx, dy

    @property
    def discrete_direction(self) -> (int, int):
        dx = -1 if self.dx < 0 else 1
        dy = -1 if self.dy < 0 else 1

        return dx, dy
