import gymnasium as gym
import numpy as np
import pandas as pd
import numpy.typing as npt
import copy

from graph_matrix_jsp_env.logger import log

from typing import Any, SupportsFloat

from graph_matrix_jsp_env.visualisation import print_graph_matrix_to_console
from jsp_vis.console import gantt_chart_console
from jsp_vis.cv2_window import render_gantt_in_window
from jsp_vis.rgb_array import gantt_chart_rgb_array


class DisjunctiveGraphJspEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'debug', 'ansi', 'window', 'rgb_array'],
        'render_modes': ['human', 'debug', 'ansi', 'window', 'rgb_array']
    }

    """
    Attributes                                                    
    """
    # the graph matrix
    # _state: list[list[int]]
    _state: npt.NDArray  # 2d array of integers
    # the number of tasks in the jsp instance (without the source and sink tasks)
    _n: int
    # the number of tasks in the graph matrix including the source and sink tasks
    _n_with_dummies: int
    # the number of columns in the graph matrix
    _no_matrix_columns: int
    # special nodes the graph matrix
    _src_task: int
    _sink_task: int
    # column and row names of the graph matrix
    _predecessor_list_first_elem_col_idx: int
    _predecessor_list_last_elem_row_idx: int

    _successor_list_first_elem_col_idx: int
    _successor_list_last_elem_row_idx: int

    _task_duration_column_idx: int
    _task_machine_column_idx: int
    _valid_action_column_idx: int

    # information about the jsp instance
    _jsp_instance: npt.NDArray
    _n_jobs: int
    _n_machines: int

    # settings
    _makespan_lower_bound: int
    _left_shifts_enabled: bool
    _reward_function: str
    _valid_reward_functions = [
        "makespan",
        "makespan_scaled_by_lb",
        "machine_utilization_ignore_unused_machines",
        "machine_utilization_avg_default_0",
        "machine_utilization_avg_default_1",
        "total_machine_utilization",
        "mcts",
    ]

    """
    Initialization of the environment
    """

    def __init__(self, jsp_instance: npt.NDArray = None, *,
                 c_lb: int = None,
                 ls_enabled: bool = True,
                 reward_function: str = "machine_utilization_ignore_unused_machines"
                 ):
        self._jsp_instance = jsp_instance
        _, n_jobs, n_machines = jsp_instance.shape
        self._n_jobs = n_jobs
        self._n_machines = n_machines
        self._n = n_jobs * n_machines
        self._n_with_dummies = self._n + 2

        self._src_task = 0
        self._sink_task = self._n + 1

        self._no_matrix_columns = self._n + 6

        self._predecessor_list_first_elem_col_idx = 0
        self._predecessor_list_last_elem_row_idx = 0

        self._successor_list_first_elem_col_idx = self._n + 1
        self._successor_list_last_elem_row_idx = self._n + 1

        self._task_machine_column_idx = self._n + 2
        self._task_duration_column_idx = self._n + 3
        self._task_start_time_column_idx = self._n + 4
        self._valid_action_column_idx = self._n + 5

        self._makespan_lower_bound = c_lb if c_lb is not None else self._get_simple_makespan_lower_bound(
            jsp_instance=jsp_instance)
        self._left_shifts_enabled = False # TODO: ls_enabled -> fix left shift bugs
        self._reward_function = reward_function

        # gym attributes
        # the action space is the set of all tasks plus the dummy action 0
        # the dummy action 0 is just included in the action space to make the action space effectively 1-indexed
        # so that action=1 corresponds to scheduling t_1, action=2 corresponds to scheduling t_2, ...
        self.action_space = gym.spaces.Discrete(self._n + 1)
        self.observation_space = gym.spaces.Box(
            low=-self._n,
            high=max(self._n * 2, jsp_instance.max(), self._makespan_lower_bound),
            shape=(self._n_with_dummies, self._no_matrix_columns),
            dtype=int
        )

        self._initialize_matrix()

    def _initialize_matrix(self, jsp_instance: npt.NDArray = None) -> None:
        log.debug("Initializing the matrix")

        if jsp_instance is None:
            jsp_instance = self._jsp_instance

        machine_order = jsp_instance[0]
        processing_times = jsp_instance[1]

        # create the matrix with correct dimensions and fill it with zeros
        self._state = np.array([
            [0 for _ in range(self._no_matrix_columns)]
            for _ in range(self._n_with_dummies)
        ])
        # write lower bound to the 00 position
        self._state[0][0] = self._makespan_lower_bound

        # fill the matrix with the jsp instance data
        for job_idx in range(self._n_jobs):
            first_task_in_job = 1 + job_idx * self._n_machines
            last_task_in_job = job_idx * self._n_machines + self._n_machines

            # list of tasks in the job
            current_job_tasks = list(range(first_task_in_job, last_task_in_job + 1))

            # list of all tasks in the jsp instance, that are not in the current job
            unknown_list = list([
                t
                for t in range(1, self._n + 1)
                if t not in current_job_tasks
            ])

            for task_within_job_idx in range(self._n_machines):
                # NOTE: task_within_job_idx is indexed from 0
                # task_id is the index of the task in the graph matrix
                task_id = 1 + job_idx * self._n_machines + task_within_job_idx

                # set duration of the task
                self._state[task_id][self._task_duration_column_idx] = processing_times[job_idx][task_within_job_idx]
                # set machine of the task
                self._state[task_id][self._task_machine_column_idx] = machine_order[job_idx][task_within_job_idx]
                # set start time of the task
                self._state[task_id][self._task_start_time_column_idx] = -1  # -1 means not start time assigned yet

                # init predecessor list and valid action column
                if task_within_job_idx == 0:
                    # 0 indicates that the task has no predecessors
                    # the source task is implicitly the predecessor
                    # since the source task is the predecessor of all tasks
                    self._state[task_id][self._predecessor_list_first_elem_col_idx] = 0
                    self._state[self._predecessor_list_last_elem_row_idx][task_id] = 0

                    # tasks are scheduled 'left to right' in the graph
                    # the first task of each job is initially a valid action
                    self._state[task_id][self._valid_action_column_idx] = 1
                else:
                    # all other tasks are not valid actions initially
                    self._state[task_id][self._valid_action_column_idx] = 0

                    last_job_predecessor = max(first_task_in_job, task_id - 1)
                    self._state[task_id][self._predecessor_list_first_elem_col_idx] = first_task_in_job
                    self._state[self._predecessor_list_last_elem_row_idx][task_id] = last_job_predecessor

                    for k in range(first_task_in_job, last_job_predecessor):
                        self._state[task_id][k] = k + 1
                    self._state[task_id][last_job_predecessor] = last_job_predecessor

                # init successor list
                if task_within_job_idx == self._n_machines - 1:
                    # case: last task in job

                    # 0 indicates that the task has no successors
                    # the sink task is implicitly the successor
                    # since the sink task is the successor of all tasks
                    self._state[task_id][self._successor_list_first_elem_col_idx] = 0
                    self._state[self._successor_list_last_elem_row_idx][task_id] = 0
                else:
                    # min() is used to cover the case of the last task in the job
                    first_successor_after_current_task = min(last_task_in_job, task_id + 1)
                    self._state[task_id][self._successor_list_first_elem_col_idx] = first_successor_after_current_task
                    self._state[self._successor_list_last_elem_row_idx][task_id] = last_task_in_job

                    for k in range(first_successor_after_current_task, last_task_in_job):
                        self._state[task_id][k] = k + 1 + self._n
                    self._state[task_id][last_task_in_job] = last_task_in_job + self._n

                # init unknown list
                if unknown_list:
                    self._state[task_id][task_id] = -unknown_list[0]
                    for a, b in zip(unknown_list, unknown_list[1:]):
                        self._state[task_id][a] = -b
                    self._state[task_id][unknown_list[-1]] = -unknown_list[-1]
                else:
                    self._state[task_id][task_id] = -task_id

    """
    Gym Environment Methods
    """

    def step(self, action: int) -> (npt.NDArray, SupportsFloat, bool, bool, dict[str, Any]):
        if action == 0:
            # ignore action 0
            # action 0 is only included in the action space, so that a action always corresponds to a task id
            # action=1 corresponds to task id 1, action=2 corresponds to task id 2, ...
            return np.array(self._state), 0.0, self.is_terminal_state(), False, {}

        if self._state[action][self._valid_action_column_idx] == 0:
            # case: action is invalid
            return np.array(self._state), self.calculate_reward(), self.is_terminal_state(), False, {}

        # case: action is valid
        # case: action is the first task on a machine
        machine = self.get_machine_of_task(task_id=action)
        last_task_on_machine: int | None = self.last_scheduled_task_on_machine(machine_id=machine)
        job_predecessor: int | None = self.get_last_predecessor_within_job(task_id=action)
        if last_task_on_machine is None:
            # case: machine is empty
            self._update_valid_actions(task_id=action)
            self._update_start_time(task_id=action, machine_predecessor=last_task_on_machine,
                                    job_predecessor=job_predecessor)
            return np.array(self._state), self.calculate_reward(), self.is_terminal_state(), False, {}

        # check if a left shift is possible
        if self._left_shifts_enabled:
            ls_possible, ls_prev_task, ls_next_task = self.is_left_shift_possible(task_to_schedule=action)
            if ls_possible:
                self.perform_left_shift(task_to_schedule=action, prev_task=ls_prev_task, next_task=ls_next_task)
                self._update_valid_actions(task_id=action)
                self._update_start_time(task_id=action, machine_predecessor=ls_prev_task,
                                        job_predecessor=job_predecessor)
                return np.array(self._state), self.calculate_reward(), self.is_terminal_state(), False, {}

        # case: machine is not empty
        # since the machine is not empty a new arc in the graph has to be introduced
        self.add_arch_to_graph(from_t_id=last_task_on_machine, to_t_id=action)
        # adjust valid action column
        self._update_valid_actions(task_id=action)
        # adjust start time of the task
        self._update_start_time(task_id=action, machine_predecessor=last_task_on_machine,
                                job_predecessor=job_predecessor)

        return np.array(self._state), self.calculate_reward(), self.is_terminal_state(), False, {}

    def reset(self, **kwargs) -> (npt.NDArray, dict[str, Any]):
        super().reset(**kwargs)
        self._initialize_matrix(jsp_instance=self._jsp_instance)
        return np.array(self._state), {}

    def render(self, mode='human', wait=1) -> npt.NDArray | None:
        if mode == 'human':
            gantt_chart_console(self._state_as_gant_dataframes(), n_machines=self._n_machines)
        elif mode == 'ansi':
            print_graph_matrix_to_console(self._state, self._n_machines)
            gantt_chart_console(self._state_as_gant_dataframes(), n_machines=self._n_machines)
        elif mode == 'debug':
            print_graph_matrix_to_console(self._state, self._n_machines, undo_task_encoding=True)
            gantt_chart_console(self._state_as_gant_dataframes(), n_machines=self._n_machines)
        elif mode == 'window':
            render_gantt_in_window(self._state_as_gant_dataframes(), n_machines=self._n_machines, wait=wait)
        elif mode == 'rgb_array':
            return gantt_chart_rgb_array(self._state_as_gant_dataframes(), n_machines=self._n_machines)

    def calculate_reward(self, reward_function: str = None) -> SupportsFloat:
        if reward_function is None:
            reward_function = self._reward_function
        if reward_function not in self._valid_reward_functions:
            raise ValueError(f"Invalid reward function: {reward_function}. "
                             f"Valid reward functions are: {self._valid_reward_functions}")
        if reward_function == "makespan":
            return - self.get_makespan() if self.is_terminal_state() else 0

        if reward_function == "makespan_scaled_by_lb":
            return - self.get_makespan() / self._makespan_lower_bound if self.is_terminal_state() else 0

        if reward_function == "mcts":
            return - self.get_makespan() / self._makespan_lower_bound + 2 if self.is_terminal_state() else 0

        if reward_function == "machine_utilization_ignore_unused_machines":
            return self.get_machine_utilization_ignore_unused_machines()

        if reward_function == "machine_utilization_avg_default_0":
            return self.get_machine_utilization_average_default_0()

        if reward_function == "machine_utilization_avg_default_1":
            return self.get_machine_utilization_average_default_1()

        if reward_function == "total_machine_utilization":
            return self.get_total_machine_utilization()

    """
    Methods to manipulate the environment state (the graph matrix)
    """

    def _update_valid_actions(self, task_id: int) -> None:
        # mark action task as invalid
        self._state[task_id][self._valid_action_column_idx] = 0
        # mark next task in the job as valid
        next_task_in_job = task_id + 1
        # special case: last task in job
        if next_task_in_job % self._n_machines == 1:
            pass  # do nothing
        else:
            self._state[next_task_in_job][self._valid_action_column_idx] = 1

    def _update_start_time(self, task_id: int, machine_predecessor: int | None, job_predecessor: int | None) -> None:
        machine_ready_time = (self._state[machine_predecessor][self._task_start_time_column_idx] +
                              self._state[machine_predecessor][
                                  self._task_duration_column_idx]) if machine_predecessor is not None else 0
        job_ready_time = (self._state[job_predecessor][self._task_start_time_column_idx] + self._state[job_predecessor][
            self._task_duration_column_idx]) if job_predecessor is not None else 0
        start_time = max(machine_ready_time, job_ready_time)
        self._state[task_id][self._task_start_time_column_idx] = start_time

    def perform_left_shift(self, task_to_schedule: int, prev_task: int, next_task: int) -> None:
        # arc prev_task -> task_to_schedule
        self.add_arch_to_graph(from_t_id=prev_task, to_t_id=task_to_schedule)
        # arc task_to_schedule -> next_task
        self.add_arch_to_graph(from_t_id=task_to_schedule, to_t_id=next_task)

    def add_arch_to_graph(self, from_t_id: int, to_t_id: int) -> None:

        # NOTE: make sure to always adjust the Unknown list first before adjusting the Predecessor and Successor lists

        # removing to_t_id from Unknown(from_t_id) list
        # self.remove_task_form_unknown_list(task_id=from_t_id, task_to_remove=to_t_id)
        # adding to_t_id to Successor(from_t_id) list
        # self.add_to_successor_list(task_id=from_t_id, task_to_add=to_t_id)
        # removing from_t_id from Unknown(to_t_id) list
        # self.remove_task_form_unknown_list(task_id=to_t_id, task_to_remove=from_t_id)
        # adding from_t_id to Predecessor(to_t_id) list
        # self.add_to_predecessor_list(task_id=to_t_id, task_to_add=from_t_id)

        # add from_t_id and predecessor-lisf of from_t_id to predecessor-lists of all successors of to_t_id
        for form_elem in [from_t_id] + self.get_predecessor_list(task_id=from_t_id):

            for succ_t_id in [to_t_id] + self.get_successor_list(task_id=to_t_id):
                if self.is_in_predecessor_list(task_id=succ_t_id, task_to_check=form_elem):
                    # case: from_t_id is already in the predecessor list of succ_t_id
                    continue

                self.remove_task_form_unknown_list(task_id=succ_t_id, task_to_remove=form_elem)
                self.add_to_predecessor_list(task_id=succ_t_id, task_to_add=form_elem)
                # and vice versa
                self.remove_task_form_unknown_list(task_id=form_elem, task_to_remove=succ_t_id)
                self.add_to_successor_list(task_id=form_elem, task_to_add=succ_t_id)

        # add to_t_id and  successor-lists of to_t_id to successor-lists of all predecessors of from_t_id
        for to_elem in [to_t_id] + self.get_successor_list(task_id=to_t_id):
            for pred_t_id in [from_t_id] + self.get_predecessor_list(task_id=from_t_id):
                if self.is_in_successor_list(task_id=pred_t_id, task_to_check=to_elem):
                    # case: to_t_id is already in the successor list of pred_t_id
                    continue
                self.remove_task_form_unknown_list(task_id=pred_t_id, task_to_remove=to_elem)
                self.add_to_successor_list(task_id=pred_t_id, task_to_add=to_elem)
                # and vice versa
                self.remove_task_form_unknown_list(task_id=to_elem, task_to_remove=pred_t_id)
                self.add_to_predecessor_list(task_id=to_elem, task_to_add=pred_t_id)

    def add_to_predecessor_list(self, task_id: int, task_to_add: int) -> None:
        # sanity check
        if task_to_add in self.get_predecessor_list(task_id):
            raise ValueError(f"{task_to_add=} is already in the predecessor list of task {task_id=}")
        if task_to_add in self.get_unknown_list(task_id):
            raise ValueError(f"{task_to_add=} is in the unknown list of task {task_id=}. "
                             f"remove it from the unknown list first by calling remove_task_form_unknown_list()")

        # case task_id has no predecessors
        if self._state[task_id][self._predecessor_list_first_elem_col_idx] == 0:
            # task_to_add is the first and last element in the predecessor list
            self._state[task_id][self._predecessor_list_first_elem_col_idx] = task_to_add
            # let task_to_add point to itself
            self._state[task_id][task_to_add] = task_to_add
            # since task_id had no predecessors, task_id is now also the last element in the predecessor list
            self._state[self._predecessor_list_last_elem_row_idx][task_id] = task_to_add
            return

        # the predecessor list is sorted in ascending order
        # task_to_add needs to be inserted in the correct position

        if task_to_add < self._state[task_id][self._predecessor_list_first_elem_col_idx]:
            # case: task_to_add is smaller than the first element in the predecessor list
            # task_to_add will be the new first element in the predecessor list
            # let task_to_add point to the old first element
            self._state[task_id][task_to_add] = self._state[task_id][self._predecessor_list_first_elem_col_idx]
            # update the first element in the predecessor list
            self._state[task_id][self._predecessor_list_first_elem_col_idx] = task_to_add
            return

        if task_to_add > self._state[self._predecessor_list_last_elem_row_idx][task_id]:
            # case: task_to_add is greater than the last element in the predecessor list
            # task_to_add will be the new last element in the predecessor list
            old_last_elem = self._state[self._predecessor_list_last_elem_row_idx][task_id]
            assert 0 < old_last_elem <= self._n, f"{old_last_elem=} is not in the range of 1 to {self._n}"
            # let the old last element point to task_to_add
            self._state[task_id][old_last_elem] = task_to_add
            # let task_to_add point to itself
            self._state[task_id][task_to_add] = task_to_add
            # update the last element in the predecessor list
            self._state[self._predecessor_list_last_elem_row_idx][task_id] = task_to_add
            return

        # case: task_to_add is in the middle of the predecessor list
        # iterate through the predecessor list of task_id to find the element before task_to_add
        k = self._state[task_id][self._predecessor_list_first_elem_col_idx]
        assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
        while True:
            if self._state[task_id][k] > task_to_add:
                break
            k = self._state[task_id][k]
            assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"

        # case: k is the element before task_to_add
        # let task_to_add point to the element after k
        self._state[task_id][task_to_add] = self._state[task_id][k]
        # let k point to task_to_add
        self._state[task_id][k] = task_to_add
        return

    def add_to_successor_list(self, task_id: int, task_to_add: int) -> None:
        # sanity check
        if task_to_add in self.get_successor_list(task_id):
            raise ValueError(f"{task_to_add=} is already in the successor list of task {task_id=}")
        if task_to_add in self.get_unknown_list(task_id):
            raise ValueError(f"{task_to_add=} is in the unknown list of task {task_id=}. "
                             f"remove it from the unknown list first by calling remove_task_form_unknown_list()")

        # case task_id has no successors
        if self._state[task_id][self._successor_list_first_elem_col_idx] == 0:
            # task_to_add is the first and last element in the successor list
            # NOTE: the values in the col self._successor_list_first_elem_col_idx are not shifted by self._n
            self._state[task_id][self._successor_list_first_elem_col_idx] = task_to_add
            # let task_to_add point to itself
            self._state[task_id][task_to_add] = task_to_add + self._n
            # since task_id had no successors, task_id is now also the last element in the successor list
            # NOTE: the values in the row self._successor_list_last_elem_row_idx are not shifted by self._n
            self._state[self._successor_list_last_elem_row_idx][task_id] = task_to_add
            return

        # the successor list is sorted in ascending order
        # task_to_add needs to be inserted in the correct position

        if task_to_add < self._state[task_id][self._successor_list_first_elem_col_idx]:
            # case: task_to_add is smaller than the first element in the successor list
            # task_to_add will be the new first element in the successor list
            # let task_to_add point to the old first element
            self._state[task_id][task_to_add] = self._state[task_id][self._successor_list_first_elem_col_idx] + self._n
            # update the first element in the successor list
            # NOTE: the values in the col self._successor_list_first_elem_col_idx are not shifted by self._n
            self._state[task_id][self._successor_list_first_elem_col_idx] = task_to_add
            return

        if task_to_add > self._state[self._successor_list_last_elem_row_idx][task_id]:
            # case: task_to_add is greater than the last element in the successor list
            # task_to_add will be the new last element in the successor list
            old_last_elem = self._state[self._successor_list_last_elem_row_idx][task_id]
            assert 0 < old_last_elem <= self._n, f"{old_last_elem=} is not in the range of 1 to {self._n}"
            # let the old last element point to task_to_add
            self._state[task_id][old_last_elem] = task_to_add + self._n
            # let task_to_add point to itself
            self._state[task_id][task_to_add] = task_to_add + self._n
            # update the last element in the successor list
            # NOTE: the values in the row self._successor_list_last_elem_row_idx are not shifted by self._n
            self._state[self._successor_list_last_elem_row_idx][task_id] = task_to_add
            return

        # case: task_to_add is in the middle of the successor list
        # iterate through the successor list of task_id to find the element before task_to_add
        k = self._state[task_id][self._successor_list_first_elem_col_idx]
        assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
        while True:
            if self._state[task_id][k] - self._n > task_to_add:
                break
            k = self._state[task_id][k] - self._n
            assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
        # case: k is the element before task_to_add
        # let task_to_add point to the element after k
        self._state[task_id][task_to_add] = self._state[task_id][
            k]  # NOTE: the entry in self._state[task_id][k] is already shifted by self._n
        # let k point to task_to_add
        self._state[task_id][k] = task_to_add + self._n
        return

    def remove_task_form_unknown_list(self, task_id: int, task_to_remove: int) -> None:
        # sanity check
        if task_to_remove not in self.get_unknown_list(task_id):
            raise ValueError(f"{task_to_remove=} is not in the unknown list of task {task_id=}")

        # case: task_to_remove is the first task in the unknown list
        if self._state[task_id][task_id] == -task_to_remove:

            if self._state[task_id][task_to_remove] == -task_to_remove:
                # case: task_to_remove is the only task in the unknown list
                self._state[task_id][task_id] = -task_id
                return
            else:
                # case: task_to_remove is not the only task in the unknown list
                next_task = -self._state[task_id][task_to_remove]
                assert 0 < next_task <= self._n, f"{next_task=} is not in the range of 1 to {self._n}"
                self._state[task_id][task_id] = -next_task
                return
        # case: task_to_remove is not the first task in the unknown list

        # iterate through the unknown list of task_id to find the element before task_id_to_remove
        k = -self._state[task_id][task_id]
        assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
        while self._state[task_id][k] != -task_to_remove:
            k = -self._state[task_id][k]
            assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
        # case: k is the element before task_to_remove
        if self._state[task_id][task_to_remove] == -task_to_remove:
            # case: task_to_remove is the last element in the unknown list
            # k is the new last element in the unknown list
            # let k point to itself
            # this indicates that k is the last element in the unknown list
            self._state[task_id][k] = -k
            return
        else:
            # case: task_to_remove is not the last element in the unknown list
            # k points to task_to_remove
            # let k point to the element after task_to_remove
            next_task = -self._state[task_id][task_to_remove]
            assert 0 < next_task <= self._n, f"{next_task=} is not in the range of 1 to {self._n}"
            self._state[task_id][k] = -next_task
            return

    """
    Methods to access the environment state (the graph matrix)
    """

    def is_terminal_state(self) -> bool:
        for row in self._state[1:-1]:
            if row[self._task_start_time_column_idx] == -1:
                return False
        return True

    def get_machine_of_task(self, task_id: int) -> int:
        assert 0 < task_id <= self._n, f"{task_id=} is not in the range of 1 to {self._n}"
        return self._state[task_id][self._task_machine_column_idx]

    def get_last_predecessor_within_job(self, task_id: int) -> int | None:
        return task_id - 1 if task_id % self._n_machines != 1 else None

    def is_in_predecessor_list(self, task_id: int, task_to_check: int) -> bool:
        # assume the predecessor list is sorted in ascending order

        # case: predecessor list is empty
        if self._state[task_id][self._predecessor_list_first_elem_col_idx] == 0:
            return False

        # case: task_to_check is larger than the last element in the predecessor list
        if task_to_check > self._state[self._predecessor_list_last_elem_row_idx][task_id]:
            return False

        # case: task_to_check is smaller than the first element in the predecessor list
        if task_to_check < self._state[task_id][self._predecessor_list_first_elem_col_idx]:
            return False

        # case task_to_check is the last element in the predecessor list
        if self._state[self._predecessor_list_last_elem_row_idx][task_id] == task_to_check:
            return True

        # case task_to_check is the first element in the predecessor list
        if self._state[task_id][self._predecessor_list_first_elem_col_idx] == task_to_check:
            return True

        # case: task_to_check might be in the middle of the predecessor list
        k = self._state[task_id][self._predecessor_list_first_elem_col_idx]
        while k != self._state[task_id][k]:
            k = self._state[task_id][k]
            if k == task_to_check:
                return True
        return False

    def is_in_successor_list(self, task_id: int, task_to_check: int) -> bool:
        # assume the successor list is sorted in ascending order

        # case: successor list is empty
        if self._state[task_id][self._successor_list_first_elem_col_idx] == 0:
            return False

        # case: task_to_check is larger than the last element in the successor list
        if task_to_check > self._state[self._successor_list_last_elem_row_idx][task_id]:
            return False

        # case: task_to_check is smaller than the first element in the successor list
        if task_to_check < self._state[task_id][self._successor_list_first_elem_col_idx]:
            return False

        # case task_to_check is the last element in the successor list
        if self._state[self._successor_list_last_elem_row_idx][task_id] == task_to_check:
            return True

        # case task_to_check is the first element in the successor list
        if self._state[task_id][self._successor_list_first_elem_col_idx] == task_to_check:
            return True

        # case: task_to_check might be in the middle of the successor list
        k = self._state[task_id][self._successor_list_first_elem_col_idx]
        while k != self._state[task_id][k] - self._n:
            k = self._state[task_id][k] - self._n
            assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
            if k == task_to_check:
                return True
        return False

    def last_scheduled_task_on_machine(self, machine_id: int) -> int | None:
        assert 0 <= machine_id < self._n_machines, f"{machine_id=} is not in the range of 0 to {self._n_machines}"
        last_scheduled_task = None
        last_scheduled_task_start_time = -1
        for i, row in enumerate(self._state[1:-1], start=1):
            if row[self._task_machine_column_idx] != machine_id:
                # task is not on the machine
                continue
            # case: task is on the machine
            if row[self._task_start_time_column_idx] > last_scheduled_task_start_time:
                last_scheduled_task = i
                last_scheduled_task_start_time = row[self._task_start_time_column_idx]
        return last_scheduled_task

    def get_predecessor_list(self, task_id: int) -> list[int]:
        # check if the task id is valid
        if task_id < 1 or task_id > self._n:
            raise ValueError(f"Task id must be between 1 and {self._n}.")

        # case: task_id has no predecessors
        if self._state[task_id][self._predecessor_list_first_elem_col_idx] == 0:
            return []

        # case: task_id one predecessor
        # the first and last element of the predecessor list are the same
        if self._state[task_id][self._predecessor_list_first_elem_col_idx] == \
                self._state[self._predecessor_list_last_elem_row_idx][task_id]:
            return [self._state[task_id][self._predecessor_list_first_elem_col_idx]]

        # case: task_id has more than one predecessor
        predecessors = []
        k = self._state[task_id][self._predecessor_list_first_elem_col_idx]
        while True:
            predecessors.append(k)
            k = self._state[task_id][k]
            assert 0 < k <= self._n
            if k == self._state[task_id][k]:
                predecessors.append(k)
                break

        return predecessors

    def get_successor_list(self, task_id: int) -> list[int]:
        # check if the task id is valid
        if task_id < 1 or task_id > self._n:
            raise ValueError(f"Task id must be between 1 and {self._n}.")

        # case: task_id has no successors
        if self._state[task_id][self._successor_list_first_elem_col_idx] == 0:
            return []

        # case: task_id one successor
        # the first and last element of the successor list are the same
        if self._state[task_id][self._successor_list_first_elem_col_idx] == \
                self._state[self._successor_list_last_elem_row_idx][task_id]:
            return [self._state[task_id][self._successor_list_first_elem_col_idx]]

        # case: task_id has more than one successor
        successors = []
        # NOTE: the first element and last element cells are not shifted by self._n
        k = self._state[task_id][self._successor_list_first_elem_col_idx]
        assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
        successors.append(k)
        while k != self._state[task_id][k] - self._n:
            k = self._state[task_id][k] - self._n
            assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
            successors.append(k)

        return successors

    def get_unknown_list(self, task_id: int) -> list[int]:
        # check if the task id is valid
        if task_id < 1 or task_id > self._n:
            raise ValueError(f"Task id must be between 1 and {self._n}.")

        # case: there is no unknown task
        if self._state[task_id][task_id] == -task_id:
            return []

        # case: there are multiple unknown tasks
        unknowns = []
        k = -self._state[task_id][task_id]
        assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
        unknowns.append(k)
        while k != -self._state[task_id][k]:
            k = -self._state[task_id][k]
            assert 0 < k <= self._n, f"{k=} is not in the range of 1 to {self._n}"
            unknowns.append(k)

        return unknowns

    def _state_as_gant_dataframes(self) -> pd.DataFrame:
        return pd.DataFrame([
            {
                'Task': f'Job {(t_id - 1) // self._n_machines}',
                'Start': row[self._task_start_time_column_idx],
                'Finish': row[self._task_start_time_column_idx] + row[self._task_duration_column_idx],
                'Resource': f'Machine {row[self._task_machine_column_idx]}'
            }
            for t_id, row in enumerate(self._state[1:-1], start=1)
            if row[self._task_start_time_column_idx] != -1
        ])

    def get_makespan(self) -> int:
        makespan = 0
        for row in self._state[1:-1]:
            if row[self._task_start_time_column_idx] == -1:
                continue
            makespan = max(makespan, row[self._task_start_time_column_idx] + row[self._task_duration_column_idx])
        return makespan

    def get_machine_utilization_ignore_unused_machines(self) -> float:
        machine_end_times = [-1 for _ in range(self._n_machines)]
        accumulated_processing_time = [0 for _ in range(self._n_machines)]
        for row in self._state[1:-1]:
            machine_id = row[self._task_machine_column_idx]
            start_time = row[self._task_start_time_column_idx]
            if start_time == -1:
                continue
            duration = row[self._task_duration_column_idx]
            machine_end_times[machine_id] = max(machine_end_times[machine_id], start_time + duration)
            accumulated_processing_time[machine_id] += duration
        machine_utilisation_per_machine = [
            accumulated_processing_time[i] / machine_end_times[i]
            for i in range(self._n_machines)
            if machine_end_times[i] != -1
        ]
        # divide by the number of machines to get the average machine utilisation
        average_utilisation = sum(machine_utilisation_per_machine) / len(
            machine_utilisation_per_machine) if machine_utilisation_per_machine else 0
        return average_utilisation

    def get_machine_utilization_average_default_0(self) -> float:
        machine_end_times = [-1 for _ in range(self._n_machines)]
        accumulated_processing_time = [0 for _ in range(self._n_machines)]
        for row in self._state[1:-1]:
            machine_id = row[self._task_machine_column_idx]
            start_time = row[self._task_start_time_column_idx]
            if start_time == -1:
                continue
            duration = row[self._task_duration_column_idx]
            machine_end_times[machine_id] = max(machine_end_times[machine_id], start_time + duration)
            accumulated_processing_time[machine_id] += duration
        machine_utilisation_per_machine = [
            accumulated_processing_time[i] / machine_end_times[i] if machine_end_times[i] != -1 else 0
            for i in range(self._n_machines)
        ]
        # divide by the number of machines to get the average machine utilisation
        average_utilisation = sum(machine_utilisation_per_machine) / self._n_machines
        return average_utilisation

    def get_machine_utilization_average_default_1(self) -> float:
        machine_end_times = [-1 for _ in range(self._n_machines)]
        accumulated_processing_time = [0 for _ in range(self._n_machines)]
        for row in self._state[1:-1]:
            machine_id = row[self._task_machine_column_idx]
            start_time = row[self._task_start_time_column_idx]
            if start_time == -1:
                continue
            duration = row[self._task_duration_column_idx]
            machine_end_times[machine_id] = max(machine_end_times[machine_id], start_time + duration)
            accumulated_processing_time[machine_id] += duration
        machine_utilisation_per_machine = [
            accumulated_processing_time[i] / machine_end_times[i] if machine_end_times[i] != -1 else 1
            for i in range(self._n_machines)
        ]
        # divide by the number of machines to get the average machine utilisation
        average_utilisation = sum(machine_utilisation_per_machine) / self._n_machines
        return average_utilisation

    def get_total_machine_utilization(self) -> float:
        latest_scheduled_end_time = 0;
        accumulated_duration_of_scheduled_tasks = 0;

        for row in self._state[1:-1]:
            start_time = row[self._task_start_time_column_idx]
            if start_time == -1:
                continue
            duration = row[self._task_duration_column_idx]
            latest_scheduled_end_time = max(latest_scheduled_end_time, start_time + duration)
            accumulated_duration_of_scheduled_tasks += duration

        return accumulated_duration_of_scheduled_tasks / (
                latest_scheduled_end_time * self._n_machines) if latest_scheduled_end_time != 0 else 0

    """
    Utility methods for the environment
    """

    def _get_simple_makespan_lower_bound(self, jsp_instance: npt.NDArray) -> int:
        # calculate the processing time of the longest job
        processing_times = jsp_instance[1]
        # sum all task inside a job, then take the max of the resulting values
        return max([sum(processing_times[job]) for job in range(self._n_jobs)])

    def valid_action_mask(self) -> npt.NDArray[np.int8]:
        # NOTE: 0 intentionally included
        return np.array([row[self._valid_action_column_idx] for row in self._state[:-1]], dtype=np.int8)

    def valid_action_list(self) -> list[int]:
        return [i for i, is_valid in enumerate(self.valid_action_mask()) if is_valid]

    def is_left_shift_possible(self, task_to_schedule: int) -> (bool, int | None, int | None):
        machine_id = self.get_machine_of_task(task_id=task_to_schedule)
        prev_task_in_job: int | None = self.get_last_predecessor_within_job(task_id=task_to_schedule)
        # task_to_schedule cannot start before the end of the previous task in the job
        # min_start_time is the early start time of task_to_schedule
        if prev_task_in_job is None:
            # case: task_to_schedule is the first task in the job
            min_start_time = 0
        else:
            min_start_time = self._state[prev_task_in_job][self._task_start_time_column_idx] + \
                             self._state[prev_task_in_job][self._task_duration_column_idx]
            # print(f"prev_task_in_job: {prev_task_in_job}")
            # print(f"prev_task_start_time: {self._state[prev_task_in_job][self._task_start_time_column_idx]}")
            # print(f"prev_task_duration: {self._state[prev_task_in_job][self._task_duration_column_idx]}")
            # print(f"min_start_time: {min_start_time}")

        list_of_scheduled_tasks_on_machine = [
            i for i, row in enumerate(self._state[1:-1], start=1)
            if row[self._task_machine_column_idx] == machine_id
               and row[self._task_start_time_column_idx] != -1
               and row[self._task_start_time_column_idx] + row[self._task_duration_column_idx] >= min_start_time
            # and row[self._task_start_time_column_idx] + row[self._task_duration_column_idx] >= 1
        ]
        # sort the list of scheduled tasks on the machine by start time
        list_of_scheduled_tasks_on_machine.sort(key=lambda x: self._state[x][self._task_start_time_column_idx])
        # print(f"list_of_scheduled_tasks_on_machine: {list_of_scheduled_tasks_on_machine}")
        # print(f"list_of_scheduled_tasks_on_machine: {[ divmod(elem, 6) for elem in list_of_scheduled_tasks_on_machine]}")
        if len(list_of_scheduled_tasks_on_machine):
            first_task_on_machine_after_job_pred_ends = list_of_scheduled_tasks_on_machine[0]
            first_task_on_machine_after_job_pred_ends_start_time = \
            self._state[first_task_on_machine_after_job_pred_ends][self._task_start_time_column_idx]
            if (min_start_time - first_task_on_machine_after_job_pred_ends_start_time) >= self._state[task_to_schedule][
                self._task_duration_column_idx]:
                return True, None, first_task_on_machine_after_job_pred_ends_start_time

        for prev, next in zip(list_of_scheduled_tasks_on_machine, list_of_scheduled_tasks_on_machine[1:]):
            prev_end_time = self._state[prev][self._task_start_time_column_idx] + self._state[prev][
                self._task_duration_column_idx]
            next_start_time = self._state[next][self._task_start_time_column_idx]
            # print(f"endtime of t({prev}): {self._state[prev][self._task_start_time_column_idx]}")
            # print(f"startime of t({next}): {self._state[next][self._task_start_time_column_idx]}")
            # task_to_schedule_duration = self._state[task_to_schedule][self._task_duration_column_idx]
            # if task_to_schedule fits in between prev and next, then a left shift is possible
            if (next_start_time - prev_end_time) >= self._state[task_to_schedule][self._task_duration_column_idx]:
                return True, prev, next
        return False, None, None

    def random_rollout(self) -> int:

        done = self.is_terminal_state()

        # unfortunately, we dont have any information about the past rewards
        # so we just return the cumulative reward from the current state onwards
        cumulative_reward_from_current_state_onwards = 0

        while not done:
            valid_action_list = self.valid_action_list()
            random_action = np.random.choice(valid_action_list)
            _, rew, done, _, _ = self.step(random_action)
            cumulative_reward_from_current_state_onwards += rew

        return cumulative_reward_from_current_state_onwards

    def greedy_rollout(self) -> int:

        def get_best_action():
            prev_state = self.get_state()
            max_utilisation = 0.0
            best_action = None
            for action in self.valid_action_list():
                _, _, done, _, _ = self.step(action)

                utilisation = self.get_machine_utilization_ignore_unused_machines()
                if utilisation > max_utilisation:
                    max_utilisation = utilisation
                    best_action = action
                self.load_state(prev_state)
            return best_action

        done = self.is_terminal_state()
        cumulative_reward_from_current_state_onwards = 0
        while not done:
            best_action = get_best_action()
            _, rew, done, _, _ = self.step(best_action)
            cumulative_reward_from_current_state_onwards += rew

        return cumulative_reward_from_current_state_onwards

    def load_state(self, state: npt.NDArray) -> None:
        # this method does not check if the state is valid or not
        if state.shape != self._state.shape:
            raise ValueError(f"Invalid state shape. Expected: {self._state.shape}, got: {state.shape}")
        self._state = state.copy()

    def get_state(self) -> npt.NDArray:
        return self._state.copy()

    def get_c_lb(self) -> int:
        return self.get_state()[0][0]


if __name__ == '__main__':
    custom_jsp_instance = np.array([
        [
            [0, 1, 2, 3],  # job 0
            [0, 2, 1, 3]  # job 1
        ],
        [
            [11, 3, 3, 12],  # task durations of job 0
            [5, 16, 7, 4]  # task durations of job 1
        ]

    ], dtype=np.int32)
    env = DisjunctiveGraphJspEnv(
        jsp_instance=custom_jsp_instance,
    )
    obs, info = env.reset()
    env.render()

    for a in [5, 1, 2, 6, 3, 7, 4, 8]:
        obs, reward, done, info, _ = env.step(a)
        print(f"{a=}, {reward=}, {done=}, {info=}")
        env.render(mode='debug')

    # env.random_rollout()
    env.render()
