import os
import pickle
import time
from matplotlib import pyplot as plt
import re

from control.controllerFactory import ControllerFactory

MAX_PLAYING_TIME = 3.6
MAX_FRAMES = 7200

def main():
    controller = ControllerFactory.get_instance(is_human=False)

    test_id = 47

    base_path = f"tests/test{test_id}"
    q_tables = [path for path in os.listdir(base_path) if re.match('Q_table-\d+k\.pkl', path)]

    reporter = PerformanceReporter()
    looped = False

    episodes = 100
    for q_table in q_tables:
        Q = load_table(base_path + "/" + q_table)
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
                    reporter.add_loop()
                    looped = True
                    break

            if not looped:
                reporter.add(controller.broken_bricks())
            else:
                looped = False

        reporter.report(f"tests/test{test_id}", q_table.split('k')[0].split('-')[-1])


def load_table(path='Q_table.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)

class PerformanceReporter:
    def __init__(self, n_bricks:int = 10):
        self.n_bricks = n_bricks
        self.perf_map = [0] * (n_bricks + 1)

    def add(self, score:int) -> None:
        self.perf_map[score] += 1

    def add_loop(self) -> None:
        self.perf_map[-1] += 1

    def report(self, base_path:str, episodes:str = None) -> None:
        plt.figure(figsize=(10, 6))
        bar_colors = ['blue'] * self.n_bricks + ['red']
        keys = list(map(str, range(self.n_bricks))) + ['x']
        plt.bar(keys, self.perf_map, color=bar_colors)
        plt.xlabel("Punteggio")
        plt.ylabel("Numero di episodi")
        plt.title("Performance" + (f" ({episodes})" if episodes else ""))
        plt.savefig(f"{base_path}/trained_performances{episodes}.png")
        plt.plot()
        self.perf_map = [0] * (self.n_bricks + 1) # reset

if __name__ == '__main__':
    main()
