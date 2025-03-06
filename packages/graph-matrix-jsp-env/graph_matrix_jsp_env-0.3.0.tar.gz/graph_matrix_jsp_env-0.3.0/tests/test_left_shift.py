import pytest


@pytest.mark.skipif(reason="Needs to be updated")
def test_left_shifts(left_shift_jsp_instance):
    """
    ○ : no start time assigned yet
    ● : start time assigned

    the initial situation can be constructed by calling the step with the following actions: 1, 4, 2, 5

    Graph of initial situation:
              1        2         3
              ●-------→●--------→○
            ↗   ⟍                   ⟍
         ⟋        ⟍                   ⟍
       ⟋      4      ↘  5        6       ↘
    0 ●-------→●-------→●--------→○--------→●
       ⟍                                 ↗
         ⟍                            ⟋
            ↘                      ⟋
              ○-------→○--------→○
              7        8         9

    Graph after left shift:

              1        2         3
              ●-------→●--------→○
            ↗ |                     ⟍
         ⟋    |                       ⟍
       ⟋      |4        5         6      ↘
    0 ●-------→●-------→●--------→○--------→● 10
       ⟍      |      ↗                   ↗
         ⟍    |   ⟋                   ⟋
            ↘ ↓ ⟋                   ⟋
              ●-------→○--------→○
              7        8         9

    the Graph after left shift (after calling step with action 7) should look the same as appllying the following
    actions sequence: 1, 4, 7, 2, 5

    After the left shift the predecessor-, successor- and unknown-lists should look like this:

    Predecessor lists:

    Predecessor(t_1): []
    Predecessor(t_2): [1]
    Predecessor(t_3): [1, 2]
    Predecessor(t_4): []
    Predecessor(t_5): [1, 4, 7]
    Predecessor(t_6): [1, 4, 5, 7]
    Predecessor(t_7): [1]
    Predecessor(t_8): [1, 7]
    Predecessor(t_9): [1, 7, 8]

    Successor lists:

    Successor(t_1): [2, 3, 5, 6, 7, 8, 9]
    Successor(t_2): [3]
    Successor(t_3): []
    Successor(t_4): [5, 6]
    Successor(t_5): [6]
    Successor(t_6): []
    Successor(t_7): [5, 6, 8, 9]
    Successor(t_8): [9]
    Successor(t_9): []

    Unknown lists:

    Unknown(t_1): [4]
    Unknown(t_2): [4, 5, 6, 7, 8, 9]
    Unknown(t_3): [4, 5, 6, 7, 8, 9]
    Unknown(t_4): [1, 2, 3, 7, 8, 9]
    Unknown(t_5): [2, 3, 8, 9]
    Unknown(t_6): [2, 3, 8, 9]
    Unknown(t_7): [2, 3, 4]
    Unknown(t_8): [2, 3, 4, 5, 6]
    Unknown(t_9): [2, 3, 4, 5, 6]

    """
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=left_shift_jsp_instance, ls_enabled=False)
    obs_without_left_shift = None
    for a in [1, 4, 7, 2, 5]:
        obs_without_left_shift, *_ = env.step(action=a)
    env.render(mode='debug')

    # test predecessor lists
    assert (np.array(env.get_predecessor_list(1)) == np.array([])).all(), \
        f"Predecessor(t_1) is incorrect. expected: [], got: {env.get_predecessor_list(1)}"
    assert (np.array(env.get_predecessor_list(2)) == np.array([1])).all(), \
        f"Predecessor(t_2) is incorrect. expected: [1], got: {env.get_predecessor_list(2)}"
    assert (np.array(env.get_predecessor_list(3)) == np.array([1, 2])).all(), \
        f"Predecessor(t_3) is incorrect. expected: [1, 2], got: {env.get_predecessor_list(3)}"
    assert (np.array(env.get_predecessor_list(4)) == np.array([])).all(), \
        f"Predecessor(t_4) is incorrect. expected: [], got: {env.get_predecessor_list(4)}"
    assert (np.array(env.get_predecessor_list(5)) == np.array([1, 4, 7])).all(), \
        f"Predecessor(t_5) is incorrect. expected: [1, 4, 7], got: {env.get_predecessor_list(5)}"
    assert (np.array(env.get_predecessor_list(6)) == np.array([1, 4, 5, 7])).all(), \
        f"Predecessor(t_6) is incorrect. expected: [1, 4, 5, 7], got: {env.get_predecessor_list(6)}"
    assert (np.array(env.get_predecessor_list(7)) == np.array([1])).all(), \
        f"Predecessor(t_7) is incorrect. expected: [1], got: {env.get_predecessor_list(7)}"
    assert (np.array(env.get_predecessor_list(8)) == np.array([1, 7])).all(), \
        f"Predecessor(t_8) is incorrect. expected: [1, 7], got: {env.get_predecessor_list(8)}"
    assert (np.array(env.get_predecessor_list(9)) == np.array([1, 7, 8])).all(), \
        f"Predecessor(t_9) is incorrect. expected: [1, 7, 8], got: {env.get_predecessor_list(9)}"

    # test successor lists
    assert (np.array(env.get_successor_list(1)) == np.array([2, 3, 5, 6, 7, 8, 9])).all(), \
        f"Successor(t_1) is incorrect. expected: [2, 3, 5, 6, 7, 8, 9], got: {env.get_successor_list(1)}"
    assert (np.array(env.get_successor_list(2)) == np.array([3])).all(), \
        f"Successor(t_2) is incorrect. expected: [3], got: {env.get_successor_list(2)}"
    assert (np.array(env.get_successor_list(3)) == np.array([])).all(), \
        f"Successor(t_3) is incorrect. expected: [], got: {env.get_successor_list(3)}"
    assert (np.array(env.get_successor_list(4)) == np.array([5, 6])).all(), \
        f"Successor(t_4) is incorrect. expected: [5, 6], got: {env.get_successor_list(4)}"
    assert (np.array(env.get_successor_list(5)) == np.array([6])).all(), \
        f"Successor(t_5) is incorrect. expected: [6], got: {env.get_successor_list(5)}"
    assert (np.array(env.get_successor_list(6)) == np.array([])).all(), \
        f"Successor(t_6) is incorrect. expected: [], got: {env.get_successor_list(6)}"
    assert (np.array(env.get_successor_list(7)) == np.array([5, 6, 8, 9])).all(), \
        f"Successor(t_7) is incorrect. expected: [5, 6, 8, 9], got: {env.get_successor_list(7)}"
    assert (np.array(env.get_successor_list(8)) == np.array([9])).all(), \
        f"Successor(t_8) is incorrect. expected: [9], got: {env.get_successor_list(8)}"
    assert (np.array(env.get_successor_list(9)) == np.array([])).all(), \
        f"Successor(t_9) is incorrect. expected: [], got: {env.get_successor_list(9)}"

    # test unknown lists
    assert (np.array(env.get_unknown_list(1)) == np.array([4])).all(), \
        f"Unknown(t_1) is incorrect. expected: [4], got: {env.get_unknown_list(1)}"
    assert (np.array(env.get_unknown_list(2)) == np.array([4, 5, 6, 7, 8, 9])).all(), \
        f"Unknown(t_2) is incorrect. expected: [4, 5, 6, 7, 8, 9], got: {env.get_unknown_list(2)}"
    assert (np.array(env.get_unknown_list(3)) == np.array([4, 5, 6, 7, 8, 9])).all(), \
        f"Unknown(t_3) is incorrect. expected: [4, 5, 6, 7, 8, 9], got: {env.get_unknown_list(3)}"
    assert (np.array(env.get_unknown_list(4)) == np.array([1, 2, 3, 7, 8, 9])).all(), \
        f"Unknown(t_4) is incorrect. expected: [1, 2, 3, 7, 8, 9], got: {env.get_unknown_list(4)}"
    assert (np.array(env.get_unknown_list(5)) == np.array([2, 3, 8, 9])).all(), \
        f"Unknown(t_5) is incorrect. expected: [2, 3, 8, 9], got: {env.get_unknown_list(5)}"
    assert (np.array(env.get_unknown_list(6)) == np.array([2, 3, 8, 9])).all(), \
        f"Unknown(t_6) is incorrect. expected: [2, 3, 8, 9], got: {env.get_unknown_list(6)}"
    assert (np.array(env.get_unknown_list(7)) == np.array([2, 3, 4])).all(), \
        f"Unknown(t_7) is incorrect. expected: [2, 3, 4], got: {env.get_unknown_list(7)}"
    assert (np.array(env.get_unknown_list(8)) == np.array([2, 3, 4, 5, 6])).all(), \
        f"Unknown(t_8) is incorrect. expected: [2, 3, 4, 5, 6], got: {env.get_unknown_list(8)}"
    assert (np.array(env.get_unknown_list(9)) == np.array([2, 3, 4, 5, 6])).all(), \
        f"Unknown(t_9) is incorrect. expected: [2, 3, 4, 5, 6], got: {env.get_unknown_list(9)}"

    env = DisjunctiveGraphJspEnv(jsp_instance=left_shift_jsp_instance, ls_enabled=True)
    obs_with_left_shift = None
    for a in [1, 4, 2, 5, 7]:
        obs_with_left_shift, *_ = env.step(action=a)
        env.render(mode='debug')
    env.render(mode='debug')

    assert (obs_with_left_shift == obs_without_left_shift).all()


@pytest.mark.skipif(reason="Needs to be updated")
def test_left_shifts2(left_shift_jsp_instance2):
    """
    todo text

    """
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=left_shift_jsp_instance2, ls_enabled=False)
    obs_without_left_shift = None
    # for a in [7, 1, 4, 7, 2, 5]:
    #   obs_without_left_shift, *_ = env.step(action=a)
    # env.render(mode='debug')

    env = DisjunctiveGraphJspEnv(jsp_instance=left_shift_jsp_instance2, ls_enabled=False)
    obs_with_left_shift = None
    env.render(mode='debug')
    for a in [7, 1, 2, 4, 5, 8]:
        obs_with_left_shift, *_ = env.step(action=a)
        env.render(mode='debug')
    env.render(mode='debug')

    # assert (obs_with_left_shift == obs_without_left_shift).all()
