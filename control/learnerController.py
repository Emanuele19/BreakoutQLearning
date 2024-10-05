from control.abstractController import AbstractController
from objects.brick import Brick
from objects.ceiling import Ceiling
from objects.floor import Floor
from objects.slider import Slider
import configs


MIN_PENALTY = -10
MAX_PENALTY = -100
TICK_PENALTY = -0.0001
CEILING_PENALTY = -1
BOUNCE_REWARD = 1
BRICK_REWARD = 10


class LearnerController(AbstractController):
    def __init__(self):
        super().__init__()

    def run_game(self, action: Slider.Action = None) -> bool:
        ret = self.__train(action=action)
        # self.refresh()
        return ret

    def __train(self, action: Slider.Action):
        self.clock.tick(configs.TRAIN_FPS)
        self.screen.fill(configs.BLACK)

        self.slider.move(action)

        self.ball.move()
        self.refresh()
        collider = self.collisionHandler.check_collision(self.ball)
        if isinstance(collider, Floor):
            distance = self.slider.x - self.ball.x if self.ball.x < self.slider.x else self.ball.x - self.slider.x + self.slider.width
            self.last_reward = max(MIN_PENALTY, MAX_PENALTY * (float(distance) / configs.WIDTH))  # Penalty proportional to distance
            return False
        elif isinstance(collider, Slider):
            self.last_reward = BOUNCE_REWARD
        elif isinstance(collider, Brick):
            self.last_reward = BRICK_REWARD
        elif isinstance(collider, Ceiling):
            self.last_reward = CEILING_PENALTY
        else:
            self.last_reward = TICK_PENALTY

        self.total_reward += self.last_reward
        return True
