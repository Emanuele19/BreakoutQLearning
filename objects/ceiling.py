from collisions.collidable import Collidable


class Ceiling(Collidable):
    def __init__(self, w: float):
        self.width = w

    def get_boundaries(self) -> [float, float, float, float]:
        return [0, 0, self.width, 1]

    def on_collision(self, other: 'Collidable') -> None:
        pass
