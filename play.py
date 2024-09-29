from control.controllerFactory import ControllerFactory
import pygame
import sys


def main():
    game = ControllerFactory.get_instance(is_human=True)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("pygame.QUIT")
                sys.exit(1)
        if not game.run_game():
            game.reset()


if __name__ == "__main__":
    main()
