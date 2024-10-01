import os
import pickle

import numpy as np
import pygame
from matplotlib import pyplot as plt

from control.controllerFactory import ControllerFactory

def main():
    controller = ControllerFactory.get_instance(is_human=False)

    # Inizializzazione della tabella
    Q = load_table()

    broken_bricks_tracking_list = []

    episode = 0
    while True:
        running = True
        controller.reset()
        while running:
            # 1. Osserva lo stato corrente
            state = controller.get_game_state()

            # 2. Scegli un'azione
            action = max(Q[state], key=Q[state].get)

            # 3. Esegui l'azione
            running = controller.run_game(action)

            if controller.is_ended():
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("pygame.QUIT")
                    report(broken_bricks_tracking_list, "performances.png", "rewards", episode)
                    os._exit(1)

        broken_bricks_tracking_list.append(controller.broken_bricks())

        if (episode + 1) % 100 == 0 and episode != 0:
            report(broken_bricks_tracking_list, "performances.png", "rewards", episode)
            return

        episode += 1


def load_table():
    with open('Q_table.pkl', 'rb') as f:
        return pickle.load(f)

def report(parameter_list: list, filename: str, parameter_name: str, episodes: int):
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    plt.figure()
    plt.title(f"{parameter_name} ({episodes+1}) episodes")
    plt.ylabel(parameter_name)
    means_list = [np.mean(c) for c in chunks(parameter_list, 50)]
    x_means = np.arange(25, len(parameter_list), 50)
    plt.plot(parameter_list, marker='.')
    plt.plot(x_means, means_list, marker='x')
    plt.savefig(filename)
    plt.close()

if __name__ == '__main__':
    main()
