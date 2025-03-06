import matplotlib.pyplot as plt
import numpy as np

CEND = "\33[0m"
CBOLD = "\33[1m"
CITALIC = "\33[3m"
CURL = "\33[4m"
CBLINK = "\33[5m"
CBLINK2 = "\33[6m"
CSELECTED = "\33[7m"

CBLACK = "\33[30m"
CRED = "\33[31m"
CGREEN = "\33[32m"
CYELLOW = "\33[33m"
CBLUE = "\33[34m"
CCYAN = '\33[96m'
CMAGENTA = '\033[35m'
CVIOLET = "\33[35m"
CBEIGE = "\33[36m"
CWHITE = "\33[37m"

CBLACKBG = "\33[40m"
CREDBG = "\33[41m"
CGREENBG = "\33[42m"
CYELLOWBG = "\33[43m"
CBLUEBG = "\33[44m"
CVIOLETBG = "\33[45m"
CBEIGEBG = "\33[46m"
CWHITEBG = "\33[47m"

CGREY = "\33[90m"
CRED2 = "\33[91m"
CGREEN2 = "\33[92m"
CYELLOW2 = "\33[93m"
CBLUE2 = "\33[94m"
CCYAN2 = "\033[36m"
CVIOLET2 = "\33[95m"
CBEIGE2 = "\33[96m"
CWHITE2 = "\33[97m"

CGREYBG = "\33[100m"
CREDBG2 = "\33[101m"
CGREENBG2 = "\33[102m"
CYELLOWBG2 = "\33[103m"
CBLUEBG2 = "\33[104m"
CVIOLETBG2 = "\33[105m"
CBEIGEBG2 = "\33[106m"
CWHITEBG2 = "\33[107m"


def rgb_color_sequence(r: int | float, g: int | float, b: int | float,
                       *, format_type: str = 'foreground') -> str:
    """
    generates a color-codes, that change the color of text in console outputs.

    rgb values must be numbers between 0 and 255 or 0.0 and 1.0.

    :param r:               red value.
    :param g:               green value
    :param b:               blue value

    :param format_type:     specifies weather the foreground-color or the background-color shall be adjusted.
                            valid options: 'foreground','background'
    :return:                a string that contains the color-codes.
    """
    # type: ignore # noqa: F401
    if format_type == 'foreground':
        f = '\033[38;2;{};{};{}m'.format  # font rgb format
    elif format_type == 'background':
        f = '\033[48;2;{};{};{}m'.format  # font background rgb format
    else:
        raise ValueError(f"format {format_type} is not defined. Use 'foreground' or 'background'.")
    rgb = [r, g, b]

    if isinstance(r, int) and isinstance(g, int) and isinstance(b, int):
        if min(rgb) < 0 and max(rgb) > 255:
            raise ValueError("rgb values must be numbers between 0 and 255 or 0.0 and 1.0")
        return f(r, g, b)
    if isinstance(r, float) and isinstance(g, float) and isinstance(b, float):
        if min(rgb) < 0 and max(rgb) > 1:
            raise ValueError("rgb values must be numbers between 0 and 255 or 0.0 and 1.0")
        return f(*[int(n * 255) for n in [r, g, b]])


def print_graph_matrix_to_console(
        graph: list[list[int]],
        n_machines: int,
        undo_task_encoding=False,
        c_map="rainbow"
) -> None:
    """
    prints a graph matrix to the console.

    :param graph: the graph matrix to print

    :param n_machines: the number of machines. This could be determined by the graph matrix itself, but it is more
                       efficient to pass it as an argument.

    :param undo_task_encoding: If set to True, the task encoding will be undone. This means that member of the unknown
                               list will have the minus sign removed. Members of the successor list will be reduced by
                               the number of tasks. This is useful for debugging purposes.

    :param c_map: A string that specifies the colormap to use. This must be a valid colormap name from matplotlib.
                  The color map is used to color the machines (so that they match the colors of the gantt chart
                  visualisation).
    :return:
    """
    state = graph
    n_rows, n_cols = len(state), len(state[0])
    n_total_tasks = n_rows
    n = n_total_tasks - 2

    _task_machine_column_idx = n_cols - 4
    _task_duration_column_idx = n_cols - 3
    _task_start_time_column_idx = n_cols - 2
    _valid_action_column_idx = n_cols - 1

    # generate colors for machines
    c_map = plt.cm.get_cmap(c_map)  # select the desired cmap
    arr = np.linspace(0, 1, n_machines)  # create a list with numbers from 0 to 1 with n items
    machine_colors = {m_id: c_map(val)[:-1] for m_id, val in enumerate(arr)}

    headline = "┃".join([
        "    ",
        *[f" {t_id:2} " if t_id < 100 else f"{t_id:4}" for t_id in range(n_total_tasks)],
        "  m ",
        "  d ",
        "  s ",
        "  v "
    ])
    headline = f"┃{headline}┃"
    header_top = "".join(["━" * 4 + "┳" for _ in range(n_cols + 1)])
    header_top = "┏" + header_top[:-1] + "┓"
    header_sep = "╇".join(["━" * 4 for _ in range(n_cols - 1)])
    header_sep = "┣" + "━" * 4 + "╋" + header_sep + "╇" + "━" * 4 + "┫"
    legend = f"""
color encoding: 
{CVIOLET}Successors{CEND}, {CBLUE}Predecessors{CEND}, {CYELLOW}Unknown{CEND},
{CBLUEBG}{CBOLD} t_id {CEND} first task in {CBLUE}Predecessors{CEND}-List
{CBLUEBG2}{CBOLD} t_id {CEND} last task in {CBLUE}Predecessors{CEND}-List
{CVIOLETBG}{CBOLD} t_id {CEND} first task in  {CVIOLET}Successors{CEND}-List
{CVIOLETBG2}{CBOLD} t_id {CEND} last task in {CVIOLET}Successors{CEND}-List
{CYELLOWBG}{CBOLD} t_id {CEND} first task in {CYELLOW}Unknown{CEND}-List

{CGREENBG2}{CBOLD} makespan lower bound estimate{CEND} 
"""
    if undo_task_encoding:
        print(legend)

    print(header_top)
    print(headline)
    print(header_sep)


    row_sep = "┼".join(["─" * 4 for _ in range(n_cols - 1)])
    row_sep = "┣" + "━" * 4 + "╉" + row_sep + "┼" + "─" * 4 + "┨"

    last_row_sep = "┷".join(["━" * 4 for _ in range(n_cols - 1)])
    last_row_sep = "┗" + "━" * 4 + "┻" + last_row_sep + "┷" + "━" * 4 + "┛"
    for row_idx, row in enumerate(state):
        task_cell = f"┃ {row_idx:2} ┃" if row_idx < 100 else f"┃{row_idx:4}┃"

        def get_colored_cell(row_idx, col_idx: int, undo_task_encoding=undo_task_encoding) -> str:
            current_row = state[row_idx]
            cell_content = current_row[col_idx]

            if undo_task_encoding:
                temp = cell_content
                if col_idx < _task_machine_column_idx - 1:
                    if cell_content < 0:
                        # element is in unknown list
                        temp = -cell_content
                    if cell_content > n:
                        # element is in successor list
                        temp = temp - n
                cell_text = f" {temp:2} " if -100 < temp < 100 else f"{temp:4}"
            else:
                cell_text = f" {cell_content:2} " if -100 < cell_content < 100 else f"{cell_content:4}"

            # special cases
            if row_idx == 0 and col_idx == 0:
                return f"{CGREENBG2}{CBOLD}{cell_content:4}{CEND}"
            if row_idx == 0 and 0 < col_idx < _task_machine_column_idx - 1:
                # last task in predecessors list
                return f"{CBLUEBG2}{CBOLD}{cell_text}{CEND}"
            if row_idx == n_rows - 1 and 0 < col_idx < _task_machine_column_idx - 1:
                # last task in successors list
                return f"{CVIOLETBG2}{CBOLD}{cell_text}{CEND}"

            if row_idx == 0 and col_idx == _task_machine_column_idx:
                return f"{CGREY}{cell_text}{CEND}"
            if row_idx == 0 and col_idx == _task_duration_column_idx:
                return f"{CGREY}{cell_text}{CEND}"
            if row_idx == 0 and col_idx == _task_start_time_column_idx:
                return f"{CGREY}{cell_text}{CEND}"
            if row_idx == 0 and col_idx == _valid_action_column_idx:
                return f"{CGREY}{cell_text}{CEND}"

            if row_idx == n_rows - 1 and col_idx == _task_machine_column_idx:
                return f"{CGREY}{cell_text}{CEND}"
            if row_idx == n_rows - 1 and col_idx == _task_duration_column_idx:
                return f"{CGREY}{cell_text}{CEND}"
            if row_idx == n_rows - 1 and col_idx == _task_start_time_column_idx:
                return f"{CGREY}{cell_text}{CEND}"
            if row_idx == n_rows - 1 and col_idx == _valid_action_column_idx:
                return f"{CGREY}{cell_text}{CEND}"

            if col_idx == 0:
                if row_idx == 0 or row_idx == n_rows - 1:
                    return f"{CGREY}{cell_text}{CEND}"
                # first tasks in predecessor list
                return f"{CBLUEBG}{CBOLD}{cell_text}{CEND}"

            if col_idx == _task_machine_column_idx - 1:
                if row_idx == 0 or row_idx == n_total_tasks - 1:
                    return f"{CGREY}{cell_text}{CEND}"
                # last tasks in predecessor list
                return f"{CVIOLETBG}{CBOLD}{cell_text}{CEND}"

            if col_idx == _task_machine_column_idx:
                return f"{rgb_color_sequence(*machine_colors[cell_content], format_type='background')}{cell_text}{CEND}"
            if col_idx == _task_duration_column_idx:
                return f"{CCYAN}{cell_text}{CEND}"
            if col_idx == _task_start_time_column_idx:
                return f"{CGREEN2 if cell_content != -1 else CRED2}{cell_text}{CEND}"
            if col_idx == _valid_action_column_idx:
                return f"{CRED if cell_content == 0 else CGREEN}{cell_text}{CEND}"

            if cell_content < 0:
                if col_idx == row_idx:
                    return f"{CYELLOWBG}{CBOLD}{cell_text}{CEND}"
                return f"{CYELLOW}{cell_text}{CEND}"
            elif cell_content <= n:
                return f"{CBLUE}{cell_text}{CEND}"
            else:
                return f"{CVIOLET}{cell_text}{CEND}"

        row = "│".join([
            *[get_colored_cell(row_idx, t_id) for t_id in range(n_total_tasks)],
            get_colored_cell(row_idx, _task_machine_column_idx),
            get_colored_cell(row_idx, _task_duration_column_idx),
            get_colored_cell(row_idx, _task_start_time_column_idx),
            get_colored_cell(row_idx, _valid_action_column_idx),
        ])

        row = task_cell + row + "┃"
        print(row)
        print(row_sep if row_idx < n_total_tasks - 1 else last_row_sep)


def wrap_with_color_codes(s: object, /, r: int | float, g: int | float, b: int | float, **kwargs) \
        -> str:
    """
    stringify an object and wrap it with console color codes. It adds the color control sequence in front and one
    at the end that resolves the color again.

    rgb values must be numbers between 0 and 255 or 0.0 and 1.0.

    :param s: the object to stringify and wrap
    :param r: red value.
    :param g: green value.
    :param b: blue value.
    :param kwargs: additional argument for the 'DisjunctiveGraphJspVisualizer.rgb_color_sequence'-method.
    :return:
    """
    return f"{rgb_color_sequence(r, g, b, **kwargs)}" \
           f"{s}" \
           f"{CEND}"
