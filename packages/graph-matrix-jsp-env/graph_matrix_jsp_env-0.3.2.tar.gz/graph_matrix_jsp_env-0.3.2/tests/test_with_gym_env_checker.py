def test_with_sb3_env_checker(custom_jsp_instance):
    from stable_baselines3.common.env_checker import check_env
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv

    env = DisjunctiveGraphJspEnv(jsp_instance=custom_jsp_instance)
    check_env(env)


def test_with_sb3_env_checker_ft06(ft06):
    from stable_baselines3.common.env_checker import check_env
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv

    env = DisjunctiveGraphJspEnv(jsp_instance=ft06)
    check_env(env)


def test_with_sb3_env_checker_single_job_instance(single_job_jsp_instance):
    from stable_baselines3.common.env_checker import check_env
    from graph_matrix_jsp_env.disjunctive_jsp_env import DisjunctiveGraphJspEnv

    env = DisjunctiveGraphJspEnv(jsp_instance=single_job_jsp_instance)
    check_env(env)
