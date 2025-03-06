# Graph Matrix Job Shop Env

![](https://github.com/Alexander-Nasuta/GraphMatrixJobShopEnv/raw/master/resources/asni-render.gif)

A Gymnasium Environment for Job Shop Scheduling using the Graph Matrix Representation by [Błażewicz et al.](https://www.sciencedirect.com/science/article/abs/pii/S0377221799004865).

- Github: [GraphMatrixJobShopEnv](https://github.com/Alexander-Nasuta/GraphMatrixJobShopEnv)
- Pypi: [GraphMatrixJobShopEnv](https://pypi.org/project/graph-matrix-jsp-env/)
- Documentation: [GraphMatrixJobShopEnv Docs](https://graphmatrixjobshopenv.readthedocs.io/en/latest/)

## Description

A Gymnasium Environment for Job Shop Scheduling using the Graph Matrix Representation by [Błażewicz et al.](https://www.sciencedirect.com/science/article/abs/pii/S0377221799004865).
It can be used to solve the Job Shop Scheduling Problem (JSP) using Reinforcement Learning with libraries like [Stable Baselines3](https://stable-baselines3.readthedocs.io/en/master/) or [RLlib](https://docs.ray.io/en/latest/rllib/index.html).
A minimal working example is provided in the [Quickstart](#quickstart) section.

## Quickstart

```shell
pip install graph-matrix-jsp-env
```

### Random Agent Example

```python
from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
import numpy as np

if __name__ == '__main__':
    custom_jsp_instance = np.array([
        [
            [0, 1, 2, 3],  # job 0
            [0, 2, 1, 3]  # job 1
        ],
        [
            [11, 3, 3, 12],  # task durations of job 0
            [5, 16, 7, 4]  # task durations of job 1
        ]

    ], dtype=np.int32)
    env = DisjunctiveGraphJspEnv(
        jsp_instance=custom_jsp_instance,
    )
    obs, info = env.reset()

    terminated = False

    while not terminated:
        action = env.action_space.sample(mask=env.valid_action_mask())
        obs, reward, terminated, truncated, info = env.step(action)
        env.render(mode='debug')
```

### Stable Baselines3 Example

To train a PPO agent using the environment with Stable Baselines3 one first needs to install the required dependencies:

```shell
pip install stable-baselines3
pip install sb3-contrib
```

Then one can use the following code to train a PPO agent:

```python
import gymnasium as gym
import sb3_contrib
import stable_baselines3 as sb3

import numpy as np
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker

from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv

if __name__ == '__main__':
    
    custom_jsp_instance = np.array([
        [
            [0, 1, 2, 3],  # job 0
            [0, 2, 1, 3]  # job 1
        ],
        [
            [11, 3, 3, 12],  # task durations of job 0
            [5, 16, 7, 4]  # task durations of job 1
        ]

    ], dtype=np.int32)
    
    # just make sure to import them from jsp_instance_utils.instances
    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance) 
    env = sb3.common.monitor.Monitor(env)


    def mask_fn(env: gym.Env) -> np.ndarray:
        return env.unwrapped.valid_action_mask()


    env = ActionMasker(env, mask_fn)

    model = sb3_contrib.MaskablePPO(
        MaskableActorCriticPolicy,
        env,
        verbose=1,
        device="cpu" # Note: You can also use "cuda" if you have a GPU with CUDA
    )

    # Train the agent
    model.learn(total_timesteps=10_000)
```

## Visualizations

The environment offers multiple visualisation options.
There are four visualisations that can be mixed and matched:
- `human` (default): prints a Gantt chart visualisation to the console.
- `ansi`: prints a visualisation of the graph matrix and the Gantt chart to the console.
- `debug`: prints a visualisation of the graph matrix. The debugs visualisation is maps the elements of the successor lists and unknown list to the original graph indices of the takes ad uses colors to separate the different elements. It also prints the Gantt chart and some additional information.
- `window`: creates a Gantt chart visualisation in a separate window.
- `rgb_array`: creates a Gantt chart visualisation as a RGB array. This mode return the RGB array of the `window` visualisation. This can be used to create a video of the Gantt chart visualisation. 

### Examples

For the following Job Shop Scheduling Problem (JSP) instance:

```python
from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
import numpy as np

if __name__ == '__main__':
    custom_jsp_instance = np.array([
        [
            [0, 1, 2, 3],  # job 0
            [0, 2, 1, 3]  # job 1
        ],
        [
            [11, 3, 3, 12],  # task durations of job 0
            [5, 16, 7, 4]  # task durations of job 1
        ]

    ], dtype=np.int32)
    env = DisjunctiveGraphJspEnv(
        jsp_instance=custom_jsp_instance,
    )
    obs, info = env.reset()
    mode = 'debug' # replace with 'human', 'ansi', 'window', 'rgb_array' for different visualizations
    env.render(mode=mode) 

    for a in [5, 1, 2, 6, 3, 7, 4, 8]:
        env.step(a)
        env.render(mode=mode)

    env.render()
```

The individual rendering modes result in the following visualisations:

#### ANSI

![](https://github.com/Alexander-Nasuta/GraphMatrixJobShopEnv/raw/master/resources/asni-render.gif)

#### Debug

![](https://github.com/Alexander-Nasuta/GraphMatrixJobShopEnv/raw/master/resources/debug-render.gif)

#### Defualt (Human)

![](https://github.com/Alexander-Nasuta/GraphMatrixJobShopEnv/raw/master/resources/default-render.gif)

### window

![](https://github.com/Alexander-Nasuta/GraphMatrixJobShopEnv/raw/master/resources/window-render.gif)

The Terminal used for the visualisations is [Ghostty](https://github.com/ghostty-org/ghostty).

## State of the Project

This project is complementary material for a research paper. It will not be frequently updated.
Minor updates might occur.
Significant further development will most likely result in a new project. In that case, a note with a link will be added in the `README.md` of this project.  

## Dependencies

This project specifies multiple requirements files. 
`requirements.txt` contains the dependencies for the environment to work. These requirements will be installed automatically when installing the environment via `pip`.
`requirements_dev.txt` contains the dependencies for development purposes. It includes the dependencies for testing, linting, and building the project on top of the dependencies in `requirements.txt`.
`requirements_examples.txt` contains the dependencies for running the examples inside the project. It includes the dependencies in `requirements.txt` and additional dependencies for the examples.

In this Project the dependencies are specified in the `pyproject.toml` file with as little version constraints as possible.
The tool `pip-compile` translates the `pyproject.toml` file into a `requirements.txt` file with pinned versions. 
That way version conflicts can be avoided (as much as possible) and the project can be built in a reproducible way.

## Development Setup

If you want to check out the code and implement new features or fix bugs, you can set up the project as follows:

### Clone the Repository

clone the repository in your favorite code editor (for example PyCharm, VSCode, Neovim, etc.)

using https:
```shell
git clone https://github.com/Alexander-Nasuta/GraphMatrixJobShopEnv.git
```
or by using the GitHub CLI:
```shell
gh repo clone Alexander-Nasuta/GraphMatrixJobShopEnv
```

if you are using PyCharm, I recommend doing the following additional steps:

- mark the `src` folder as source root (by right-clicking on the folder and selecting `Mark Directory as` -> `Sources Root`)
- mark the `tests` folder as test root (by right-clicking on the folder and selecting `Mark Directory as` -> `Test Sources Root`)
- mark the `resources` folder as resources root (by right-clicking on the folder and selecting `Mark Directory as` -> `Resources Root`)

at the end your project structure should look like this:

todo

### Create a Virtual Environment (optional)

Most Developers use a virtual environment to manage the dependencies of their projects. 
I personally use `conda` for this purpose.

When using `conda`, you can create a new environment with the name 'my-graph-jsp-env' following command:

```shell
conda create -n my-graph-jsp-env python=3.11
```

Feel free to use any other name for the environment or an more recent version of python.
Activate the environment with the following command:

```shell
conda activate my-graph-jsp-env
```

Replace `my-graph-jsp-env` with the name of your environment, if you used a different name.

You can also use `venv` or `virtualenv` to create a virtual environment. In that case please refer to the respective documentation.

### Install the Dependencies

To install the dependencies for development purposes, run the following command:

```shell
pip install -r requirements_dev.txt
pip install tox
```

The testing package `tox` is not included in the `requirements_dev.txt` file, because it sometimes causes issues when 
using github actions. 
Github Actions uses an own tox environment (namely 'tox-gh-actions'), which can cause conflicts with the tox environment on your local machine.

Reference: [Automated Testing in Python with pytest, tox, and GitHub Actions](https://www.youtube.com/watch?v=DhUpxWjOhME).

### Install the Project in Editable Mode

To install the project in editable mode, run the following command:

```shell
pip install -e .
```

This will install the project in editable mode, so you can make changes to the code and test them immediately.

### Run the Tests

This project uses `pytest` for testing. To run the tests, run the following command:

```shell
pytest
```
Here is a screenshot of what the output might look like:

![](https://github.com/Alexander-Nasuta/GraphMatrixJobShopEnv/raw/master/resources/pytest-screenshot.png)

For testing with `tox` run the following command:

```shell
tox
```

Here is a screenshot of what the output might look like:

![](https://github.com/Alexander-Nasuta/GraphMatrixJobShopEnv/raw/master/resources/tox-screenshot.png)

Tox will run the tests in a separate environment and will also check if the requirements are installed correctly.

### Builing and Publishing the Project to PyPi 

In order to publish the project to PyPi, the project needs to be built and then uploaded to PyPi.

To build the project, run the following command:

```shell
python -m build
```

It is considered good practice use the tool `twine` for checking the build and uploading the project to PyPi.
By default the build command creates a `dist` folder with the built project files.
To check all the files in the `dist` folder, run the following command:

```shell
twine check dist/**
```

If the check is successful, you can upload the project to PyPi with the following command:

```shell
twine upload dist/**
```

### Documentation
This project uses `sphinx` for generating the documentation. 
It also uses a lot of sphinx extensions to make the documentation more readable and interactive.
For example the extension `myst-parser` is used to enable markdown support in the documentation (instead of the usual .rst-files).
It also uses the `sphinx-autobuild` extension to automatically rebuild the documentation when changes are made.
By running the following command, the documentation will be automatically built and served, when changes are made (make sure to run this command in the root directory of the project):

```shell
sphinx-autobuild ./docs/source/ ./docs/build/html/
```

This project features most of the extensions featured in this Tutorial: [Document Your Scientific Project With Markdown, Sphinx, and Read the Docs | PyData Global 2021](https://www.youtube.com/watch?v=qRSb299awB0).



## Contact

If you have any questions or feedback, feel free to contact me via [email](mailto:alexander.nasuta@wzl-iqs.rwth-aachen.de) or open an issue on repository.
