from collisions.collidable import Collidable


class SideWall(Collidable):
    def __init__(self, x, height):
        self.x = x
        self.height = height

    def get_boundaries(self) -> [float, float, float, float]:
        return [self.x, 0, 1, self.height]

    def on_collision(self, other: 'Collidable') -> None:
        pass