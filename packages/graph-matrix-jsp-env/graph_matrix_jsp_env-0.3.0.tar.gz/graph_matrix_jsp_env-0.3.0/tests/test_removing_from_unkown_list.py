def list_has_no_duplicates(lst):
    return len(lst) == len(set(lst))


def test_scheduling_removing_from_unknown_list(custom_jsp_instance):
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

        #
        the unknown list is updated using the `remove_task_form_unknown_list` method
        the graph matrix is not in a valid state after the update.
        this test is only to check if the method is working as expected

        Unknown lists:

        Unknown(t_1): [6, 7, 8] # after removing task 5
        Unknown(t_2): [5, 7, 8] # after removing task 6
        Unknown(t_3): [5, 6, 8] # after removing task 7
        Unknown(t_4): [5, 6, 7] # after removing task 8
        Unknown(t_5): [1, 2, 3] # after removing task 4
        Unknown(t_6): [1, 4] # after removing task 2 and 3
        Unknown(t_7): [3, 4] # after removing task 1 and 2
        Unknown(t_8): [] # after removing task 1, 2, 3, 4

        """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, c_lb=0)

    env.remove_task_form_unknown_list(task_id=1, task_to_remove=5)
    unknown_list_1 = env.get_unknown_list(task_id=1)
    assert (np.array(unknown_list_1) == np.array(
        [6, 7, 8])).all(), f"Unknown(t_1): {unknown_list_1}, but expected [6, 7, 8]"
    assert len(unknown_list_1) == 3, f"Unknown(t_1): {unknown_list_1}, but expected [6, 7, 8]"

    env.remove_task_form_unknown_list(task_id=2, task_to_remove=6)
    unknown_list_2 = env.get_unknown_list(task_id=2)
    assert (np.array(unknown_list_2) == np.array(
        [5, 7, 8])).all(), f"Unknown(t_2): {unknown_list_2}, but expected [5, 7, 8]"
    assert list_has_no_duplicates(unknown_list_2), f"Unknown(t_2): {unknown_list_2}, but expected [5, 7, 8]"

    env.remove_task_form_unknown_list(task_id=3, task_to_remove=7)
    unknown_list_3 = env.get_unknown_list(task_id=3)
    assert (np.array(unknown_list_3) == np.array(
        [5, 6, 8])).all(), f"Unknown(t_3): {unknown_list_3}, but expected [5, 6, 8]"
    assert list_has_no_duplicates(unknown_list_3), f"Unknown(t_3): {unknown_list_3}, but expected [5, 6, 8]"

    env.remove_task_form_unknown_list(task_id=4, task_to_remove=8)
    unknown_list_4 = env.get_unknown_list(task_id=4)
    assert (np.array(unknown_list_4) == np.array(
        [5, 6, 7])).all(), f"Unknown(t_4): {unknown_list_4}, but expected [5, 6, 7]"
    assert list_has_no_duplicates(unknown_list_4), f"Unknown(t_4): {unknown_list_4}, but expected [5, 6, 7]"

    env.remove_task_form_unknown_list(task_id=5, task_to_remove=4)
    unknown_list_5 = env.get_unknown_list(task_id=5)
    assert (np.array(unknown_list_5) == np.array(
        [1, 2, 3])).all(), f"Unknown(t_5): {unknown_list_5}, but expected [1, 2, 3]"
    assert list_has_no_duplicates(unknown_list_5), f"Unknown(t_5): {unknown_list_5}, but expected [1, 2, 3]"

    env.remove_task_form_unknown_list(task_id=6, task_to_remove=2)
    env.remove_task_form_unknown_list(task_id=6, task_to_remove=3)
    unknown_list_6 = env.get_unknown_list(task_id=6)
    assert (np.array(unknown_list_6) == np.array([1, 4])).all(), f"Unknown(t_6): {unknown_list_6}, but expected [1, 4]"
    assert list_has_no_duplicates(unknown_list_6), f"Unknown(t_6): {unknown_list_6}, but expected [1, 4]"

    env.remove_task_form_unknown_list(task_id=7, task_to_remove=1)
    env.remove_task_form_unknown_list(task_id=7, task_to_remove=2)
    unknown_list_7 = env.get_unknown_list(task_id=7)
    assert (np.array(unknown_list_7) == np.array([3, 4])).all(), f"Unknown(t_7): {unknown_list_7}, but expected [3, 4]"
    assert list_has_no_duplicates(unknown_list_7), f"Unknown(t_7): {unknown_list_7}, but expected [3, 4]"

    env.remove_task_form_unknown_list(task_id=8, task_to_remove=4)
    env.remove_task_form_unknown_list(task_id=8, task_to_remove=1)
    env.remove_task_form_unknown_list(task_id=8, task_to_remove=2)
    env.remove_task_form_unknown_list(task_id=8, task_to_remove=3)
    unknown_list_8 = env.get_unknown_list(task_id=8)
    assert (np.array(unknown_list_8) == np.array([])).all(), f"Unknown(t_8): {unknown_list_8}, but expected []"
    assert list_has_no_duplicates(unknown_list_8), f"Unknown(t_8): {unknown_list_8}, but expected []"


def test_scheduling_removing_from_unknown_list_2(custom_jsp_instance):
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

        #
        the unknown list is updated using the `remove_task_form_unknown_list` method
        the graph matrix is not in a valid state after the update.
        this test is only to check if the method is working as expected


        removing tasks Unknown(t_4) in the following order: 5, 7, 6

        Expected unknown list:

        Unknown(t_4): [8]

        """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance)

    env.remove_task_form_unknown_list(task_id=4, task_to_remove=5)
    env.remove_task_form_unknown_list(task_id=4, task_to_remove=7)
    env.remove_task_form_unknown_list(task_id=4, task_to_remove=6)
    unknown_list_4 = env.get_unknown_list(task_id=4)

    env.render(mode='debug')
    assert (np.array(unknown_list_4) == np.array([8])).all(), f"Unknown(t_4): {unknown_list_4}, but expected [8]"
    assert list_has_no_duplicates(unknown_list_4), f"Unknown(t_4): {unknown_list_4}, but expected [8]"
