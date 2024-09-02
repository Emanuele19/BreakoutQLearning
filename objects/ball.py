import pygame
import configs
import random
from objects.slider import Slider
import math


class Ball:
    def __init__(self):
        self.radius = 10
        self.x = configs.WIDTH // 2
        self.y = configs.HEIGHT // 2
        # Componenti del vettore direzione per le 5 sezioni dì collisione dello slider
        self.bouncing_comps = [(-0.7, 0.7), (-0.2, 0.9), (0, 1), (0.2, 0.9), (0.7, 0.7)]
        self.velocity = 8
        velocity_vector = random.choice(self.bouncing_comps)
        self.dx = self.velocity * velocity_vector[0]
        self.dy = -self.velocity * velocity_vector[1]
        self.color = configs.RED
        self.SAMPLING_RATE = 10
        self.slider_ref = Slider()

    # Ritorna True se tocca il soffitto, False se cade e None per ogni altro evento
    def move(self) -> bool | None:
        self.x += self.dx
        self.y += self.dy

        # Collisione con i bordi
        if self.x - self.radius <= 0 or self.x + self.radius >= configs.WIDTH:
            self.dx = -self.dx
        elif self.y - self.radius <= 0:  # Punto guadagnato
            self.dy = -self.dy
            return True
        elif self.y + self.radius >= configs.HEIGHT:  # Palla persa
            return False  # Segnale per reset
        self.__collision_with_slider()
        return None

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    @property
    def discrete_position(self) -> (int, int):
        dx = self.x // (configs.WIDTH // configs.SAMPLING_RATE)
        dy = self.y // (configs.HEIGHT // configs.SAMPLING_RATE)

        return dx, dy

    @property
    def discrete_direction(self) -> (int, int):
        dx = -1 if self.dx < 0 else 1
        dy = -1 if self.dy < 0 else 1

        return dx, dy

    def __collision_with_slider(self):
        if (self.y + self.radius >= self.slider_ref.y) and (
                self.slider_ref.x <= self.x <= self.slider_ref.x + self.slider_ref.width):
            # Calcolo della velocità x e y sulla base della zona dello slider colpita
            normalized_ball_x = self.x - self.slider_ref.x
            collision_section = int(normalized_ball_x // (self.slider_ref.width // 5))
            comps = self.bouncing_comps[collision_section]
            self.dx = self.velocity * comps[0]
            self.dy = self.velocity * comps[1] * -1
            self.y = self.slider_ref.y - self.radius - 10  # Collision check

            print(f"{collision_section=} {self.dx=} {self.dy=}")
