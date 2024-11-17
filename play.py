from control.controllerFactory import ControllerFactory
import pygame
import sys
import time


def main():
    game = ControllerFactory.get_instance(is_human=True)
    frame_counter = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("pygame.QUIT")
                print(frame_counter)
                sys.exit()
        if not game.run_game():
            game.reset()

        frame_counter += 1
        if frame_counter % 50 == 0:
            print(".")


if __name__ == "__main__":
    main()
