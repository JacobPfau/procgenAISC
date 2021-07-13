# Objective Robustness in Procgen

This is a fork of the [procgen benchmark](https://github.com/openai/procgen) that implements modifications for the paper [Objective Robustness in Deep Reinforcement Learning](https://arxiv.org/abs/2105.14111).

## Training code

Code to reproduce the results from the paper is [available from this repository](https://github.com/jbkjr/train-procgen-pytorch/tree/objective-robustness) on branch `objective-robustness`.

## Descriptions of the modified environments

* `coinrun_aisc`: Like `coinrun`, but the coin is placed randomly on ground level instead of at the far right end.
* `coinrun`: Added a flag `--random_percent`, which places the coin randomly in a given percentage of environments. Default 0.
* `heist_aisc_many_chests`: A heavily modified `heist`. Doors are now 'chests' (they do not prevent the agent from passing). Every key can open every chest. The agent is rewarded for opening chests. This version generates twice as many chests as keys.
* `heist_aisc_many_keys`: Same as `heist_aisc_many_chests`, but instead has twice as many keys as chests.
* `maze_aisc`: Like maze, but the cheese is always to be found in the top right corner.
* `maze_yellowgem`: like maze, but the goal is a yellow gem.
* `maze_redgem_yellowstar`: like maze, but two objects are placed in the maze: a red gem, and a yellow star. The objective is the red gem.
* `maze_yellowstar_redgem`: Identical to `maze_yellowstar_redgem`, but the objective is instead the yellow star.

For more information on the standard environments see the original repository.

## Installation

Below we reproduce the instructions to install from source, copied from the [original repo](https://github.com/openai/procgen).

---

First make sure you have a supported version of python:

```
# run these commands to check for the correct python version
python -c "import sys; assert (3,6,0) <= sys.version_info <= (3,9,0), 'python is incorrect version'; print('ok')"
python -c "import platform; assert platform.architecture()[0] == '64bit', 'python is not 64-bit'; print('ok')"
```

If you want to change the environments or create new ones, you should build from source.  You can get miniconda from https://docs.conda.io/en/latest/miniconda.html if you don't have it, or install the dependencies from [`environment.yml`](environment.yml) manually.  On Windows you will also need "Visual Studio 15 2017" installed.

```
git clone git@github.com:openai/procgen.git
cd procgen
conda env update --name procgen --file environment.yml
conda activate procgen
pip install -e .
# this should say "building procgen...done"
python -c "from procgen import ProcgenGym3Env; ProcgenGym3Env(num=1, env_name='coinrun')"
# this should create a window where you can play the coinrun environment
python -m procgen.interactive
```

The environment code is in C++ and is compiled into a shared library exposing the [`gym3.libenv`](https://github.com/openai/gym3/blob/master/gym3/libenv.h) C interface that is then loaded by python.  The C++ code uses [Qt](https://www.qt.io/) for drawing.
