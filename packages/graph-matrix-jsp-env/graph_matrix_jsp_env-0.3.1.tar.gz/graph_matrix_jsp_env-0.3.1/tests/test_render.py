import pytest
import sys

@pytest.mark.skipif(sys.platform == "win32", reason="Causes troubles with windows gitlab runner.")
def test_render_mode_human(custom_jsp_instance, ft06, left_shift_jsp_instance):
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv

    for instance in [custom_jsp_instance, ft06, left_shift_jsp_instance]:
        env = DisjunctiveGraphJspEnv(jsp_instance=instance)
        env.render(mode='human')

@pytest.mark.skipif(sys.platform == "win32", reason="Causes troubles with windows gitlab runner.")
def test_render_mode_debug(custom_jsp_instance, ft06, left_shift_jsp_instance):
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv

    for instance in [custom_jsp_instance, ft06, left_shift_jsp_instance]:
        env = DisjunctiveGraphJspEnv(jsp_instance=instance)
        env.render(mode='debug')


@pytest.mark.skipif(sys.platform == "win32", reason="Causes troubles with windows gitlab runner.")
def test_random_action_and_render(custom_jsp_instance, ft06, left_shift_jsp_instance):
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    for instance in [custom_jsp_instance, ft06, left_shift_jsp_instance]:
        env = DisjunctiveGraphJspEnv(jsp_instance=instance)
        _ = env.reset()
        terminal = False
        while not terminal:
            action = env.action_space.sample(mask=env.valid_action_mask())
            _, _, terminal, *_ = env.step(action)
            env.render(mode='human')
            env.render(mode='debug')
            assert type(env.render(mode='rgb_array')) == np.ndarray
            env.render(mode='ansi')
