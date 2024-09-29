import pygame
import configs
from collisions.collisionHandler import CollisionHandler
from objects.brick import Brick
from objects.ceiling import Ceiling
from objects.floor import Floor
from objects.sideWall import SideWall
from objects.slider import Slider
from objects.ball import Ball
from abc import ABC, abstractmethod


class AbstractController(ABC):

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((configs.WIDTH, configs.HEIGHT))
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.slider = Slider()
        self.ball = Ball()
        self.ceiling = Ceiling(configs.WIDTH)
        self.floor = Floor(configs.HEIGHT, configs.WIDTH)
        self.leftWall = SideWall(1, configs.HEIGHT)
        self.rightWall = SideWall(configs.WIDTH - 1, configs.HEIGHT)
        self.bricks = [Brick(x, 0, configs.WIDTH // configs.SAMPLING_RATE, 20) for x in range(0, configs.WIDTH, configs.SAMPLING_RATE)]
        self.collisionHandler = CollisionHandler([
            self.ball,
            self.slider,
            self.ceiling,
            self.floor,
            self.leftWall,
            self.rightWall
        ] + self.bricks)
        self.score = 0
        self.last_reward = 0
        self.total_reward = 0
        pygame.display.set_caption("Brick Breaker")

    @abstractmethod
    def run_game(self, action: Slider.Action = None) -> bool:
        raise NotImplementedError

    def refresh(self) -> None:
        self.slider.draw(self.screen)
        self.ball.draw(self.screen)
        for brick in self.bricks: brick.draw(self.screen)

        score_text = self.font.render(f"Rewards: {self.total_reward}", True, configs.WHITE)
        self.screen.blit(score_text, (configs.WIDTH - score_text.get_width() - 10, 10))

        pygame.display.flip()

    def reset(self):
        self.ball = Ball()
        self.slider.reset()
        self.score = 0
        self.total_reward = 0
        for brick in self.bricks:
            brick.reset()

    def get_game_state(self) -> (int, int, int, int, int):
        return (self.ball.discrete_position[0], self.ball.discrete_position[1],
                self.ball.discrete_direction[1], self.ball.discrete_direction[1],
                self.slider.discrete_position)

    def get_reward(self) -> float:
        return self.last_reward

    def get_total_reward(self) -> float:
        return self.total_reward
