from collisions.collidable import Collidable


class Floor(Collidable):
    def __init__(self, y, width):
        self.y = y
        self.width = width

    def get_boundaries(self) -> [float, float, float, float]:
        return [0, self.y, self.width, 10]

    def on_collision(self, other: 'Collidable') -> None:
        pass