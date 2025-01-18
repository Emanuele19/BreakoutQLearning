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

os.environ["SDL_VIDEODRIVER"] = "dummy"  # Required to run pygame in headless mode

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
    # action_space e state_space sono tutte le possibili azioni e tutti i possibili stati
    action_space = [action for action in Slider.Action]
    state_space = [(ball_x, ball_dir_x, slider_x, brick_state)
                   for ball_x in range(configs.SAMPLING_RATE)
                   for ball_dir_x in [1, -1]
                   for slider_x in range(configs.SAMPLING_RATE)
                   for brick_state in tuple(itertools.product([True, False], repeat=len(controller.bricks)))]

    # Inizializzazione della tabella
    Q1 = Q2 = {}
    for state in state_space:
        Q1[state] = Q2[state] = {action: 0.0 for action in action_space}

    # Esecuzione
    reward_traking_list = []
    epsilon_tracking_list = []
    broken_bricks_list = []
    alpha_tracking_list = []

    controller.reset()


    try:
        for episode in range(metaparameters["episodes"]):
            running = True
            if (episode % 50) == 0:
                print(f"Running episode: {episode}")
            frame_counter = 0
            while running:
                # 1. Osserva lo stato corrente
                state = controller.get_game_state()

                # 2. Scegli un'azione
                action = choose_action(Q1, Q2, state, action_space, exploration_rate)

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

                # 4. Aggiorna la tabella
                update_table(Q1, Q2, state, action, reward, new_state, learning_rate, metaparameters["discount_factor"]
                             ,is_terminal_state=(not running))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print("pygame.QUIT")
                        serialize_tables(Q1, Q2, output_path, episode // 1000)
                        report(reward_traking_list, output_path)
                        os._exit(1)


            # exploration_rate = linear_decay(episode, metaparameters["min_epsilon"], metaparameters["epsilon"], metaparameters["episodes"])
            exploration_rate = exp_decay(metaparameters['min_epsilon'], metaparameters['decay_rate'], episode)
            # learning_rate = alpha_decay(metaparameters["learning_rate"], metaparameters["decay_rate"], episode)
            reward_traking_list.append(controller.get_total_reward())
            broken_bricks_list.append(controller.broken_bricks())
            alpha_tracking_list.append(learning_rate)

            if (episode + 1) % 500 == 0 and episode != 0:
                plot_performance(reward_traking_list, f"{output_path}obtained_rewards.png", "rewards", episode)
                # plot_performance(epsilon_tracking_list, f"{output_path}exploration_rate_decay.png", "epsilon", episode)
                plot_performance(broken_bricks_list, f"{output_path}broken_bricks.png", "broken bricks", episode)
                plot_performance(alpha_tracking_list, f"{output_path}lr_decay.png", "alpha", episode)

            if episode % 25_000 == 0 and episode != 0:
                serialize_tables(Q1, Q2, output_path, episode // 1000)

            controller.reset()

    except KeyboardInterrupt as e:
        print("KeyboardInterrupt")
        serialize_tables(Q1, Q2, output_path, episode)
        report(reward_traking_list, output_path)
    pygame.quit()

    report(reward_traking_list, output_path)
    serialize_tables(Q1, Q2, output_path, float(metaparameters['episodes']) // 1000)



def choose_action(q1, q2, current_state, action_space, p) -> Slider.Action:
    """
    ε-greedy policy implementation, necessary condition for q-learning convergence
    :returns the greedy choice (from q table) with ε probaility and a random choice with 1-ε
    """
    if random.uniform(0, 1) < p:
        return random.choice(action_space)
    else:
        # result = {key: dict1[key] + dict2[key] for key in dict1}
        s1 = q1[current_state]
        s2 = q2[current_state]
        Q_combined = {action: s1[action] + s2[action] for action in s1}

        return max(Q_combined, key=Q_combined.get)

def update_table(q1, q2, state, action, reward, new_state, learning_rate, discount_factor, is_terminal_state=False):
    """
    With equal probability update eitheir the first or the second table
    """
    if random.uniform(0, 1) < 0.5:
        max_future_reward = 0 if is_terminal_state else max(q2[new_state].values())
        q1[state][action] += learning_rate * (reward + discount_factor * max_future_reward - q1[state][action])
    else:
        max_future_reward = 0 if is_terminal_state else max(q1[new_state].values())
        q2[state][action] += learning_rate * (reward + discount_factor * max_future_reward - q2[state][action])

def linear_decay(current_episode: int, min_val:float, val:float, total_episodes:int) -> float:
    return max(min_val, val - current_episode * (val - min_val) / total_episodes)

def exp_decay(starting_val: float, decay_rate: float, episode: int) -> float:
    """
    Applies the formula αn = α0 ⋅ e^(-λn) where an is the calculated LR, a0 is the initial LR, λ is the decay rate and
    n is the number of episodes elapsed.

    :param: starting_val initial value
    :param: decay_rate exponent (lambda), is a positive value
    :param: episode current episode
    :return: calculated value
    """
    return starting_val * np.exp(-decay_rate * episode)
        
def serialize_tables(q1, q2, path, id):
    with open(f'{path}Q1-{id}k.pkl', 'wb') as f:
        pickle.dump(q1, f)
    with open(f'{path}Q2-{id}k.pkl', 'wb') as f:
        pickle.dump(q2, f)

def load_tables():
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


def report(parameter_list: list, path):
    """Serializes a list containing the total rewards obtained per episode"""
    with open(f"{path}rewards_per_episode.pkl", "wb") as f:
        pickle.dump(parameter_list, f)

if __name__ == "__main__":
    main()
