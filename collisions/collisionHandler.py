from collisions.collidable import Collidable
from utils.singletonMeta import SingletonMeta


class CollisionHandler(metaclass=SingletonMeta):
    def __init__(self, collidables: list[Collidable]):
        self.collidables = collidables

    ''' 
    Check if obj collides with another object, 
    if yes it calls the on_collision methods to both obj and the collider and returns the collider 
    '''
    def check_collision(self, obj: Collidable) -> Collidable | None:
        for collider in self.collidables:
            if collider is obj:
                continue
            if obj.is_colliding(collider):
                obj.on_collision(collider)
                collider.on_collision(obj)
                return collider
        return None