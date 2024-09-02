from control.controller import MainController
import pygame
import sys


def main():
    game = MainController().getInstance(is_human=True, is_training=False)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("pygame.QUIT")
                sys.exit(1)
        if not game.run_game():
            game.reset()


if __name__ == "__main__":
    main()
