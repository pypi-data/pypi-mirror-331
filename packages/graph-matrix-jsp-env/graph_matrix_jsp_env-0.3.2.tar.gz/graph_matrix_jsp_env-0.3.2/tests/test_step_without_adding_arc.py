
def test_scheduling_t1_after_init(custom_jsp_instance):
    """
    ○ : no start time assigned yet
    ● : start time assigned

    Graph:
             1         2         3         4
             ●--------→○--------→○--------→○
           ↗                                  ↘
      0  ●                                      ●  9
           ↘                                  ↗
             ○--------→○--------→○--------→○
             5         6         7         8

    Expected graph matrix:
    ┏━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┓
    ┃    ┃  0 ┃  1 ┃  2 ┃  3 ┃  4 ┃  5 ┃  6 ┃  7 ┃  8 ┃  9 ┃  m ┃  d ┃  s ┃  v ┃
    ┣━━━━╋━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━┫
    ┃  0 ┃  0 │  0 │  1 │  2 │  3 │  0 │  5 │  6 │  7 │  0 │  0 │  0 │  0 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  1 ┃  0 │ -5 │ 11 │ 12 │ 12 │ -6 │ -7 │ -8 │ -8 │  2 │  0 │ 11 │  0 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  2 ┃  1 │  1 │ -5 │ 12 │ 12 │ -6 │ -7 │ -8 │ -8 │  3 │  1 │  3 │ -1 │  1 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  3 ┃  1 │  2 │  2 │ -5 │ 12 │ -6 │ -7 │ -8 │ -8 │  4 │  2 │  3 │ -1 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  4 ┃  1 │  2 │  3 │  3 │ -5 │ -6 │ -7 │ -8 │ -8 │  0 │  3 │ 12 │ -1 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  5 ┃  0 │ -2 │ -3 │ -4 │ -4 │ -1 │ 15 │ 16 │ 16 │  6 │  0 │  5 │ -1 │  1 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  6 ┃  5 │ -2 │ -3 │ -4 │ -4 │  5 │ -1 │ 16 │ 16 │  7 │  2 │ 16 │ -1 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  7 ┃  5 │ -2 │ -3 │ -4 │ -4 │  6 │  6 │ -1 │ 16 │  8 │  1 │  7 │ -1 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  8 ┃  5 │ -2 │ -3 │ -4 │ -4 │  6 │  7 │  7 │ -1 │  0 │  3 │  4 │ -1 │  0 ┃
    ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
    ┃  9 ┃  0 │  4 │  4 │  4 │  0 │  8 │  8 │  8 │  0 │  0 │  0 │  0 │  0 │  0 ┃
    ┗━━━━┻━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┛

    Predecessor lists:

    Predecessor(t_1): []
    Predecessor(t_2): [1]
    Predecessor(t_3): [1, 2]
    Predecessor(t_4): [1, 2, 3]
    Predecessor(t_5): []
    Predecessor(t_6): [5]
    Predecessor(t_7): [5, 6]
    Predecessor(t_8): [5, 6, 7]

    Successor lists:

    Successor(t_1): [2, 3, 4]
    Successor(t_2): [3, 4]
    Successor(t_3): [4]
    Successor(t_4): []
    Successor(t_5): [6, 7, 8]
    Successor(t_6): [7, 8]
    Successor(t_7): [8]
    Successor(t_8): []

    Unknown lists:

    Unknown(t_1): [5, 6, 7, 8]
    Unknown(t_2): [5, 6, 7, 8]
    Unknown(t_3): [5, 6, 7, 8]
    Unknown(t_4): [5, 6, 7, 8]
    Unknown(t_5): [1, 2, 3, 4]
    Unknown(t_6): [1, 2, 3, 4]
    Unknown(t_7): [1, 2, 3, 4]
    Unknown(t_8): [1, 2, 3, 4]

    """
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, c_lb=0)
    env.step(1)

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
        [e] + [_ + 0, _ + 1, _ + 2, _ + 3, _ + 0, _ + 5, _ + 6, _ + 7] + [e] + [e, e, e, e],
        # job 0
        [0] + [u * 5, s + 3, s + 4, s + 4, u * 6, u * 7, u * 8, u * 8] + [2] + [0, 11, 0, 0],
        [1] + [p + 1, u * 5, s + 4, s + 4, u * 6, u * 7, u * 8, u * 8] + [3] + [1, 3, -1, 1],
        [1] + [p + 2, p + 2, u * 5, s + 4, u * 6, u * 7, u * 8, u * 8] + [4] + [2, 3, -1, 0],
        [1] + [p + 2, p + 3, p + 3, u * 5, u * 6, u * 7, u * 8, u * 8] + [0] + [3, 12, -1, 0],
        # job 1
        [0] + [u * 2, u * 3, u * 4, u * 4, u * 1, s + 7, s + 8, s + 8] + [6] + [0, 5, -1, 1],
        [5] + [u * 2, u * 3, u * 4, u * 4, p + 5, u * 1, s + 8, s + 8] + [7] + [2, 16, -1, 0],
        [5] + [u * 2, u * 3, u * 4, u * 4, p + 6, p + 6, u * 1, s + 8] + [8] + [1, 7, -1, 0],
        [5] + [u * 2, u * 3, u * 4, u * 4, p + 6, p + 7, p + 7, u * 1] + [0] + [3, 4, -1, 0],
        # footer row
        [e] + [_ + 4, _ + 4, _ + 4, _ + 0, _ + 8, _ + 8, _ + 8, _ + 0] + [e] + [e, e, e, e]
    ]

    assert (np.array(env._state) == np.array(expected_graph_matrix)).all()

    # Predecessor lists
    assert (np.array(env.get_predecessor_list(1)) == np.array(
        [])).all(), f"Predecessor(t_1) is incorrect. expected: [], got: {env.get_predecessor_list(1)}"
    assert (np.array(env.get_predecessor_list(2)) == np.array(
        [1])).all(), f"Predecessor(t_2) is incorrect. expected: [1], got: {env.get_predecessor_list(2)}"
    assert (np.array(env.get_predecessor_list(3)) == np.array(
        [1, 2])).all(), f"Predecessor(t_3) is incorrect. expected: [1, 2], got: {env.get_predecessor_list(3)}"
    assert (np.array(env.get_predecessor_list(4)) == np.array(
        [1, 2, 3])).all(), f"Predecessor(t_4) is incorrect. expected: [1, 2, 3], got: {env.get_predecessor_list(4)}"
    assert (np.array(env.get_predecessor_list(5)) == np.array(
        [])).all(), f"Predecessor(t_5) is incorrect. expected: [], got: {env.get_predecessor_list(5)}"
    assert (np.array(env.get_predecessor_list(6)) == np.array(
        [5])).all(), f"Predecessor(t_6) is incorrect. expected: [5], got: {env.get_predecessor_list(6)}"
    assert (np.array(env.get_predecessor_list(7)) == np.array(
        [5, 6])).all(), f"Predecessor(t_7) is incorrect. expected: [5, 6], got: {env.get_predecessor_list(7)}"
    assert (np.array(env.get_predecessor_list(8)) == np.array(
        [5, 6, 7])).all(), f"Predecessor(t_8) is incorrect. expected: [5, 6, 7], got: {env.get_predecessor_list(8)}"

    # Successor lists
    assert (np.array(env.get_successor_list(1)) == np.array(
        [2, 3, 4])).all(), f"Successor(t_1) is incorrect. expected: [2, 3, 4], got: {env.get_successor_list(1)}"
    assert (np.array(env.get_successor_list(2)) == np.array(
        [3, 4])).all(), f"Successor(t_2) is incorrect. expected: [3, 4], got: {env.get_successor_list(2)}"
    assert (np.array(env.get_successor_list(3)) == np.array(
        [4])).all(), f"Successor(t_3) is incorrect. expected: [4], got: {env.get_successor_list(3)}"
    assert (np.array(env.get_successor_list(4)) == np.array(
        [])).all(), f"Successor(t_4) is incorrect. expected: [], got: {env.get_successor_list(4)}"
    assert (np.array(env.get_successor_list(5)) == np.array(
        [6, 7, 8])).all(), f"Successor(t_5) is incorrect. expected: [6, 7, 8], got: {env.get_successor_list(5)}"
    assert (np.array(env.get_successor_list(6)) == np.array(
        [7, 8])).all(), f"Successor(t_6) is incorrect. expected: [7, 8], got: {env.get_successor_list(6)}"
    assert (np.array(env.get_successor_list(7)) == np.array(
        [8])).all(), f"Successor(t_7) is incorrect. expected: [8], got: {env.get_successor_list(7)}"
    assert (np.array(env.get_successor_list(8)) == np.array(
        [])).all(), f"Successor(t_8) is incorrect. expected: [], got: {env.get_successor_list(8)}"

    # Unknown lists
    assert (np.array(env.get_unknown_list(1)) == np.array(
        [5, 6, 7, 8])).all(), f"Unknown(t_1) is incorrect. expected: [5, 6, 7, 8], got: {env.get_unknown_list(1)}"
    assert (np.array(env.get_unknown_list(2)) == np.array(
        [5, 6, 7, 8])).all(), f"Unknown(t_2) is incorrect. expected: [5, 6, 7, 8], got: {env.get_unknown_list(2)}"
    assert (np.array(env.get_unknown_list(3)) == np.array(
        [5, 6, 7, 8])).all(), f"Unknown(t_3) is incorrect. expected: [5, 6, 7, 8], got: {env.get_unknown_list(3)}"
    assert (np.array(env.get_unknown_list(4)) == np.array(
        [5, 6, 7, 8])).all(), f"Unknown(t_4) is incorrect. expected: [5, 6, 7, 8], got: {env.get_unknown_list(4)}"
    assert (np.array(env.get_unknown_list(5)) == np.array(
        [1, 2, 3, 4])).all(), f"Unknown(t_5) is incorrect. expected: [1, 2, 3, 4], got: {env.get_unknown_list(5)}"
    assert (np.array(env.get_unknown_list(6)) == np.array(
        [1, 2, 3, 4])).all(), f"Unknown(t_6) is incorrect. expected: [1, 2, 3, 4], got: {env.get_unknown_list(6)}"
    assert (np.array(env.get_unknown_list(7)) == np.array(
        [1, 2, 3, 4])).all(), f"Unknown(t_7) is incorrect. expected: [1, 2, 3, 4], got: {env.get_unknown_list(7)}"
    assert (np.array(env.get_unknown_list(8)) == np.array(
        [1, 2, 3, 4])).all(), f"Unknown(t_8) is incorrect. expected: [1, 2, 3, 4], got: {env.get_unknown_list(8)}"


def test_scheduling_t5_after_init(custom_jsp_instance):
    """
        ○ : no start time assigned yet
        ● : start time assigned

        Graph:
                 1         2         3         4
                 ○--------→○--------→○--------→○
               ↗                                  ↘
          0  ●                                      ●  9
               ↘                                  ↗
                 ●--------→○--------→○--------→○
                 5         6         7         8

        Expected graph matrix:
        ┏━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┳━━━━┓
        ┃    ┃  0 ┃  1 ┃  2 ┃  3 ┃  4 ┃  5 ┃  6 ┃  7 ┃  8 ┃  9 ┃  m ┃  d ┃  s ┃  v ┃
        ┣━━━━╋━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━╇━━━━┫
        ┃  0 ┃  0 │  0 │  1 │  2 │  3 │  0 │  5 │  6 │  7 │  0 │  0 │  0 │  0 │  0 ┃
        ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
        ┃  1 ┃  0 │ -5 │ 11 │ 12 │ 12 │ -6 │ -7 │ -8 │ -8 │  2 │  0 │ 11 │ -1 │  1 ┃
        ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
        ┃  2 ┃  1 │  1 │ -5 │ 12 │ 12 │ -6 │ -7 │ -8 │ -8 │  3 │  1 │  3 │ -1 │  0 ┃
        ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
        ┃  3 ┃  1 │  2 │  2 │ -5 │ 12 │ -6 │ -7 │ -8 │ -8 │  4 │  2 │  3 │ -1 │  0 ┃
        ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
        ┃  4 ┃  1 │  2 │  3 │  3 │ -5 │ -6 │ -7 │ -8 │ -8 │  0 │  3 │ 12 │ -1 │  0 ┃
        ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
        ┃  5 ┃  0 │ -2 │ -3 │ -4 │ -4 │ -1 │ 15 │ 16 │ 16 │  6 │  0 │  5 │  0 │  0 ┃
        ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
        ┃  6 ┃  5 │ -2 │ -3 │ -4 │ -4 │  5 │ -1 │ 16 │ 16 │  7 │  2 │ 16 │ -1 │  1 ┃
        ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
        ┃  7 ┃  5 │ -2 │ -3 │ -4 │ -4 │  6 │  6 │ -1 │ 16 │  8 │  1 │  7 │ -1 │  0 ┃
        ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
        ┃  8 ┃  5 │ -2 │ -3 │ -4 │ -4 │  6 │  7 │  7 │ -1 │  0 │  3 │  4 │ -1 │  0 ┃
        ┣━━━━╉────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┨
        ┃  9 ┃  0 │  4 │  4 │  4 │  0 │  8 │  8 │  8 │  0 │  0 │  0 │  0 │  0 │  0 ┃
        ┗━━━━┻━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┛

        Predecessor lists:

        Predecessor(t_1): []
        Predecessor(t_2): [1]
        Predecessor(t_3): [1, 2]
        Predecessor(t_4): [1, 2, 3]
        Predecessor(t_5): []
        Predecessor(t_6): [5]
        Predecessor(t_7): [5, 6]
        Predecessor(t_8): [5, 6, 7]

        Successor lists:

        Successor(t_1): [2, 3, 4]
        Successor(t_2): [3, 4]
        Successor(t_3): [4]
        Successor(t_4): []
        Successor(t_5): [6, 7, 8]
        Successor(t_6): [7, 8]
        Successor(t_7): [8]
        Successor(t_8): []

        Unknown lists:

        Unknown(t_1): [5, 6, 7, 8]
        Unknown(t_2): [5, 6, 7, 8]
        Unknown(t_3): [5, 6, 7, 8]
        Unknown(t_4): [5, 6, 7, 8]
        Unknown(t_5): [1, 2, 3, 4]
        Unknown(t_6): [1, 2, 3, 4]
        Unknown(t_7): [1, 2, 3, 4]
        Unknown(t_8): [1, 2, 3, 4]

        """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, c_lb=0)
    env.step(5)

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
        [e] + [_ + 0, _ + 1, _ + 2, _ + 3, _ + 0, _ + 5, _ + 6, _ + 7] + [e] + [e, e, e, e],
        # job 0
        [0] + [u * 5, s + 3, s + 4, s + 4, u * 6, u * 7, u * 8, u * 8] + [2] + [0, 11, -1, 1],
        [1] + [p + 1, u * 5, s + 4, s + 4, u * 6, u * 7, u * 8, u * 8] + [3] + [1, 3, -1, 0],
        [1] + [p + 2, p + 2, u * 5, s + 4, u * 6, u * 7, u * 8, u * 8] + [4] + [2, 3, -1, 0],
        [1] + [p + 2, p + 3, p + 3, u * 5, u * 6, u * 7, u * 8, u * 8] + [0] + [3, 12, -1, 0],
        # job 1
        [0] + [u * 2, u * 3, u * 4, u * 4, u * 1, s + 7, s + 8, s + 8] + [6] + [0, 5, 0, 0],
        [5] + [u * 2, u * 3, u * 4, u * 4, p + 5, u * 1, s + 8, s + 8] + [7] + [2, 16, -1, 1],
        [5] + [u * 2, u * 3, u * 4, u * 4, p + 6, p + 6, u * 1, s + 8] + [8] + [1, 7, -1, 0],
        [5] + [u * 2, u * 3, u * 4, u * 4, p + 6, p + 7, p + 7, u * 1] + [0] + [3, 4, -1, 0],
        # footer row
        [e] + [_ + 4, _ + 4, _ + 4, _ + 0, _ + 8, _ + 8, _ + 8, _ + 0] + [e] + [e, e, e, e]
    ]

    assert (np.array(env._state) == np.array(expected_graph_matrix)).all()

    # Predecessor lists
    assert (np.array(env.get_predecessor_list(1)) == np.array(
        [])).all(), f"Predecessor(t_1) is incorrect. expected: [], got: {env.get_predecessor_list(1)}"
    assert (np.array(env.get_predecessor_list(2)) == np.array(
        [1])).all(), f"Predecessor(t_2) is incorrect. expected: [1], got: {env.get_predecessor_list(2)}"
    assert (np.array(env.get_predecessor_list(3)) == np.array(
        [1, 2])).all(), f"Predecessor(t_3) is incorrect. expected: [1, 2], got: {env.get_predecessor_list(3)}"
    assert (np.array(env.get_predecessor_list(4)) == np.array(
        [1, 2, 3])).all(), f"Predecessor(t_4) is incorrect. expected: [1, 2, 3], got: {env.get_predecessor_list(4)}"
    assert (np.array(env.get_predecessor_list(5)) == np.array(
        [])).all(), f"Predecessor(t_5) is incorrect. expected: [], got: {env.get_predecessor_list(5)}"
    assert (np.array(env.get_predecessor_list(6)) == np.array(
        [5])).all(), f"Predecessor(t_6) is incorrect. expected: [5], got: {env.get_predecessor_list(6)}"
    assert (np.array(env.get_predecessor_list(7)) == np.array(
        [5, 6])).all(), f"Predecessor(t_7) is incorrect. expected: [5, 6], got: {env.get_predecessor_list(7)}"
    assert (np.array(env.get_predecessor_list(8)) == np.array(
        [5, 6, 7])).all(), f"Predecessor(t_8) is incorrect. expected: [5, 6, 7], got: {env.get_predecessor_list(8)}"

    # Successor lists
    assert (np.array(env.get_successor_list(1)) == np.array(
        [2, 3, 4])).all(), f"Successor(t_1) is incorrect. expected: [2, 3, 4], got: {env.get_successor_list(1)}"
    assert (np.array(env.get_successor_list(2)) == np.array(
        [3, 4])).all(), f"Successor(t_2) is incorrect. expected: [3, 4], got: {env.get_successor_list(2)}"
    assert (np.array(env.get_successor_list(3)) == np.array(
        [4])).all(), f"Successor(t_3) is incorrect. expected: [4], got: {env.get_successor_list(3)}"
    assert (np.array(env.get_successor_list(4)) == np.array(
        [])).all(), f"Successor(t_4) is incorrect. expected: [], got: {env.get_successor_list(4)}"
    assert (np.array(env.get_successor_list(5)) == np.array(
        [6, 7, 8])).all(), f"Successor(t_5) is incorrect. expected: [6, 7, 8], got: {env.get_successor_list(5)}"
    assert (np.array(env.get_successor_list(6)) == np.array(
        [7, 8])).all(), f"Successor(t_6) is incorrect. expected: [7, 8], got: {env.get_successor_list(6)}"
    assert (np.array(env.get_successor_list(7)) == np.array(
        [8])).all(), f"Successor(t_7) is incorrect. expected: [8], got: {env.get_successor_list(7)}"
    assert (np.array(env.get_successor_list(8)) == np.array(
        [])).all(), f"Successor(t_8) is incorrect. expected: [], got: {env.get_successor_list(8)}"

    # Unknown lists
    assert (np.array(env.get_unknown_list(1)) == np.array(
        [5, 6, 7, 8])).all(), f"Unknown(t_1) is incorrect. expected: [5, 6, 7, 8], got: {env.get_unknown_list(1)}"
    assert (np.array(env.get_unknown_list(2)) == np.array(
        [5, 6, 7, 8])).all(), f"Unknown(t_2) is incorrect. expected: [5, 6, 7, 8], got: {env.get_unknown_list(2)}"
    assert (np.array(env.get_unknown_list(3)) == np.array(
        [5, 6, 7, 8])).all(), f"Unknown(t_3) is incorrect. expected: [5, 6, 7, 8], got: {env.get_unknown_list(3)}"
    assert (np.array(env.get_unknown_list(4)) == np.array(
        [5, 6, 7, 8])).all(), f"Unknown(t_4) is incorrect. expected: [5, 6, 7, 8], got: {env.get_unknown_list(4)}"
    assert (np.array(env.get_unknown_list(5)) == np.array(
        [1, 2, 3, 4])).all(), f"Unknown(t_5) is incorrect. expected: [1, 2, 3, 4], got: {env.get_unknown_list(5)}"
    assert (np.array(env.get_unknown_list(6)) == np.array(
        [1, 2, 3, 4])).all(), f"Unknown(t_6) is incorrect. expected: [1, 2, 3, 4], got: {env.get_unknown_list(6)}"
    assert (np.array(env.get_unknown_list(7)) == np.array(
        [1, 2, 3, 4])).all(), f"Unknown(t_7) is incorrect. expected: [1, 2, 3, 4], got: {env.get_unknown_list(7)}"
    assert (np.array(env.get_unknown_list(8)) == np.array(
        [1, 2, 3, 4])).all(), f"Unknown(t_8) is incorrect. expected: [1, 2, 3, 4], got: {env.get_unknown_list(8)}"