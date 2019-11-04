import loa_game, random
import matplotlib.pyplot as plt
import numpy as np
# from matplotlib.ticker import MaxNLocator

class Agent:
    def get_action(self):
        return random.randrange(0, 4)

env = loa_game.Env()

agent = Agent()

reward_list = []
action_list = []
step_list = []

episode_num = 1

for episode in range(episode_num):
    state = env.reset()
    total_reward = 0
    step = 1

    while True:
        env.render()
        #stage 깼을 떄의 보상 & step이 아닌 stage수로 바꾸기!

        action = agent.get_action()
        action_list.append(action)
        next_state, reward, done, info = env.step(action)

        total_reward += reward

        if done:
            reward_list.append(total_reward)
            step_list.append(step)
            break

        step += 1

plt.subplot(2,2,1)
# episode 간격으로 표시되도록 하기!
plt.plot(reward_list)
plt.title('Score per Episode')
plt.xlabel('Episode')
plt.ylabel('Scores')

plt.subplot(2,2,2)
# episode 간격으로 표시되도록 하기!
plt.plot(step_list)
plt.title('Steps per Episode')
plt.xlabel('Episode')
plt.ylabel('Steps')

plt.subplot(2,1,2)
plt.hist(np.asarray(action_list), bins=None, cumulative=False)
plt.title('Action Plot')
plt.xlabel('Action')
plt.xticks((0.15, 1.05, 1.95, 2.85), ("UP", "DOWN", "LEFT", "RIGHT")) # 더 좋은 방법 있?
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()
env.close()