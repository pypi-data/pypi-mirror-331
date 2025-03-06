def test_is_in_predecessor_list(custom_jsp_instance):
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

    Predecessor lists:

    Predecessor(t_1): []
    Predecessor(t_2): [1]
    Predecessor(t_3): [1, 2]
    Predecessor(t_4): [1, 2, 3]
    Predecessor(t_5): []
    Predecessor(t_6): [5]
    Predecessor(t_7): [5, 6]
    Predecessor(t_8): [5, 6, 7]
    """
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, c_lb=0)

    for t in range(1, 9):
        predecessor_list = env.get_predecessor_list(task_id=t)
        for pred_t in predecessor_list:
            assert env.is_in_predecessor_list(task_id=t, task_to_check=pred_t)
            assert not env.is_in_successor_list(task_id=t, task_to_check=pred_t)
            assert pred_t not in env.get_unknown_list(task_id=t)
