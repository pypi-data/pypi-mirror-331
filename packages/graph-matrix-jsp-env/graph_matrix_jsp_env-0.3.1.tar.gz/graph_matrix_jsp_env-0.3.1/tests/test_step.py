def test_fully_scheduled(custom_jsp_instance):
    """↖ ↑ ↗ ← · →↙ ↓ ↘⟋
    ○ : no start time assigned yet
    ● : start time assigned

    Graph:
             1         2         3         4
             ●--------→●--------→●--------→●
           ↗ ↑           ⟍     ↗          |  ↘
      0  ●   |              ✕             |     ●  9
           ↘ |           ⟋     ↘          ↓  ↗
             ●--------→●--------→●--------→●
             5         6         7         8

    Expected graph matrix:

    ┏━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┓
    ┃    ┃  0 ┃  1 ┃  2 ┃  3 ┃  4 ┃  5 ┃  6 ┃  7 ┃  8 ┃  9 ┃  m ┃  d ┃  s ┃  v ┃
    ┣━━━━╋━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━┫
    ┃  0 ┃  0 │  5 │  5 │  6 │  6 │  0 │  5 │  6 │  7 │  0 │  0 │  0 │  0 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  1 ┃  5 │ -6 │ 11 │ 12 │ 15 │  5 │ -6 │ 16 │ 16 │  2 │  0 │ 11 │  5 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  2 ┃  1 │  5 │ -6 │ 12 │ 15 │  5 │ -6 │ 16 │ 16 │  3 │  1 │  3 │ 16 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  3 ┃  1 │  2 │  5 │ -7 │ 16 │  6 │  6 │ -7 │ 16 │  4 │  2 │  3 │ 21 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  4 ┃  1 │  2 │  3 │  5 │ -7 │  6 │  6 │ -7 │ 16 │  8 │  3 │ 12 │ 24 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  5 ┃  0 │ 10 │ 11 │ 12 │ 14 │ -5 │ 15 │ 16 │ 16 │  1 │  0 │  5 │  0 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  6 ┃  5 │ -2 │ -2 │ 12 │ 15 │  5 │ -1 │ 16 │ 16 │  3 │  2 │ 16 │  5 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  7 ┃  1 │  2 │  5 │ -4 │ -4 │  6 │  6 │ -3 │ 16 │  8 │  1 │  7 │ 21 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  8 ┃  1 │  2 │  3 │  4 │  5 │  6 │  7 │  7 │ -8 │  0 │  3 │  4 │ 36 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  9 ┃  0 │  8 │  8 │  8 │  8 │  8 │  8 │  8 │  0 │  0 │  0 │  0 │  0 │  0 ┃
    ┗━━━━┻━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┛

    Predecessor lists:

    Predecessor(t_1): [5]
    Predecessor(t_2): [1, 5]
    Predecessor(t_3): [1, 2, 5, 6]
    Predecessor(t_4): [1, 2, 3, 5, 6]
    Predecessor(t_5): []
    Predecessor(t_6): [5]
    Predecessor(t_7): [1, 2, 5, 6]
    Predecessor(t_8): [1, 2, 3, 4, 5, 6, 7]

    Successor lists:

    Successor(t_1): [2, 3, 4, 7, 8]
    Successor(t_2): [3, 4, 7, 8]
    Successor(t_3): [4, 8]
    Successor(t_4): [8]
    Successor(t_5): [1, 2, 3, 4, 6, 7, 8]
    Successor(t_6): [3, 4, 7, 8]
    Successor(t_7): [8]
    Successor(t_8): []

    Unknown lists:

    Unknown(t_1): [6]
    Unknown(t_2): [6]
    Unknown(t_3): [7]
    Unknown(t_4): [7]
    Unknown(t_5): []
    Unknown(t_6): [1, 2]
    Unknown(t_7): [3, 4]
    Unknown(t_8): []

    """
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, c_lb=0)

    e = 0  # placeholder for empty cell

    # these values are just used to calculate the expected graph matrix
    # the symbols help me to keep track of what a specific cell represents
    # and help with formatting for code editing
    s = 8  # successor
    p = 0  # predecessor
    u = -1  # unknown
    _ = 0
    expected_graph_matrix = [
        # header row
        [e] + [_ + 5, _ + 5, _ + 6, _ + 6, _ + 0, _ + 5, _ + 6, _ + 7] + [e] + [e, e, e, e],
        # job 0
        [5] + [u * 6, s + 3, s + 4, s + 7, p + 5, u * 6, s + 8, s + 8] + [2] + [0, 11, 5, 0],
        [1] + [p + 5, u * 6, s + 4, s + 7, p + 5, u * 6, s + 8, s + 8] + [3] + [1, 3, 16, 0],
        [1] + [p + 2, p + 5, u * 7, s + 8, p + 6, p + 6, u * 7, s + 8] + [4] + [2, 3, 21, 0],
        [1] + [p + 2, p + 3, p + 5, u * 7, p + 6, p + 6, u * 7, s + 8] + [8] + [3, 12, 24, 0],
        # job 1
        [0] + [s + 2, s + 3, s + 4, s + 6, u * 5, s + 7, s + 8, s + 8] + [1] + [0, 5, 0, 0],
        [5] + [u * 2, u * 2, s + 4, s + 7, p + 5, u * 1, s + 8, s + 8] + [3] + [2, 16, 5, 0],
        [1] + [p + 2, p + 5, u * 4, u * 4, p + 6, p + 6, u * 3, s + 8] + [8] + [1, 7, 21, 0],
        [1] + [p + 2, p + 3, p + 4, p + 5, p + 6, p + 7, p + 7, u * 8] + [0] + [3, 4, 36, 0],
        # footer row
        [e] + [_ + 8, _ + 8, _ + 8, _ + 8, _ + 8, _ + 8, _ + 8, _ + 0] + [e] + [e, e, e, e]
    ]

    for a in [5, 1, 2, 6, 3, 7, 4, 8]:
        env.step(a)

    assert (np.array(env._state) == np.array(expected_graph_matrix)).all()


def test_partial_scheduling(custom_jsp_instance):
    """
    ○ : no start time assigned yet
    ● : start time assigned

    Graph:
             1         2         3         4
             ●--------→●--------→●--------→○
           ↗ |                 ⟋             ↘
      0  ●   |              ⟋                  ●  9
           ↘ ↓           ↙                   ↗
             ●--------→●--------→○--------→○
             5         6         7         8

    Expected graph matrix:

    Predecessor lists:

    Predecessor(t_1): []
    Predecessor(t_2): [1]
    Predecessor(t_3): [1, 2]
    Predecessor(t_4): [1, 2, 3]
    Predecessor(t_5): [1]
    Predecessor(t_6): [1, 2, 3, 5]
    Predecessor(t_7): [1, 2, 3, 5, 6]
    Predecessor(t_8): [1, 2, 3, 5, 6, 7]

    Successor lists:

    Successor(t_1): [2, 3, 4, 5, 6, 7, 8]
    Successor(t_2): [3, 4, 6, 7, 8]
    Successor(t_3): [4, 6, 7, 8]
    Successor(t_4): []
    Successor(t_5): [6, 7, 8]
    Successor(t_6): [7, 8]
    Successor(t_7): [8]
    Successor(t_8): []

    Unknown lists:

    Unknown(t_1): []
    Unknown(t_2): [5]
    Unknown(t_3): [5]
    Unknown(t_4): [5, 6, 7, 8]
    Unknown(t_5): [2, 3, 4]
    Unknown(t_6): [4]
    Unknown(t_7): [4]
    Unknown(t_8): [4]

    """
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, c_lb=0)

    for a in [1, 5, 2, 3, 6]:
        env.step(a)

    # test predecessor lists
    def elementwise_equality_check_using_numpy(task_id, is_list, should_list):
        assert (np.array(is_list) == np.array(
            should_list)).all(), f"Predecessor(t_{task_id}) is incorrect. expected: {should_list}, got: {is_list}"

    elementwise_equality_check_using_numpy(1, env.get_predecessor_list(1), [])
    elementwise_equality_check_using_numpy(2, env.get_predecessor_list(2), [1])
    elementwise_equality_check_using_numpy(3, env.get_predecessor_list(3), [1, 2])
    elementwise_equality_check_using_numpy(4, env.get_predecessor_list(4), [1, 2, 3])
    elementwise_equality_check_using_numpy(5, env.get_predecessor_list(5), [1])
    elementwise_equality_check_using_numpy(6, env.get_predecessor_list(6), [1, 2, 3, 5])
    elementwise_equality_check_using_numpy(7, env.get_predecessor_list(7), [1, 2, 3, 5, 6])
    elementwise_equality_check_using_numpy(8, env.get_predecessor_list(8), [1, 2, 3, 5, 6, 7])

    # test successor lists
    elementwise_equality_check_using_numpy(1, env.get_successor_list(1), [2, 3, 4, 5, 6, 7, 8])
    elementwise_equality_check_using_numpy(2, env.get_successor_list(2), [3, 4, 6, 7, 8])
    elementwise_equality_check_using_numpy(3, env.get_successor_list(3), [4, 6, 7, 8])
    elementwise_equality_check_using_numpy(4, env.get_successor_list(4), [])
    elementwise_equality_check_using_numpy(5, env.get_successor_list(5), [6, 7, 8])
    elementwise_equality_check_using_numpy(6, env.get_successor_list(6), [7, 8])
    elementwise_equality_check_using_numpy(7, env.get_successor_list(7), [8])
    elementwise_equality_check_using_numpy(8, env.get_successor_list(8), [])

    # test unknown lists
    elementwise_equality_check_using_numpy(1, env.get_unknown_list(1), [])
    elementwise_equality_check_using_numpy(2, env.get_unknown_list(2), [5])
    elementwise_equality_check_using_numpy(3, env.get_unknown_list(3), [5])
    elementwise_equality_check_using_numpy(4, env.get_unknown_list(4), [5, 6, 7, 8])
    elementwise_equality_check_using_numpy(5, env.get_unknown_list(5), [2, 3, 4])
    elementwise_equality_check_using_numpy(6, env.get_unknown_list(6), [4])
    elementwise_equality_check_using_numpy(7, env.get_unknown_list(7), [4])
    elementwise_equality_check_using_numpy(8, env.get_unknown_list(8), [4])


def test_random_actions_custom_instance(custom_jsp_instance):
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance)
    terminal = False
    for _ in range(8):
        action = env.action_space.sample(mask=env.valid_action_mask())
        _, _, terminal, _, _ = env.step(action)
    assert terminal

    env.reset()
    terminal = False
    for _ in range(8):
        action = env.valid_action_list()[0]
        _, _, terminal, _, _ = env.step(action)
    assert terminal


def test_random_actions_ft06(ft06):
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    env = DisjunctiveGraphJspEnv(jsp_instance=ft06)
    terminal = False
    for _ in range(36):
        action = env.action_space.sample(mask=env.valid_action_mask())
        _, _, terminal, _, _ = env.step(action)
    assert terminal

    env.reset()
    terminal = False
    for _ in range(36):
        action = env.valid_action_list()[0]
        _, _, terminal, _, _ = env.step(action)
    assert terminal
