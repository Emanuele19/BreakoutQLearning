from abc import ABC, abstractmethod


class Collidable(ABC):
    @abstractmethod
    def get_boundaries(self) -> [float, float, float, float]:
        raise NotImplementedError

    @abstractmethod
    def on_collision(self, other: 'Collidable') -> None:
        raise NotImplementedError

    def is_colliding(self, other: 'Collidable') -> bool:
        x1, y1, w1, h1 = self.get_boundaries()
        x2, y2, w2, h2 = other.get_boundaries()
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2
