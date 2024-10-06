from control.abstractController import AbstractController
from objects.brick import Brick
from objects.ceiling import Ceiling
from objects.floor import Floor
from objects.slider import Slider
import configs


default_rewards = {
    "min_penalty": -10,
    "max_penalty": -100,
    "tick_penalty": -0.0001,
    "ceiling_penalty": -1,
    "bounce_reward": 1,
    "brick_reward": 10
}

class LearnerController(AbstractController):
    def __init__(self, rewards: dict = default_rewards):
        super().__init__()
        self.rewards = rewards

    def run_game(self, action: Slider.Action = None) -> bool:
        ret = self.__train(action=action)
        self.refresh()
        return ret

    def __train(self, action: Slider.Action):
        self.clock.tick(configs.TRAIN_FPS)
        self.screen.fill(configs.BLACK)

        self.slider.move(action)

        self.ball.move()
        # self.refresh()
        collider = self.collisionHandler.check_collision(self.ball)
        if isinstance(collider, Floor):
            distance = self.slider.x - self.ball.x if self.ball.x < self.slider.x else self.ball.x - self.slider.x + self.slider.width
            self.last_reward = max(self.rewards["min_penalty"], self.rewards["max_penalty"] * (float(distance) / configs.WIDTH))  # Penalty proportional to distance
            return False
        elif isinstance(collider, Slider):
            self.last_reward = self.rewards["bounce_reward"]
        elif isinstance(collider, Brick):
            self.last_reward = self.rewards["brick_reward"]
        elif isinstance(collider, Ceiling):
            self.last_reward = self.rewards["ceiling_penalty"]
        else:
            self.last_reward = self.rewards["tick_penalty"]

        self.total_reward += self.last_reward
        return True
