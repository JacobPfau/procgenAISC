"""
Generates a dataset of CoinRun images. For a description and images of the classes in this dataset, see https://buildaligned.atlassian.net/browse/CE-100.

This is how each of the classes is generated:
- Agent next to coin on RHS: This is the final state of a normal run of coin run.
- Agent next to coin not on RHS: This is the final state of a run of coin run with random coin placement.
- Agent on RHS but not next to coin: This is a horizontally flipped version of the  starting state of the normal coin run.
- Agent not next to coin and coin on RHS: This is a non-final state of a normal run.

There are vastly more examples of the agent not being next to the coin and not being on the right hand side than there are examples of the other three classes. The fixed_mix_rate flag for write_to_dirs controls whether to read just the mix rates. If this flag is not set, unlabeled/diag/playerLeftCoinNotFound will contain thousands of examples.

Note that the images in this dataset are the low resolution 64x64 images that are used by ML agents, rather than the high resolution images for humans. 

The version of procgen used is this fork https://github.com/JacobPfau/procgenAISC, rather than the original OpenAI version
"""
import sys
import os
import random
import json
import numpy as np
from procgen import ProcgenGym3Env
from gym3 import types_np
from PIL import Image

metadata = {
    "training_folders": {
        "labeled/diag/playerRightCoinFound": [[1, 1], [True, True]],
        "labeled/diag/playerLeftCoinNotFound": [[0, 0], [True, True]],
        "unlabeled/diag/playerRightCoinFound": [[1, 1], [False, False]],
        "unlabeled/diag/playerLeftCoinNotFound": [[0, 0], [False, False]],
        "unlabeled/cross/playerLeftCoinFound": [[0, 1], [False, False]],
        "unlabeled/cross/playerRightCoinNotFound": [[1, 0], [False, False]],
    },
    "validation_folders": {
        "val/diag/playerRightCoinFound": [[1, 1]],
        "val/diag/playerLeftCoinNotFound": [[0, 0]],
        "val/cross/playerLeftCoinFound": [[0, 1]],
        "val/cross/playerRightCoinNotFound": [[1, 0]],
    },
    "testing_folders": {
        "test/diag/playerRightCoinFound": [[1, 1]],
        "test/diag/playerLeftCoinNotFound": [[0, 0]],
        "test/cross/playerLeftCoinFound": [[0, 1]],
        "test/cross/playerRightCoinNotFound": [[1, 0]],
    },
}

MULTIPLIER = 0.1

class_counts = {
    "validation_folders": {
        "val/diag/playerRightCoinFound": 50 * MULTIPLIER,
        "val/diag/playerLeftCoinNotFound": 50 * MULTIPLIER,
        "val/cross/playerLeftCoinFound": 50 * MULTIPLIER,
        "val/cross/playerRightCoinNotFound": 50 * MULTIPLIER,
    },
    "testing_folders": {
        "test/diag/playerRightCoinFound": 50 * MULTIPLIER,
        "test/diag/playerLeftCoinNotFound": 50 * MULTIPLIER,
        "test/cross/playerLeftCoinFound": 50 * MULTIPLIER,
        "test/cross/playerRightCoinNotFound": 50 * MULTIPLIER,
    },
    "training_folders": {
        "labeled/diag/playerRightCoinFound": 100 * MULTIPLIER,
        "labeled/diag/playerLeftCoinNotFound": 100 * MULTIPLIER,
        "unlabeled/diag/playerRightCoinFound": 150 * MULTIPLIER,
        "unlabeled/diag/playerLeftCoinNotFound": 150 * MULTIPLIER,
        "unlabeled/cross/playerLeftCoinFound": 150 * MULTIPLIER,
        "unlabeled/cross/playerRightCoinNotFound": 150 * MULTIPLIER,
    },
}


def add_move_to_obs(obs, move):
    try:
        obs["rgb"][:, :10, :] = move[0].detach().cpu() * 20
    except AttributeError:
        obs["rgb"][:, :10, :] = move[0] * 20


def act(env):
    _, obs, _ = env.observe()
    move = types_np.sample(env.ac_space, bshape=(env.num,))
#    move=np.array([8]) #8
    move=np.array([random.randrange(10)])
    env.act(move)
    rew, _, first = env.observe()
    add_move_to_obs(obs, move)
    return rew, obs['rgb'][0], first


def get_other_classes(count: int):
    """
    Get all the other classes of image.
    """
    playerRightCoinFound: list[np.array] = []
    playerLeftCoinNotFound: list[np.array] = []
    env = ProcgenGym3Env(num=1, env_name="coinrun")
    while len(playerRightCoinFound) < count:
        last_obs = []
        step = 0
        while True:
            rew, obs, first = act(env)
            last_obs.append(obs["rgb"][0].copy())
            if step > 0 and first:
                if rew > 0.0:
                    playerRightCoinFound.append(last_obs[-2])
                    playerLeftCoinNotFound.extend(last_obs[1 : len(last_obs) - 2])
                    print(f"Found {len(playerRightCoinFound)}/{count} other classes")
                else:
                    break
            step += 1
    random.shuffle(playerLeftCoinNotFound)
    return playerRightCoinFound, playerLeftCoinNotFound


def get_coin_found_not_right_class(count: int):
    """
    Get examples where the coin is found, but it is not on the right hand side of the game.
    """
    playerLeftCoinFound: list[np.array] = []
    playerRightCoinNotFound: list[np.array] = []
    env = ProcgenGym3Env(num=1, env_name="coinrun", random_percent=100)
    while len(playerLeftCoinFound) < count:
        last_obs = []
        step = 0
        has_reached_wall = False
        while True:
            rew, obs, first = act(env)
            last_obs.append(obs["rgb"][0].copy())
            print(env.get_info()[0]["invisible_coin_collected"])
            if (
                env.get_info()[0]["invisible_coin_collected"] == 1
                and not has_reached_wall
            ):
                has_reached_wall = True
                playerRightCoinNotFound.append(last_obs[-1])
            if step > 0 and first:
                if rew > 0.0:
                    playerLeftCoinFound.append(last_obs[-2])
                    print(
                        f"Found {len(playerLeftCoinFound)}/{count} coin found not right classes"
                    )
                else:
                    break
            step += 1
    return playerLeftCoinFound, playerRightCoinNotFound


def write_to_dirs(data_dir, fixed_mix_rate=True):
    dataset_name = data_dir.split("/")[-1]
    metadata_filename = f"metadata_{dataset_name}.json"

    with open(f"{data_dir}/{metadata_filename}", "w") as f:
        json.dump(metadata, f)

    img_total = (
        class_counts["training_folders"]["labeled/diag/playerRightCoinFound"]
        + class_counts["training_folders"]["unlabeled/diag/playerRightCoinFound"]
        + class_counts["validation_folders"]["val/diag/playerRightCoinFound"]
        + class_counts["testing_folders"]["test/diag/playerRightCoinFound"]
    )

    imgs = {}
    # (
    #     imgs["playerRightCoinFound"],
    #     imgs["playerLeftCoinNotFound"],
    # ) = get_other_classes(img_total)
    (
        imgs["playerLeftCoinFound"],
        imgs["playerRightCoinNotFound"],
    ) = get_coin_found_not_right_class(img_total)
    raise Exception()

    for _, dir_set in class_counts.items():
        for dir, count in dir_set.items():
            os.makedirs(f"{data_dir}/{dir}", exist_ok=True)
            data_class = dir.split("/")[-1]
            if dir == "labeled/diag/playerLeftCoinNotFound" and not fixed_mix_rate:
                # Use all the available images for this class rather than fixing the mix rate - see docstring. We don't want to lower the mixrate even further, so just include the proportion of these runs that were for the unlabeled dataset.
                class_imgs = imgs[data_class][
                    : round(100 / 350 * len(imgs[data_class]))
                ]
                imgs[data_class] = imgs[data_class][
                    round(100 / 350 * len(imgs[data_class])) :
                ]
            elif dir == "unlabeled/diag/playerLeftCoinNotFound" and not fixed_mix_rate:
                class_imgs = imgs[data_class][
                    : round(150 / 350 * len(imgs[data_class]))
                ]
                imgs[data_class] = imgs[data_class][
                    round(150 / 350 * len(imgs[data_class])) :
                ]
            else:
                class_imgs = imgs[data_class][: round(count)]
                imgs[data_class] = imgs[data_class][round(count) :]
            for i, im in enumerate(class_imgs):
                Image.fromarray(im).save(f"{data_dir}/{dir}/{i}.png")


if __name__ == "__main__":
    data_dir = sys.argv[1]
    fixed_mix_rate = sys.argv[2] == "True"
    write_to_dirs(data_dir, fixed_mix_rate=fixed_mix_rate)
