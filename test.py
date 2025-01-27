import os, re
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

    test_id = 56

    test_path = f'tests/test{test_id}'
    Q_tables = [f for f in os.listdir(test_path) if re.match(r'Q_table-\d+\.0k\.pkl', f)]

    broken_bricks_tracking_list = []
    reporter = PerformanceReporter()
    looped = False

    for Q in Q_tables:
        episodes = 100
        id = Q.split('-')[-1].split('.pkl')[0][:-3]
        Q_table = load_table(test_path + '/' + Q)
        print(f'Testing file {id}')
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
                action = max(Q_table[state], key=Q_table[state].get)

                # 3. Esegui l'azione
                running = controller.run_game(action)
                frame_counter += 1
                if controller.is_ended():
                    running = False
                elif frame_counter >= MAX_FRAMES:
                    print(time.time() - start_time)
                    reporter.add_loop()
                    looped = True
                    break

            if not looped:
                reporter.add(controller.broken_bricks())
            else:
                looped = False
        reporter.report(f"tests/test{test_id}", Q.split('.0k')[0].split('-')[-1])


def load_table(path='Q_table.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)

class PerformanceReporter:
    def __init__(self, n_bricks:int = 10):
        self.n_bricks = n_bricks
        self.perf_map = [0] * (n_bricks + 2)

    def add(self, score:int) -> None:
        self.perf_map[score] += 1

    def add_loop(self) -> None:
        self.perf_map[-1] += 1

    def report(self, base_path:str, episodes:str = None) -> None:
        plt.figure(figsize=(10, 6))
        bar_colors = ['blue'] * (self.n_bricks + 1) + ['red']
        keys = list(map(str, range(self.n_bricks + 1))) + ['x']
        plt.bar(keys, self.perf_map, color=bar_colors)
        plt.xlabel("Punteggio")
        plt.ylabel("Numero di episodi")
        plt.title("Performance" + (f" ({episodes})" if episodes else ""))
        plt.savefig(f"{base_path}/trained_performances{episodes}.png")
        plt.plot()
        self.perf_map = [0] * (self.n_bricks + 2) # reset

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
