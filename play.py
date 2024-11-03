from control.controllerFactory import ControllerFactory
import pygame
import sys
import time


def main():
    game = ControllerFactory.get_instance(is_human=True)
    playing_time_list = []
    won_time_list = []
    start = time.perf_counter()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("pygame.QUIT")
                print(won_time_list)
                sys.exit()
        if not game.run_game():
            elapsed = time.perf_counter() - start
            playing_time_list.append(elapsed)
            if game.is_ended():
                won_time_list.append(elapsed)
            start = time.perf_counter()
            game.reset()
            print(elapsed)


if __name__ == "__main__":
    main()
