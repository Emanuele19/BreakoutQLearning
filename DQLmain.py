import time

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
import itertools

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.mixed_precision import set_global_policy
from collections import deque


# os.environ["SDL_VIDEODRIVER"] = "dummy"  # Required to run pygame in headless mode

MAX_FRAMES = 7200  # Equivalenti a 2 minuti di gioco a 60FPS

def main():
    if len(sys.argv) < 2:
        print("[USAGE] python3 main.py path/to/parameters.json")

    with open(sys.argv[1], "r") as parameters_file:
        parameters = json.load(parameters_file)

    metaparameters = parameters["metaparameters"]
    learning_rate = metaparameters["learning_rate"]
    rewards = parameters["rewards"]
    output_path = f"./tests/test{metaparameters["id"]}/"
    os.mkdir(output_path)

    exploration_rate = metaparameters["epsilon"]

    controller = ControllerFactory.get_instance(is_human=False, rewards=rewards)

    action_space = [action for action in Slider.Action]
    state_space_len = 3 + len(controller.bricks)

    # Inizializzazione replay buffer e modello
    replay_buffer = deque(maxlen=10000)  # TODO: metti nel file di config
    model = create_dqn_model(input_dim=state_space_len, n_actions=len(action_space), learning_rate=learning_rate)

    # Esecuzione
    reward_traking_list = []
    broken_bricks_list = []
    alpha_tracking_list = []

    controller.reset()


    try:
        for episode in range(metaparameters["episodes"]):
            running = True
            if (episode % 50) != 0:
                print(f"Running episode: {episode}")
            frame_counter = 0
            while running:
                # 1. Osserva lo stato corrente
                state = controller.get_game_state()

                # 2. Scegli un'azione
                action = choose_action(model, state, action_space, exploration_rate)

                # 3. Esegui l'azione
                running = controller.run_game(action)

                new_state = controller.get_game_state()
                reward = controller.get_reward()
                frame_counter += 1

                if controller.is_ended():
                    reward = rewards["win_reward"]
                    running = False
                elif frame_counter >= MAX_FRAMES:
                    reward = rewards["time_exceeded_penalty"]
                    running = False
                    print("Time")

                done = not running  # Se il gioco è terminato

                # 4. Memorizza l'esperienza nella replay buffer
                store_experience(replay_buffer,
                                 preprocess_state(state),
                                 action_to_index(action),
                                 reward,
                                 preprocess_state(new_state),
                                 done)

                # 5. Aggiorna il modello
                if frame_counter % 10 == 0:
                    train_dqn(model, replay_buffer, metaparameters['batch_size'], metaparameters['discount_factor'])

                # 6. Aggiorna il tasso di esplorazione
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print("pygame.QUIT")
                        model.save(f"{output_path}model.h5")
                        report(reward_traking_list, output_path)
                        os._exit(1)


            exploration_rate = epsilon_decay(episode, metaparameters["min_epsilon"], metaparameters["epsilon"],metaparameters["episodes"])
            reward_traking_list.append(controller.get_total_reward())
            broken_bricks_list.append(controller.broken_bricks())
            alpha_tracking_list.append(learning_rate)

            if (episode + 1) % 500 == 0 and episode != 0:
                plot_performance(reward_traking_list, f"{output_path}obtained_rewards.png", "rewards", episode)
                plot_performance(broken_bricks_list, f"{output_path}broken_bricks.png", "broken bricks", episode)
                plot_performance(alpha_tracking_list, f"{output_path}lr_decay.png", "alpha", episode)

            controller.reset()

    except KeyboardInterrupt as e:
        print("KeyboardInterrupt")
        model.save(f"{output_path}model.h5")
        report(reward_traking_list, output_path)
    pygame.quit()

    report(reward_traking_list, output_path)
    model.save(f"{output_path}model.h5")

def action_to_index(action: Slider.Action) -> int:
    return {action: idx for idx, action in enumerate(Slider.Action)}[action]

def index_to_action(index: int) -> Slider.Action:
    return {idx: action for idx, action in enumerate(Slider.Action)}[index]

def preprocess_state(state: list) -> np.array:
    int1, int2, int3, bool_list = state
    bool_array = np.array(bool_list, dtype=np.float32)
    processed_state = np.array([int1, int2, int3], dtype=np.float32)
    processed_state = np.concatenate([processed_state, bool_array])

    return processed_state

def choose_action(model, state, action_space, exploration_rate):
    """
    ε-greedy policy implementation, necessary condition for q-learning convergence
    :returns the greedy choice (from q table) with ε probability and a random choice with 1-ε
    """
    if np.random.rand() < exploration_rate:
        return np.random.choice(action_space)
    else:
        q_values = model.predict(preprocess_state(state).reshape(1, -1), verbose=0)  # Predict Q values
        return index_to_action(np.argmax(q_values[0]))


def update_table(q_table, state, action, reward, new_state, learning_rate, discount_factor):
    max_future_reward = max(q_table[new_state].values())
    q_table[state][action] += learning_rate * (reward + discount_factor * max_future_reward - q_table[state][action])

def epsilon_decay(current_episode: int, min_epsilon:float, epsilon:float, total_episodes:int) -> float:
    return max(min_epsilon, epsilon - current_episode * (epsilon - min_epsilon) / total_episodes)

def alpha_decay(alpha_0: float, decay_rate: float, episode: int) -> float:
    """
    Applies the formula αn = α0 ⋅ e^(-λn) where an is the calculated LR, a0 is the initial LR, λ is the decay rate and
    n is the number of episodes elapsed.

    :param: alpha_0 initial learning rate
    :param: decay_rate exponent (lambda), is a positive value
    :param: episode current episode
    :return: calculated learning rate
    """
    return alpha_0 * np.exp(-decay_rate * episode)

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


def report(parameter_list: list, path):
    """Serializes a list containing the total rewards obtained per episode"""
    with open(f"{path}rewards_per_episode.pkl", "wb") as f:
        pickle.dump(parameter_list, f)


def create_dqn_model(input_dim, n_actions, learning_rate=0.001):
    model = Sequential([
        Dense(64, input_dim=input_dim, activation='relu'),
        Dense(32, activation='relu'),
        Dense(n_actions, activation='linear')
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    return model

def store_experience(replay_buffer, state, action, reward, next_state, done):
    replay_buffer.append((state, action, reward, next_state, done))

def train_dqn(model, replay_buffer, batch_size, gamma):
    if len(replay_buffer) < batch_size or len(replay_buffer) < 10000:
        return  # Aspetta di avere abbastanza esperienze nel buffer
    # Campiona un batch di esperienze dal buffer
    minibatch = random.sample(replay_buffer, batch_size)

    # Prepara le variabili per il training
    states = np.array([exp[0] for exp in minibatch])
    actions = np.array([exp[1] for exp in minibatch]).tolist()
    rewards = np.array([exp[2] for exp in minibatch])
    next_states = np.array([exp[3] for exp in minibatch])
    dones = np.array([exp[4] for exp in minibatch])

    # Predizione dei Q-values per lo stato attuale e quello successivo
    q_values = model.predict(states, verbose=0)
    next_q_values = model.predict(next_states, verbose=0)

    # Calcola il target per ogni transizione
    for i in range(batch_size):
        if dones[i]:
            q_values[i][actions[i]] = rewards[i]  # Nessun valore futuro se lo stato è terminale
        else:
            target_q = rewards[i] + gamma * np.max(next_q_values[i])  # Bellman equation
            q_values[i][actions[i]] = target_q

    # Aggiorna il modello
    model.fit(states, q_values, verbose=0, batch_size=batch_size)


import tensorflow as tf
if __name__ == "__main__":
    # tf.debugging.set_log_device_placement(True)
    set_global_policy('mixed_float16')
    with tf.device('/device:CPU:0'):
        main()
