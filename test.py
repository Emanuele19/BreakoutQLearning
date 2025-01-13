import os
import pickle
import random
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
    test_id = 35
    Q1, Q2 = load_tables(f'tests/test{test_id}')

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
            s1 = Q1[state]
            s2 = Q2[state]
            Q_combined = {action: s1[action] + s2[action] for action in s1}

            action = max(Q_combined, key=Q_combined.get)

            # 3. Esegui l'azione
            running = controller.run_game(action)
            frame_counter += 1
            if controller.is_ended():
                running = False
            elif frame_counter >= MAX_FRAMES:
                print(time.time() - start_time)
                return


        broken_bricks_tracking_list.append(controller.broken_bricks())

    report(broken_bricks_tracking_list, f"tests/test{test_id}/trained_performances.png", "broken bricks", episodes)


def load_tables(path1:str):
    with open(path1 + "/Q1.pkl", 'rb') as f:
        q1 = pickle.load(f)

    with open(path1 + "/Q2.pkl", 'rb') as f:
        q2 = pickle.load(f)

    return q1, q2

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
