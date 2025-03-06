def list_has_no_duplicates(lst):
    return len(lst) == len(set(lst))


def test_adding_to_predecessor_list(custom_jsp_instance):
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
        the unknown list is updated using the `add_to_predecessor_list` method
        the graph matrix is not in a valid state after the update.
        this test is only to check if the method is working as expected

        Predecessor lists:

        Predecessor(t_1): [5] # after adding task 5
        Predecessor(t_2): [1, 5] # after adding task 5
        Predecessor(t_3): [1, 2, 5, 6] # after adding task 6 and 5
        Predecessor(t_4): [1, 2, 3, 5, 6, 7] # after adding task 5, 6 and 7
        Predecessor(t_5): [1, 2, 3, 4] # after adding task 2, 3, 4 and 1
        Predecessor(t_6): [1, 2, 3, 4, 5] # after adding task 4, 3, 2 and 1
        Predecessor(t_7): [1, 2, 3, 4, 5, 6] # after adding task 4, 1, 2 and 3
        Predecessor(t_8): [1, 2, 3, 4, 5, 6, 7] # after adding task 3, 1, 4 and 2

        """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, c_lb=0)

    env.remove_task_form_unknown_list(task_id=1, task_to_remove=5)
    env.add_to_predecessor_list(task_id=1, task_to_add=5)

    predecessor_list_1 = env.get_predecessor_list(task_id=1)
    assert (np.array(predecessor_list_1) == [5]).all(), \
        f"Predecessor(t_1): {predecessor_list_1}, but expected [5]"
    assert len(predecessor_list_1) == 1, \
        f"Predecessor(t_1): {predecessor_list_1}, but expected [5]"

    env.remove_task_form_unknown_list(task_id=2, task_to_remove=5)
    env.add_to_predecessor_list(task_id=2, task_to_add=5)

    predecessor_list_2 = env.get_predecessor_list(task_id=2)
    assert (np.array(predecessor_list_2) == [1, 5]).all(), \
        f"Predecessor(t_2): {predecessor_list_2}, but expected [1, 5]"
    assert list_has_no_duplicates(predecessor_list_2), \
        f"Predecessor(t_2): {predecessor_list_2}, but expected [1, 5]"

    env.remove_task_form_unknown_list(task_id=3, task_to_remove=6)
    env.add_to_predecessor_list(task_id=3, task_to_add=6)

    env.remove_task_form_unknown_list(task_id=3, task_to_remove=5)
    env.add_to_predecessor_list(task_id=3, task_to_add=5)

    predecessor_list_3 = env.get_predecessor_list(task_id=3)
    assert (np.array(predecessor_list_3) == [1, 2, 5, 6]).all(), \
        f"Predecessor(t_3): {predecessor_list_3}, but expected [1, 2, 5, 6]"
    assert list_has_no_duplicates(predecessor_list_3), \
        f"Predecessor(t_3): {predecessor_list_3}, but expected [1, 2, 5, 6]"

    env.remove_task_form_unknown_list(task_id=4, task_to_remove=5)
    env.add_to_predecessor_list(task_id=4, task_to_add=5)

    env.remove_task_form_unknown_list(task_id=4, task_to_remove=6)
    env.add_to_predecessor_list(task_id=4, task_to_add=6)

    env.remove_task_form_unknown_list(task_id=4, task_to_remove=7)
    env.add_to_predecessor_list(task_id=4, task_to_add=7)

    predecessor_list_4 = env.get_predecessor_list(task_id=4)
    assert (np.array(predecessor_list_4) == [1, 2, 3, 5, 6, 7]).all(), \
        f"Predecessor(t_4): {predecessor_list_4}, but expected [1, 2, 3, 5, 6, 7]"
    assert list_has_no_duplicates(predecessor_list_4), \
        f"Predecessor(t_4): {predecessor_list_4}, but expected [1, 2, 3, 5, 6, 7]"

    env.remove_task_form_unknown_list(task_id=5, task_to_remove=1)
    env.add_to_predecessor_list(task_id=5, task_to_add=1)

    env.remove_task_form_unknown_list(task_id=5, task_to_remove=2)
    env.add_to_predecessor_list(task_id=5, task_to_add=2)

    env.remove_task_form_unknown_list(task_id=5, task_to_remove=3)
    env.add_to_predecessor_list(task_id=5, task_to_add=3)

    env.remove_task_form_unknown_list(task_id=5, task_to_remove=4)
    env.add_to_predecessor_list(task_id=5, task_to_add=4)

    predecessor_list_5 = env.get_predecessor_list(task_id=5)
    assert (np.array(predecessor_list_5) == [1, 2, 3, 4]).all(), \
        f"Predecessor(t_5): {predecessor_list_5}, but expected [1, 2, 3, 4]"
    assert list_has_no_duplicates(predecessor_list_5), \
        f"Predecessor(t_5): {predecessor_list_5}, but expected [1, 2, 3, 4]"

    env.remove_task_form_unknown_list(task_id=6, task_to_remove=4)
    env.add_to_predecessor_list(task_id=6, task_to_add=4)

    env.remove_task_form_unknown_list(task_id=6, task_to_remove=3)
    env.add_to_predecessor_list(task_id=6, task_to_add=3)

    env.remove_task_form_unknown_list(task_id=6, task_to_remove=2)
    env.add_to_predecessor_list(task_id=6, task_to_add=2)

    env.remove_task_form_unknown_list(task_id=6, task_to_remove=1)
    env.add_to_predecessor_list(task_id=6, task_to_add=1)

    predecessor_list_6 = env.get_predecessor_list(task_id=6)
    assert (np.array(predecessor_list_6) == [1, 2, 3, 4, 5]).all(), \
        f"Predecessor(t_6): {predecessor_list_6}, but expected [1, 2, 3, 4, 5]"
    assert list_has_no_duplicates(predecessor_list_6), \
        f"Predecessor(t_6): {predecessor_list_6}, but expected [1, 2, 3, 4, 5]"

    env.remove_task_form_unknown_list(task_id=7, task_to_remove=4)
    env.add_to_predecessor_list(task_id=7, task_to_add=4)

    env.remove_task_form_unknown_list(task_id=7, task_to_remove=1)
    env.add_to_predecessor_list(task_id=7, task_to_add=1)

    env.remove_task_form_unknown_list(task_id=7, task_to_remove=2)
    env.add_to_predecessor_list(task_id=7, task_to_add=2)

    env.remove_task_form_unknown_list(task_id=7, task_to_remove=3)
    env.add_to_predecessor_list(task_id=7, task_to_add=3)

    predecessor_list_7 = env.get_predecessor_list(task_id=7)
    assert (np.array(predecessor_list_7) == [1, 2, 3, 4, 5, 6]).all(), \
        f"Predecessor(t_7): {predecessor_list_7}, but expected [1, 2, 3, 4, 5, 6]"
    assert list_has_no_duplicates(predecessor_list_7), \
        f"Predecessor(t_7): {predecessor_list_7}, but expected [1, 2, 3, 4, 5, 6]"

    env.remove_task_form_unknown_list(task_id=8, task_to_remove=3)
    env.add_to_predecessor_list(task_id=8, task_to_add=3)

    env.remove_task_form_unknown_list(task_id=8, task_to_remove=1)
    env.add_to_predecessor_list(task_id=8, task_to_add=1)

    env.remove_task_form_unknown_list(task_id=8, task_to_remove=4)
    env.add_to_predecessor_list(task_id=8, task_to_add=4)

    env.remove_task_form_unknown_list(task_id=8, task_to_remove=2)
    env.add_to_predecessor_list(task_id=8, task_to_add=2)

    predecessor_list_8 = env.get_predecessor_list(task_id=8)
    assert (np.array(predecessor_list_8) == [1, 2, 3, 4, 5, 6, 7]).all(), \
        f"Predecessor(t_8): {predecessor_list_8}, but expected [1, 2, 3, 4, 5, 6, 7]"
    assert list_has_no_duplicates(predecessor_list_8), \
        f"Predecessor(t_8): {predecessor_list_8}, but expected [1, 2, 3, 4, 5, 6, 7]"

    env.render()
