from utils.singletonMeta import SingletonMeta
import pygame
import configs
from objects.ball import Ball
from objects.slider import Slider
import os


class Controller(metaclass=SingletonMeta):

    def __init__(self, training=True):
        pygame.init()
        self.__screen = pygame.display.set_mode((configs.WIDTH, configs.HEIGHT))
        self.__font = pygame.font.Font(None, 36)
        self.__clock = pygame.time.Clock()
        self.__slider = Slider()
        self.__ball = Ball()
        self.__score = 0
        self.__last_reward = 0
        self.__total_reward = 0
        self.__is_training = training
        pygame.display.set_caption("Brick Breaker")

    def run_game(self, action: Slider.Action = None) -> bool:
        if self.__is_training:
            return self.__train(action)
        else:
            return self.__play()

    def reset(self):
        self.__ball = Ball()
        self.__slider.reset()
        self.__score = 0
        self.__total_reward = 0

    def get_game_state(self) -> (int, int, int, int, int):
        return (self.__ball.discrete_position[0], self.__ball.discrete_position[1],
                self.__ball.discrete_direction[1], self.__ball.discrete_direction[1],
                self.__slider.discrete_position)

    def get_reward(self) -> float:
        return self.__last_reward

    def get_total_reward(self) -> float:
        return self.__total_reward

    def __train(self, action: Slider.Action):
        self.__clock.tick(configs.TRAIN_FPS)
        self.__screen.fill(configs.BLACK)

        self.__slider.move(action)

        # Ball movement feedback
        ball_state = self.__ball.move()
        if ball_state is not None:
            if not ball_state:
                self.__last_reward = -100
                return False
            else:
                self.__score += 1
                self.__last_reward = 1
        else:
            self.__last_reward = -0.00001

        self.__total_reward += self.__last_reward

        # self.__slider.collide(self.__ball)

        self.__slider.draw(self.__screen)
        self.__ball.draw(self.__screen)

        score_text = self.__font.render(f"Score: {self.__score}\nRews: {self.__total_reward:.5f}", True, configs.WHITE)
        self.__screen.blit(score_text, (configs.WIDTH - score_text.get_width() - 10, 10))

        pygame.display.flip()

        return True

    def __play(self):
        self.__clock.tick(configs.PLAY_FPS)
        self.__screen.fill(configs.BLACK)

        ###########
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.__slider.move(self.__slider.Action.LEFT)
        if keys[pygame.K_RIGHT]:
            self.__slider.move(self.__slider.Action.RIGHT)

        ###########
        # Ball movement feedback
        ball_state = self.__ball.move()
        if ball_state is not None:
            if not ball_state:
                return False
            else:
                self.__score += 1


        self.__slider.collide(self.__ball)

        self.__slider.draw(self.__screen)
        self.__ball.draw(self.__screen)

        score_text = self.__font.render(f"Score: {self.__score}\nRews: {self.__total_reward:.5f}", True, configs.WHITE)
        self.__screen.blit(score_text, (configs.WIDTH - score_text.get_width() - 10, 10))

        pygame.display.flip()

        return True
