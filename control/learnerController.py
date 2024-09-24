from control.abstractController import AbstractController
from objects.slider import Slider
import configs


class LearnerController(AbstractController):
    def __init__(self):
        super().__init__()

    def run_game(self, action: Slider.Action = None):
        ret = self.__train(action=action)
        self.refresh()
        return ret

    def __train(self, action: Slider.Action):
        self.clock.tick(configs.TRAIN_FPS)
        self.screen.fill(configs.BLACK)

        self.slider.move(action)

        # Ball movement feedback
        in_game, hits_the_slider = self.ball.move()
        if hits_the_slider:
            self.score += 1
            self.last_reward = 1
        elif not in_game:  # Falls off
            self.last_reward = -100
            return False
        else:
            self.last_reward = 0

        self.total_reward += self.last_reward

        return True

    def __play(self):
        ...
