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
        self.floor = Floor(self.slider.y, configs.WIDTH)
        self.leftWall = SideWall(1, configs.HEIGHT)
        self.rightWall = SideWall(configs.WIDTH - 1, configs.HEIGHT)
        self.bricks = self.__create_bricks()
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
        # self.draw_grid()
        self.slider.draw(self.screen)
        self.ball.draw(self.screen)
        for brick in self.bricks:
            brick.draw(self.screen)

        score_text = self.font.render(f"Rewards: {self.total_reward:.4f}", True, configs.WHITE)
        self.screen.blit(score_text, (configs.WIDTH - score_text.get_width() - 10, 10))

        pygame.display.flip()

    def reset(self):
        self.ball = Ball()
        self.slider.reset()
        self.score = 0
        self.total_reward = 0
        for brick in self.bricks:
            brick.reset()

    def get_game_state(self) -> (int, int, int, list[bool]):
        return (self.ball.discrete_position,
                self.ball.discrete_direction,
                self.slider.discrete_position,
                self.brick_map())

    def get_reward(self) -> float:
        return self.last_reward

    def get_total_reward(self) -> float:
        return self.total_reward

    # TODO: migliora, è inefficiente
    def is_ended(self):
        return all(brick.is_broken for brick in self.bricks)

    def broken_bricks(self):
        return len([brick for brick in self.bricks if brick.is_broken])

    def brick_map(self) -> tuple[bool]:
        """
        Returns the status of the bricks in the game
        :return: list of boolean values, where True means the brick is in game.
        """
        return tuple(not brick.is_broken for brick in self.bricks)


    def __create_bricks(self, n:int = configs.SAMPLING_RATE, l:int = 1) -> list[Brick]:
        """
        Creates a cluster of n*l bricks, where n is the number of bricks per line and l is the number of lines
        """
        brick_height = configs.HEIGHT // configs.SAMPLING_RATE
        out = []
        for i in range(l):
            # Every discretion cell (SAMPLING_RATE parameter) must have at most one brick with width = WIDTH // SAMPLING_RATE
            out += [Brick(x, (brick_height+5)*i, configs.WIDTH // n * 2, brick_height) for x in range(0, configs.WIDTH, configs.WIDTH // n * 2)]
        return out

    def draw_grid(self) -> None:
        '''
        Draws a grid where every cell is WIDTH // SAMPLING_RATE pixels wide and HEIGHT // SAMPLING_RATE pixels tall
        Useful to visualize the discretion of the state space
        '''
        for x in range(0, configs.WIDTH, configs.WIDTH // configs.SAMPLING_RATE):
            pygame.draw.line(self.screen, configs.WHITE, (x, 0), (x, configs.HEIGHT))
        for y in range(0, configs.HEIGHT, configs.HEIGHT // configs.SAMPLING_RATE):
            pygame.draw.line(self.screen, configs.WHITE, (0, y), (configs.WIDTH, y))