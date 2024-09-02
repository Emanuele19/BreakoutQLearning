from control.learnerController import LearnerController
from utils.singletonMeta import SingletonMeta
import pygame
import configs
from objects.ball import Ball
from objects.slider import Slider
from control.humanController import HumanController
import os

'''
This is the super class of "humanController" and "learnerController"
It will serve as factory based on the "human" and "training" parameters
'''


class MainController(metaclass=SingletonMeta):

    def __init__(self):
        pygame.init()
        self.__screen = pygame.display.set_mode((configs.WIDTH, configs.HEIGHT))
        self.__font = pygame.font.Font(None, 36)
        self.__clock = pygame.time.Clock()
        self.__slider = Slider()
        self.__ball = Ball()
        self.__score = 0
        self.__last_reward = 0
        self.__total_reward = 0
        pygame.display.set_caption("Brick Breaker")

    def get_instance(self, is_human=False) -> HumanController | LearnerController:
        if is_human:
            return HumanController()
        else:
            return LearnerController()

    def run_game(self, action: Slider.Action = None) -> bool:
        if self.__is_human:
            result = self.__play()
        else:
            if self.__is_training:
                result = self.__train(action)
            else:
                result = self.__play()

        self.__slider.draw(self.__screen)
        self.__ball.draw(self.__screen)

        score_text = self.__font.render(f"Score: {self.__score}\nRews: {self.__total_reward:.5f}", True, configs.WHITE)
        self.__screen.blit(score_text, (configs.WIDTH - score_text.get_width() - 10, 10))

        pygame.display.flip()

        return result

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

