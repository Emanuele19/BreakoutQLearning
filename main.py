import pygame

import configs
from control.controller import MainController
from objects.slider import Slider
import random
import pickle
import matplotlib.pyplot as plt


# Appunti:
# Per far funzionare il Q-Learning con parametri continui (posizione per es.) devo prima discretizzarli
# I parametri da distretizzare sono la posizione della palla (x, y), la direzione (su/giù, sinistra/destra)
#   e la posizione dello slider (sinistra/destra)

def main():
    EPSILON = 0.1
    LEARNING_RATE = 0.001
    DISCOUNT_FACTOR = 0.999

    controller = MainController().get_instance(is_human=False)
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
    episodes = 5000
    for episode in range(episodes):
        running = True
        print(f"Running episode: {episode}")
        controller.reset()
        while running:
            # 1. Osserva lo stato corrente
            state = controller.get_game_state()

            # 2. Scegli un'azione
            action = choose_action(Q, state, action_space, EPSILON)

            # 3. Esegui l'azione
            running = controller.run_game(action)

            new_state = controller.get_game_state()
            reward = controller.get_reward()

            # 4. Aggiorna la tabella
            update_table(Q, state, action, reward, new_state, LEARNING_RATE, DISCOUNT_FACTOR)
            EPSILON = max(0.01, EPSILON * 0.99995)
            epsilon_tracking_list.append(EPSILON)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("pygame.QUIT")
                    serialize_table(Q)
                    os._exit(1)

        reward_traking_list.append(controller.get_total_reward())

        if episode % 100 == 0 and episode != 0:
            report(reward_traking_list, "rewards.png", "rewards", episode)
            report(epsilon_tracking_list, "discount_factor.png", "epsilon", episode)
    pygame.quit()

    serialize_table(Q)


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

def serialize_table(q):
    with open('Q_table.pkl', 'wb') as f:
        pickle.dump(q, f)

def load_table():
    with open('Q_table.pkl', 'rb') as f:
        return pickle.load(f)

def report(parameter_list: list, filename: str, parameter_name: str, episodes: int):
    plt.figure()
    plt.plot(parameter_list, marker='.')
    plt.title(f"{parameter_name} ({episodes}) episodes")
    plt.ylabel(parameter_name)
    plt.savefig(filename)
    plt.close()

if __name__ == "__main__":
    main()
