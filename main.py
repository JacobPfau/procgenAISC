from PIL import Image
import matplotlib.pyplot as plt
from procgen import ProcgenGym3Env
import sys
import numpy as np 
import random
from scripts.coinrun import act
import copy

if len(sys.argv) >= 2:
    labeled = bool(int(sys.argv[1]))
    print(sys.argv[1], labeled)
else:
    labeled = False
if len(sys.argv) >= 3:
    dir = sys.argv[2]
else:
    dir = 'traindir_10' # the directory into which the images shall be put

if len(sys.argv) >= 4:
    range_start = int(sys.argv[3])
else:
    range_start = 0

if len(sys.argv) >= 5:
    range_end = int(sys.argv[4])
else:
    range_end = 1500


image_plot_range = 3
after_reward = 1

if labeled: #if we're playing without labeling, the coin is randomly placed 100% of the time
    random_percent = 0
    lab = 'labeled_'
    end_run_lim = 900
else:
    random_percent = 100
    lab = 'unlabeled_'
    end_run_lim = 30

print(lab)

env = ProcgenGym3Env(num=1, env_name="coinrun", random_percent = random_percent, continue_after_coin = True)
# generates the environments, with "random_percent" percentage of them with the coin randomly placed


def get_concat_h(images): # creates an image conisting of all the images pasted in order
    image_length = 0
    for im in images:
        image_length += im.width
    dst = Image.new('RGB', (image_length, images[0].height))
    current_length = 0
    for im in images:
        dst.paste(im, (current_length, 0))
        current_length += im.width
    return dst

mid_num=0
actions = [8,4,4,-1,7,-1] # the actions are jump-moving right and moving right, to find the coin
from itertools import cycle

def update_track(track):
    for i in range(len(track)-1):
        track[i] = copy.copy(track[i+1])
    track[-1] = False

coin_track = [False for n in range(after_reward + 1)]
end_track = [False for n in range(after_reward + 1)]

def add_move_to_obs(obs, move): # adds the action chosen to the state, as a band of grey of different darkness across the top of the state image
    try:
        obs["rgb"][:, :10, :] = move[0].detach().cpu() * 20
    except AttributeError:
        obs["rgb"][:, :10, :] = move[0] * 20

for i in range(range_start, range_end):
    done=False
    mid_num=0
    images_batch = []
    acting = cycle(actions)
    for action in acting:
        move=np.array([action])
        if [action] == [-1]: move=np.array([random.randint(0,8)])
#        if True in coin_track or not labeled: # if the coin has been found (in labeled situation) or the situation is unlabeled, move randomly
#            move=np.array([random.randint(0,8)])
        env.act(move)
        rew, obs, first = env.observe()
#        add_move_to_obs(obs, move)
        if first[0] == True:
            break
        images_batch.append(Image.fromarray(obs['rgb'][0]))
        coin, end = ('', '') # resets the coin and end strings
        num = f'{mid_num:04d}'
        run_num = f'{i:05d}'

        env.get_info()[0]['invisible_coin_collected']
        update_track(end_track)
        update_track(coin_track)
        if not labeled and env.get_info()[0]['invisible_coin_collected'] == 1:
            # if there are no labels and the agent has reached the end
            end_track[-1] = True
        if rew[0] > 5:
            coin_track[-1] = True

        if coin_track[0] == True:
            coin = '_coin'
        if end_track[0] == True:
            end = '_end'

        if len(images_batch) >= image_plot_range and done==False:
            if coin_track[0] == True and labeled: # if we are in the labeled situation, we can stop generating images since we do get the end signal
                done = True
            images = [images_batch[n - image_plot_range] for n in range(image_plot_range)]
            img = get_concat_h(images)
            img.save('/home/stuad/procgenAISC/' + dir + '/' + lab + 'run_' + run_num + '_' + num + coin + end + '.png')
        mid_num+=1

        if mid_num >= end_run_lim: # gives the agent 900 turns to find the coin before ending printing the images
            done=True
 

#actions:
#        return [
# 0           ("LEFT", "DOWN"),
# 1           ("LEFT",),
# 2           ("LEFT", "UP"),
# 3           ("DOWN",),
# 4           (),
# 5           ("UP",),
# 6           ("RIGHT", "DOWN"),
# 7           ("RIGHT",),
# 8           ("RIGHT", "UP"),
# 9           ("D",),
# 10          ("A",),
# 11          ("W",),
# 12          ("S",),
# 13          ("Q",),
# 14          ("E",),
#        ]
