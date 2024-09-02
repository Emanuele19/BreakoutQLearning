from objects.slider import Slider
from control.abstractController import AbstractController
import configs
import pygame


class HumanController(AbstractController):
    def __init__(self):
        super().__init__()

    def run_game(self, action: Slider.Action = None) -> bool:
        result = self.__play()

        self.slider.draw(self.screen)
        self.ball.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}\nRews: {self.total_reward:.5f}", True, configs.WHITE)
        self.screen.blit(score_text, (configs.WIDTH - score_text.get_width() - 10, 10))

        pygame.display.flip()

        return result


    def __play(self):
        self.clock.tick(configs.PLAY_FPS)
        self.screen.fill(configs.BLACK)

        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.slider.move(self.slider.Action.LEFT)
        if keys[pygame.K_RIGHT]:
            self.slider.move(self.slider.Action.RIGHT)

        ball_state = self.ball.move()
        if self.ball.hits_the_ceiling():
            self.score += 1
        elif ball_state is False:
            return False

        return True
