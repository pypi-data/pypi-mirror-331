def test_is_in_successor_list(custom_jsp_instance):
    """
    ○ : no start time assigned yet
    ● : start time assigned

    Graph:
             1         2         3         4
             ○--------→○--------→○--------→○
           ↗                                  ↘
      0  ●                                      ●  9
           ↘                                  ↗
             ○--------→○--------→○--------→○
             5         6         7         8

    Successor lists:

    Successor(t_1): [2, 3, 4]
    Successor(t_2): [3, 4]
    Successor(t_3): [4]
    Successor(t_4): []
    Successor(t_5): [6, 7, 8]
    Successor(t_6): [7, 8]
    Successor(t_7): [8]
    Successor(t_8): []
    """
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, c_lb=0)

    for t in range(1, 9):
        successor_list = env.get_successor_list(task_id=t)
        for succ_t in successor_list:
            assert env.is_in_successor_list(task_id=t, task_to_check=succ_t)
            assert not env.is_in_predecessor_list(task_id=t, task_to_check=succ_t)
            assert succ_t not in env.get_unknown_list(task_id=t)

