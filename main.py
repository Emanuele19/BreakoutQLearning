import pygame
import configs
from control.controllerFactory import ControllerFactory
from objects.slider import Slider
import random
import pickle
import matplotlib.pyplot as plt
import os
import numpy as np
import json
import sys


# TODO: fare uno spreadsheet per confrontare le prestazioni del modello allenato su diversi valori di metaparametri
# TODO: trovato il set di parametri migliori prova a cambiare i rewards
#       sembra che l'agente si soffermi temporaneamente a palleggiare a vuoto, la penalty temporale no è abbastanza incisiva
# RICERCA: in ambienti completamente deterministici un learning rate di 1 è ottimo??? Questo è un ambiente deterministico?

# TODO: e se non dessi alcun bouncing reward? Lo slider sarà comunque incentivato ad avvicinarsi alla palla per via della penalty
#       e potrei evitare di far bloccare l'agente in politiche sub-ottimali.
def main():
    if len(sys.argv) < 2:
        print("[USAGE] python3 main.py path/to/parameters.json")

    with open(sys.argv[1], "r") as parameters_file:
        parameters = json.load(parameters_file)

    metaparameters = parameters["metaparameters"]
    rewards = parameters["rewards"]
    output_path = f"./tests/test{metaparameters["id"]}/"
    os.mkdir(output_path)

    exploration_rate = metaparameters["epsilon"]

    controller = ControllerFactory.get_instance(is_human=False, rewards=rewards)
    # action_space e state_space sono tutte le possibili azioni e tutti i possibili stati
    action_space = [action for action in Slider.Action]
    state_space = [(ball_x, ball_y, ball_dir_x, ball_dir_y, slider_x)
                   for ball_x in range(configs.SAMPLING_RATE)
                   for ball_y in range(configs.SAMPLING_RATE)
                   for ball_dir_x in [1, -1]
                   for ball_dir_y in [1, -1]
                   for slider_x in range(configs.SAMPLING_RATE)]

    # Inizializzazione della tabella
    Q = {}
    for state in state_space:
        Q[state] = {action: 0.0 for action in action_space}

    # Esecuzione
    reward_traking_list = []
    epsilon_tracking_list = []
    broken_bricks_list = []

    controller.reset()
    for episode in range(metaparameters["episodes"]):
        running = True
        print(f"Running episode: {episode}")
        while running:
            # 1. Osserva lo stato corrente
            state = controller.get_game_state()

            # 2. Scegli un'azione
            action = choose_action(Q, state, action_space, exploration_rate)

            # 3. Esegui l'azione
            running = controller.run_game(action)

            new_state = controller.get_game_state()
            reward = controller.get_reward()

            if controller.is_ended():
                reward = 1000  # Win reward
                running = False

            # 4. Aggiorna la tabella
            update_table(Q, state, action, reward, new_state, metaparameters["learning_rate"], metaparameters["discount_factor"])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("pygame.QUIT")
                    serialize_table(Q, output_path)
                    report(reward_traking_list, output_path)
                    os._exit(1)


        exploration_rate = epsilon_decay(episode, metaparameters["min_epsilon"], metaparameters["epsilon"],metaparameters["episodes"])
        epsilon_tracking_list.append(exploration_rate)
        reward_traking_list.append(controller.get_total_reward())
        broken_bricks_list.append(controller.broken_bricks())

        if (episode + 1) % 500 == 0 and episode != 0:
            plot_performance(reward_traking_list, f"{output_path}obtained_rewards.png", "rewards", episode)
            plot_performance(epsilon_tracking_list, f"{output_path}exploration_rate_decay.png", "epsilon", episode)
            plot_performance(broken_bricks_list, f"{output_path}broken_bricks.png", "broken bricks", episode)

        controller.reset()
    pygame.quit()

    report(reward_traking_list, output_path)
    serialize_table(Q, output_path)


# Scelta "epsilon" greedy
# Con probabilità epsilon (p) fai la scelta greedy, con quella complementare fai una scelta casuale
def choose_action(q_table, current_state, action_space, p):
    if random.uniform(0, 1) < p:
        return random.choice(action_space)
    else:
        return max(q_table[current_state], key=q_table[current_state].get)


def update_table(q_table, state, action, reward, new_state, learning_rate, discount_factor):
    max_future_reward = max(q_table[new_state].values())
    q_table[state][action] += learning_rate * (reward + discount_factor * max_future_reward - q_table[state][action])

def epsilon_decay(current_episode: int, min_epsilon:float, epsilon:float, total_episodes:int) -> float:
    return max(min_epsilon, epsilon - current_episode * (epsilon - min_epsilon) / total_episodes)

def serialize_table(q, path):
    with open(f'{path}Q_table.pkl', 'wb') as f:
        pickle.dump(q, f)

def load_table():
    with open('Q_table.pkl', 'rb') as f:
        return pickle.load(f)

def plot_performance(parameter_list: list, filename: str, parameter_name: str, episodes: int):
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    plt.figure()
    plt.title(f"{parameter_name} ({episodes+1}) episodes")
    plt.ylabel(parameter_name)
    means_list = [np.mean(c) for c in chunks(parameter_list, 500)]
    x_means = np.arange(250, len(parameter_list), 500)
    plt.plot(parameter_list, marker='.')
    plt.plot(x_means, means_list, marker='x')
    plt.savefig(filename)
    plt.close()

"""Serializes a list containing the total rewards obtained per episode"""
def report(parameter_list: list, path):
    with open(f"{path}rewards_per_episode.pkl", "wb") as f:
        pickle.dump(parameter_list, f)

if __name__ == "__main__":
    main()
