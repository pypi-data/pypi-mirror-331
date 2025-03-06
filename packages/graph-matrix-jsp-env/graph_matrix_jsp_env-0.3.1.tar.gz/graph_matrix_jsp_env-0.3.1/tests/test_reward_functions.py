def test_machine_utilization_ignore_unused_machines(custom_jsp_instance):
    """
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

    this test is to check if the machine utilisation is calculated correctly.
    I calculate the machine utilisation by hand for every time step and compare it to the calculated machine utilisation

    the environment will perform the following actions (in that order): 5, 1, 2, 6, 3, 7, 4, 8
    """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance,
                                 reward_function='machine_utilization_ignore_unused_machines')

    for action, expected_reward in zip(
            [5, 1, 2, 6, 3, 7, 4, 8],
            [1.0, 1.0, 0.57894737, 0.63993317, 0.6498538, 0.71626984, 0.62053571, 0.63720238]
    ):
        _, reward, *_ = env.step(action)
        eps = 1e-8
        assert abs(reward - expected_reward) < eps


def test_machine_utilization_avg_default_0(custom_jsp_instance):
    """
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

    this test is to check if the machine utilisation is calculated correctly.
    I calculate the machine utilisation by hand for every time step and compare it to the calculated machine utilisation

    the environment will perform the following actions (in that order):

    action:     5,  1,  2,  6,  3,  7,  4,  8

    """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, reward_function='machine_utilization_avg_default_0')

    for action, expected_reward in zip(
            [5, 1, 2, 6, 3, 7, 4, 8],
            [0.25, 0.25, 0.2894736842105263, 0.4799498746867168, 0.48739035087719296, 0.5372023809523809,
             0.6205357142857143, 0.6372023809523809]
    ):
        _, reward, *_ = env.step(action)
        eps = 1e-8
        assert abs(reward - expected_reward) < eps


def test_machine_utilization_avg_default_1(custom_jsp_instance):
    """
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

    this test is to check if the machine utilisation is calculated correctly.
    I calculate the machine utilisation by hand for every time step and compare it to the calculated machine utilisation

    the environment will perform the following actions (in that order):

    action:     5,  1,  2,  6,  3,  7,  4,  8

    """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, reward_function='machine_utilization_avg_default_1')

    for action, expected_reward in zip(
            [5, 1, 2, 6, 3, 7, 4, 8],
            [1.0, 1.0, 0.7894736842105263, 0.7299498746867168, 0.737390350877193, 0.7872023809523809,
             0.6205357142857143, 0.6372023809523809]
    ):
        _, reward, *_ = env.step(action)
        eps = 1e-8
        assert abs(reward - expected_reward) < eps


def test_total_machine_utilization(custom_jsp_instance):
    """
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

    this test is to check if the machine utilisation is calculated correctly.
    I calculate the machine utilisation by hand for every time step and compare it to the calculated machine utilisation

    the environment will perform the following actions (in that order):

    action:     5,  1,  2,  6,  3,  7,  4,  8

    """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, reward_function='total_machine_utilization')

    for action, expected_reward in zip(
            [5, 1, 2, 6, 3, 7, 4, 8],
            [0.25, 0.25, 0.25, 0.4166666666666667, 0.3958333333333333, 0.4017857142857143, 0.3958333333333333, 0.38125]
    ):
        _, reward, *_ = env.step(action)
        eps = 1e-8
        assert abs(reward - expected_reward) < eps


def test_makespan_reward_function(custom_jsp_instance):
    """
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

    this test is to check if the machine utilisation is calculated correctly.
    I calculate the machine utilisation by hand for every time step and compare it to the calculated machine utilisation

    the environment will perform the following actions (in that order):

    action:     5,  1,  2,  6,  3,  7,  4,  8
    reward:     0,  0,  0,  0,  0,  0,  0,-40
    """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance, reward_function='makespan')

    for action, expected_reward in zip(
            [5, 1, 2, 6, 3, 7, 4, 8],
            [0, 0, 0, 0, 0, 0, 0, -40]
    ):
        _, reward, *_ = env.step(action)
        print(f"action: {action}, reward: {reward}, expected reward: {expected_reward}")
        assert reward == expected_reward


def test_makespan_scaled_by_lb_reward_function(custom_jsp_instance):
    """
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

    this test is to check if the machine utilisation is calculated correctly.
    I calculate the machine utilisation by hand for every time step and compare it to the calculated machine utilisation

    the environment will perform the following actions (in that order):

    action:     5,  1,  2,  6,  3,  7,  4,  8
    reward:     0,  0,  0,  0,  0,  0,  0,-40
    """

    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv
    env = DisjunctiveGraphJspEnv(
        jsp_instance=custom_jsp_instance,
        reward_function='makespan_scaled_by_lb',
        c_lb=40
    )

    for action, expected_reward in zip(
            [5, 1, 2, 6, 3, 7, 4, 8],
            [0, 0, 0, 0, 0, 0, 0, -1]
    ):
        _, reward, *_ = env.step(action)
        print(f"action: {action}, reward: {reward}, expected reward: {expected_reward}")
        assert reward == expected_reward

    env = DisjunctiveGraphJspEnv(
        jsp_instance=custom_jsp_instance,
        reward_function='makespan_scaled_by_lb',
        c_lb=20
    )

    for action, expected_reward in zip(
            [5, 1, 2, 6, 3, 7, 4, 8],
            [0, 0, 0, 0, 0, 0, 0, -2]
    ):
        _, reward, *_ = env.step(action)
        print(f"action: {action}, reward: {reward}, expected reward: {expected_reward}")
        assert reward == expected_reward
