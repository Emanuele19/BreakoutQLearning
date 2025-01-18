import os
import pickle
import random
import time

import numpy as np
import re
import pygame
from matplotlib import pyplot as plt

from control.controllerFactory import ControllerFactory
from collections import defaultdict

MAX_PLAYING_TIME = 3.6
MAX_FRAMES = 7200

def main():
    controller = ControllerFactory.get_instance(is_human=False)

    # Inizializzazione della tabella
    test_id = 39

    test_path = f'tests/test{test_id}'
    Q_tables = [f for f in os.listdir(test_path) if re.match(r'Q\d-\d+k\.pkl', f)]

    # Dizionario per raggruppare i file per ID
    groups = defaultdict(list)

    # Popola il dizionario raggruppando i file per ID dopo il trattino
    for filename in Q_tables:
        match = re.match(r'(Q\d)-(\d+k)\.pkl', filename)
        if match:
            prefix, id_ = match.groups()
            groups[id_].append(filename)

    # Crea coppie
    pairs = []
    for id_, files in groups.items():
        q1_file = next((f for f in files if f.startswith('Q1')), None)
        q2_file = next((f for f in files if f.startswith('Q2')), None)
        if q1_file and q2_file:
            pairs.append((q1_file, q2_file))

    broken_bricks_tracking_list = []

    episodes = 100
    for Q1_name, Q2_name in pairs:
        print(f"Testing {Q1_name} and {Q2_name}")
        Q1, Q2 = load_tables(f'{test_path}/{Q1_name}', f'{test_path}/{Q2_name}')
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
        report(broken_bricks_tracking_list, f"tests/test{test_id}/trained_performances{Q1_name.split('.')[0].split('-')[-1]}.png", "broken bricks", episodes)
        broken_bricks_tracking_list = []


def load_tables(path1, path2):
    with open(path1, 'rb') as f:
        q1 = pickle.load(f)

    with open(path2, 'rb') as f:
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
