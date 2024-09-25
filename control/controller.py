from control.abstractController import AbstractController
from control.learnerController import LearnerController
from utils.singletonMeta import SingletonMeta
from control.humanController import HumanController

'''
This class serves as factory for HumanController (used for testing functionalities)
and LearnerController (used for training and post-training model testing).
'''

class ControllerFactory(metaclass=SingletonMeta):

    @staticmethod
    def get_instance(is_human=False) -> AbstractController:
        if is_human:
            return HumanController()
        else:
            return LearnerController()
