import copy
import numpy as np


def test_load_state(env):
    env = env

    terminal = False
    reset_obs, _ = env.reset()

    env_copy = copy.deepcopy(env)

    for _ in range(36):
        action = env.action_space.sample(mask=env.valid_action_mask())

        obs, reward, terminal, _, _ = env.step(action)
        obs_copy, reward_copy, terminal_copy, _, _ = env.step(action)

        assert np.array_equal(obs, obs_copy)
        assert reward == reward_copy
        assert terminal == terminal_copy

        reset_copy_obs, _ = env_copy.reset()

        assert np.array_equal(reset_obs, reset_copy_obs)

        env_copy.load_state(obs)

    assert terminal


def test_load_state_ft06(python_env_ft06):

    for i in range(10):
        env = python_env_ft06

        terminal = False
        reset_obs, _ = env.reset()

        env_copy = copy.deepcopy(env)

        for _ in range(36):
            action = env.action_space.sample(mask=env.valid_action_mask())

            obs, reward, terminal, _, _ = env.step(action)
            obs_copy, reward_copy, terminal_copy, _, _ = env.step(action)

            assert np.array_equal(obs, obs_copy)
            assert reward == reward_copy
            assert terminal == terminal_copy

            reset_copy_obs, _ = env_copy.reset()

            assert np.array_equal(reset_obs, reset_copy_obs)

            env_copy.load_state(obs)

        assert terminal
