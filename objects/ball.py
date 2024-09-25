import pygame
import configs
import random
from objects.slider import Slider


class Ball:
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

        # Reference to the slider (singleton)
        self.slider_ref = Slider()

    '''
    Manages the ball movement and bouncing. It is to be called every frame
    :return False if the ball falls out of the screen, True otherwise as the first boolean and whether it is hitting the slider in that instant
    '''
    def move(self) -> (bool, bool):
        self.x += self.dx
        self.y += self.dy

        # Walls collision
        if self.x - self.radius <= 0 or self.x + self.radius >= configs.WIDTH:
            self.dx = -self.dx
        elif self.hits_the_ceiling():
            self.dy = -self.dy
        elif self.y + self.radius >= configs.HEIGHT:  # Falls off
            return False, False  # Signals the reset

        return True, self.hits_the_slider()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    # To make the Q-Learning algorithm work in a contiguous space, coordinates and direction are sampled.
    # Thus, the Q-table will contain a discrete number of "ranges" of coordinates and 4 possible values for direction
    # Note: actually neither position nor direction values belong to a contiguous space because floating point
    #       have a limited precision. This is one of the main limitations of Q-Learning

    @property
    def discrete_position(self) -> (int, int):
        dx = self.x // (configs.WIDTH // configs.SAMPLING_RATE)
        dy = self.y // (configs.HEIGHT // configs.SAMPLING_RATE)

        # Boundary escape prevention
        if dx >= 30:
            dx = 29

        if dy < 0:
            dy = 0

        return dx, dy

    @property
    def discrete_direction(self) -> (int, int):
        dx = -1 if self.dx < 0 else 1
        dy = -1 if self.dy < 0 else 1

        return dx, dy

    def hits_the_ceiling(self) -> bool:
        return self.y - self.radius <= 0

    def hits_the_slider(self) -> bool:
        if (self.y + self.radius >= self.slider_ref.y) and (
                self.slider_ref.x <= self.x <= self.slider_ref.x + self.slider_ref.width):
            # Calculate the bouncing angle based on the colliding area
            normalized_ball_x = self.x - self.slider_ref.x
            collision_section = int(normalized_ball_x // (self.slider_ref.width // 5))
            comps = self.bouncing_comps[collision_section]
            self.dx = self.velocity * comps[0]
            self.dy = self.velocity * comps[1] * -1
            self.y = self.slider_ref.y - self.radius - 1  # To prevent object intersection
            return True
        return False
