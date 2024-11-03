from objects.ceiling import Ceiling
from objects.floor import Floor
from objects.slider import Slider
from control.abstractController import AbstractController
import configs
import pygame


class HumanController(AbstractController):
    def __init__(self):
        super().__init__()

    def run_game(self, action: Slider.Action = None) -> bool:
        result = self.__play()
        self.refresh()
        return result or super().is_ended()

    def __play(self):
        self.clock.tick(configs.PLAY_FPS)
        self.screen.fill(configs.BLACK)

        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.slider.move(self.slider.Action.LEFT)
        if keys[pygame.K_RIGHT]:
            self.slider.move(self.slider.Action.RIGHT)

        self.ball.move()
        collider = self.collisionHandler.check_collision(self.ball)
        if isinstance(collider, Floor):
            return False
        elif isinstance(collider, Ceiling):
            self.total_reward += 1

        return True
