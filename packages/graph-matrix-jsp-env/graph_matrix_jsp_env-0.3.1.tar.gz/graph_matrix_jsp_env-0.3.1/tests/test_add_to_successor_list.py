def list_has_no_duplicates(lst):
    return len(lst) == len(set(lst))


def test_adding_to_successor_list(custom_jsp_instance):
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
        the unknown list is updated using the `add_to_successor_list` method
        the graph matrix is not in a valid state after the update.
        this test is only to check if the method is working as expected

        Successor lists:

        Successor(t_1): [2, 3, 4, 5] # after adding task 5
        Successor(t_2): [3, 4, 6] # after adding task 6
        Successor(t_3): [4, 7, 8] # after adding task 7 and 8
        Successor(t_4): [5, 6, 7] # after adding task 5, 6 and 7
        Successor(t_5): [3, 6, 7, 8] # after adding task 3
        Successor(t_6): [2, 3, 7, 8] # after adding task 2 and 3
        Successor(t_7): [1, 2, 3, 4, 8] # after adding task 1, 2, 3 and 4
        Successor(t_8): [1, 2, 3, 4] # after adding task 1, 2, 3 and 4

        """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, c_lb=0)

    env.remove_task_form_unknown_list(task_id=1, task_to_remove=5)
    env.add_to_successor_list(task_id=1, task_to_add=5)

    successor_list_1 = env.get_successor_list(task_id=1)
    assert (np.array(successor_list_1) == [2, 3, 4, 5]).all(), \
        f"Successor(t_1): {successor_list_1}, but expected [2, 3, 4, 5]"
    assert len(successor_list_1) == 4, \
        f"Successor(t_1): {successor_list_1}, but expected [2, 3, 4, 5]"

    env.remove_task_form_unknown_list(task_id=2, task_to_remove=6)
    env.add_to_successor_list(task_id=2, task_to_add=6)

    successor_list_2 = env.get_successor_list(task_id=2)
    assert (np.array(successor_list_2) == [3, 4, 6]).all(), \
        f"Successor(t_2): {successor_list_2}, but expected [3, 4, 6]"
    assert list_has_no_duplicates(successor_list_2), \
        f"Successor(t_2): {successor_list_2}, but expected [3, 4, 6]"

    env.remove_task_form_unknown_list(task_id=3, task_to_remove=7)
    env.add_to_successor_list(task_id=3, task_to_add=7)

    env.remove_task_form_unknown_list(task_id=3, task_to_remove=8)
    env.add_to_successor_list(task_id=3, task_to_add=8)

    successor_list_3 = env.get_successor_list(task_id=3)
    assert (np.array(successor_list_3) == [4, 7, 8]).all(), \
        f"Successor(t_3): {successor_list_3}, but expected [4, 7, 8]"
    assert list_has_no_duplicates(successor_list_3), \
        f"Successor(t_3): {successor_list_3}, but expected [4, 7, 8]"

    env.remove_task_form_unknown_list(task_id=4, task_to_remove=5)
    env.add_to_successor_list(task_id=4, task_to_add=5)

    env.remove_task_form_unknown_list(task_id=4, task_to_remove=7)
    env.add_to_successor_list(task_id=4, task_to_add=7)

    env.remove_task_form_unknown_list(task_id=4, task_to_remove=6)
    env.add_to_successor_list(task_id=4, task_to_add=6)

    successor_list_4 = env.get_successor_list(task_id=4)
    assert (np.array(successor_list_4) == [5, 6,7]).all(), \
        f"Successor(t_4): {successor_list_4}, but expected [5, 6, 7]"
    assert list_has_no_duplicates(successor_list_4), \
        f"Successor(t_4): {successor_list_4}, but expected [5, 6, 7]"

    env.remove_task_form_unknown_list(task_id=5, task_to_remove=3)
    env.add_to_successor_list(task_id=5, task_to_add=3)
    successor_list_5 = env.get_successor_list(task_id=5)
    assert (np.array(successor_list_5) == [3, 6, 7,8]).all(), \
        f"Successor(t_5): {successor_list_5}, but expected [3, 6, 7, 8]"
    assert list_has_no_duplicates(successor_list_5), \
        f"Successor(t_5): {successor_list_5}, but expected [3, 6, 7, 8]"

    env.remove_task_form_unknown_list(task_id=6, task_to_remove=3)
    env.add_to_successor_list(task_id=6, task_to_add=3)

    env.remove_task_form_unknown_list(task_id=6, task_to_remove=2)
    env.add_to_successor_list(task_id=6, task_to_add=2)

    successor_list_6 = env.get_successor_list(task_id=6)
    assert (np.array(successor_list_6) == [2, 3, 7,8]).all(), \
        f"Successor(t_6): {successor_list_6}, but expected [2, 3, 7, 8]"
    assert list_has_no_duplicates(successor_list_6), \
        f"Successor(t_6): {successor_list_6}, but expected [2, 3, 7, 8]"

    env.remove_task_form_unknown_list(task_id=7, task_to_remove=1)
    env.add_to_successor_list(task_id=7, task_to_add=1)

    env.remove_task_form_unknown_list(task_id=7, task_to_remove=2)
    env.add_to_successor_list(task_id=7, task_to_add=2)

    env.remove_task_form_unknown_list(task_id=7, task_to_remove=3)
    env.add_to_successor_list(task_id=7, task_to_add=3)

    env.remove_task_form_unknown_list(task_id=7, task_to_remove=4)
    env.add_to_successor_list(task_id=7, task_to_add=4)

    successor_list_7 = env.get_successor_list(task_id=7)
    assert (np.array(successor_list_7) == [1, 2, 3, 4, 8]).all(), \
        f"Successor(t_7): {successor_list_7}, but expected [1, 2, 3, 4, 8]"
    assert list_has_no_duplicates(successor_list_7), \
        f"Successor(t_7): {successor_list_7}, but expected [1, 2, 3, 4, 8]"

    env.remove_task_form_unknown_list(task_id=8, task_to_remove=4)
    env.add_to_successor_list(task_id=8, task_to_add=4)

    env.remove_task_form_unknown_list(task_id=8, task_to_remove=1)
    env.add_to_successor_list(task_id=8, task_to_add=1)

    env.remove_task_form_unknown_list(task_id=8, task_to_remove=3)
    env.add_to_successor_list(task_id=8, task_to_add=3)

    env.remove_task_form_unknown_list(task_id=8, task_to_remove=2)
    env.add_to_successor_list(task_id=8, task_to_add=2)

    successor_list_8 = env.get_successor_list(task_id=8)
    assert (np.array(successor_list_8) == [1, 2, 3, 4]).all(), \
        f"Successor(t_8): {successor_list_8}, but expected [1, 2, 3, 4]"
    assert list_has_no_duplicates(successor_list_8), \
        f"Successor(t_8): {successor_list_8}, but expected [1, 2, 3, 4]"

    env.render()
