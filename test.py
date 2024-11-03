import os
import pickle
import time

import numpy as np
import pygame
from matplotlib import pyplot as plt

from control.controllerFactory import ControllerFactory

MAX_PLAYING_TIME = 3.6
MAX_FRAMES = 7200

def main():
    controller = ControllerFactory.get_instance(is_human=False)

    # Inizializzazione della tabella
    Q = load_table('tests/test13/Q_table.pkl')

    broken_bricks_tracking_list = []

    episodes = 100
    for episode in range(episodes):
        print(f"Running episode {episode + 1}")
        running = True
        controller.reset()
        start_time = time.time()
        frame_counter = 0
        while running:
            # 1. Osserva lo stato corrente
            state = controller.get_game_state()

            # 2. Scegli un'azione
            action = max(Q[state], key=Q[state].get)

            # 3. Esegui l'azione
            running = controller.run_game(action)
            frame_counter += 1
            if controller.is_ended():
                running = False
            elif frame_counter >= MAX_FRAMES:
                print(time.time() - start_time)
                return


        broken_bricks_tracking_list.append(controller.broken_bricks())

    report(broken_bricks_tracking_list, "trained_performances.png", "broken bricks", episodes)


def load_table(path='Q_table.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)

def report(parameter_list: list, filename: str, parameter_name: str, episodes: int):
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    plt.figure()
    plt.title(f"{parameter_name} ({episodes}) episodes")
    plt.ylabel(parameter_name)
    means_list = [np.mean(c) for c in chunks(parameter_list, 50)]
    x_means = np.arange(25, len(parameter_list), 50)
    plt.plot(parameter_list, marker='.')
    plt.plot(x_means, means_list, marker='x')
    plt.savefig(filename)
    plt.close()

if __name__ == '__main__':
    main()
