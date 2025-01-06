from collections import deque
import random

class ReplayBuffer:
    """
    The replay buffer acts as a memory of experiences that the agent can sample from to learn.
    In theory, this should reduce the correlation between consecutive experiences making them more i.i.d.
    However, it is mostly used in deep reinforcement learning, does this mean that it is useless in this setting?
    We will see. :)
    """
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def add(self, experience):
        """Adds a new experience to the buffer"""
        self.buffer.append(experience)

    def sample(self, batch_size):
        """Returns a random sample of experiences from the buffer"""
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)
