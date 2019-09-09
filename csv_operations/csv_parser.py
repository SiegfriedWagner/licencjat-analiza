# %%
import pandas as pd
from os.path import join, dirname, basename
skipnrows = None
def read_data(path, skiprows=None) -> pd.DataFrame:
    names = ['Time elapsed',
        'System time',
        'Task',
        'Value',
        'Status',
        'State',
        'Current time',
        'Duration',
        'Brightness',
        'Volume',
        'Video',
        'Panel',
        'Key']
    ret = pd.read_csv(path, 
        delimiter=',',
        names=names,
        skipinitialspace=True,
        skiprows=skiprows)
    ret = ret[ret['Panel'].notnull()]
    if ret.empty:
        ret = pd.read_csv(path, 
            delimiter=';',
            names=names,
            skipinitialspace=True,
            skiprows=skiprows)
        ret = ret[ret['Panel'].notnull()]
    if ret.empty:
        raise ValueError(f'Not a valid data: {path}')
    return ret

def isF2row(row):
    return True if row['Key'] == 'key: F2' else False

def isF3row(row):
    return True if row['Key'] == 'key: F3' else False

def is_status_start_row(row):
    return True if row['Status'] != 'Start' else False

def get_volume(row):
    return int(row['Volume'].strip('volume: '))

def get_video_percentage(row):
    current_time = float(row['Current time'].strip('current time: '))
    duration = float(row['Duration'].strip('duration: '))
    if duration == 0:
        return 0
    return current_time/duration*100

def get_current_panel(row):
    return int(row['Panel'].strip('related videos: ').strip('/3'))

def get_current_time(row):
    return float(row['Time elapsed'])

def get_current_stamp(row):
    return row['System time'].strip(' ')

class TaskAnalyzer():

    def __init__(self, start_row, subtasks):
        self.subtasks = subtasks
        self.start_time = get_current_time(start_row)
        self.start_panel = get_current_panel(start_row)
        self.start_stamp = get_current_stamp(start_row)
        self.last_step_time = self.start_time
        self.last_step_stamp = get_current_stamp(start_row)
        self.number_of_errors = 0
        self.isFinished = False
        self.task_name = None
        self._analyzer = None
        self._result = []
        self.subtask = None

    @property
    def result_df(self):
        return pd.DataFrame(self._result, columns=columns)

    @property
    def time_delta(self):
        return self.last_step_time - self.start_time

    def send(self, row):
        if isF3row(row):
            self.last_step_time = get_current_time(row)
            self.last_step_stamp = get_current_stamp(row)
        elif isF2row(row):
            raise ValueError("Unexpected F2row")
        else:
            self._analyzer.send(row)

    def finish(self):
        self._append_result()
        self._analyzer.close()
        
    def _append_result(self):
        self._result.append([self.task_name,
                            self.start_stamp, 
                            self.last_step_stamp,
                            self.time_delta,
                            self.number_of_errors,
                            self.isFinished,
                            self.subtask])
    
    def _task_set_volume(self, target_value, starting_value):
        margin = 5
        previous = starting_value
        while True:
            row = yield
            percentage = get_volume(row)
            if row['Task'] not in  ['VolumeDown', 'VolumeUp']:
                self.number_of_errors += 1
            else:
                if percentage >= (target_value - margin) and percentage <= (target_value + margin):
                    self.isFinished = True
                if abs(target_value - previous) < abs(target_value - percentage):
                    self.number_of_errors += 1
                previous = percentage

    def _task_time(self, target_value, starting_value):
        margin = 5
        previous = starting_value
        while True:
            row = yield
            percentage = get_video_percentage(row)
            if row['Task'] != 'FastForward' and row['Task'] != 'Rewind':
                self.number_of_errors += 1
            else:
                if percentage >= (target_value - margin) and percentage <= (target_value + margin):
                    self.isFinished = True
                if abs(target_value - previous) < abs(target_value - percentage):
                    self.number_of_errors += 1
                previous = percentage

    def _task_pause_and_resume(self):
        while True:
            row = yield
            if row['Task'] != 'Pause':
                self.number_of_errors += 1
            else:
                break
        while True:
            row = yield
            if row['Task'] != 'Play':
                self.number_of_errors += 1
            else:
                self.isFinished = True

    def _task_set_panel_and_video(self, video, panel):
        current_panel = self.start_panel 
        while panel > current_panel:
            row = yield
            if row['Task'] != 'RelativePanelDown':
                self.number_of_errors += 1
            else:
                current_panel = get_current_panel(row)
        while panel < current_panel:
            row = yield
            if row['Task'] != 'RelativePanelUp':
                self.number_of_errors += 1
            else:
                current_panel = get_current_panel(row)
        while True:
            row = yield
            if row['Task'].startswith('RelativePanel') and row['Task'][-1].isdigit():
                set_video = int(row['Task'][-1])
                if set_video == video:
                    self.isFinished = True
            else:
                self.number_of_errors += 1

    def _task_pause(self):
        while True:
            row = yield
            if row['Task'] != ' Pause':
                self.number_of_errors += 1
            else:
                self.isFinished = True

    @classmethod
    def get_task_analyzer(cls, task, F2_row, subtasks=True):
        analyzer = cls(F2_row, subtasks)
        if task.startswith('Przewiń film do'):
            target_time = float(task.strip('Przewiń film do ').strip("%\n"))
            if target_time < get_video_percentage(F2_row):
                analyzer.task_name = "Rewind"
            else:
                analyzer.task_name = "FeedForward"
            analyzer._analyzer = analyzer._task_time(target_time, get_video_percentage(F2_row))
        elif task.startswith('Ustaw głośność na') or task.startswith("Ustaw głośności na"):
            target_volume = float(task.strip('Ustaw głośność na').strip("Ustaw głośności na").strip('%\n'))
            if target_volume < get_volume(F2_row):
                analyzer.task_name = "ReduceVolume"
            else:
                analyzer.task_name = "IncreaseVolume"
            analyzer._analyzer = analyzer._task_set_volume(target_volume, get_volume(F2_row))
        elif task.startswith('Wstrzymaj, a następnie wznów film'):
            analyzer.task_name = "PauseAndResume"
            analyzer._analyzer = analyzer._task_pause_and_resume()
        elif task.startswith('Wybierz'):
            analyzer.task_name = "SetVideo"
            video = int(task.strip('Wybierz ')[0])
            analyzer._analyzer = analyzer._task_set_panel_and_video(video, analyzer.start_panel)
        elif task.startswith('Przewiń listę filmów'):
            analyzer.task_name = "SetPanelAndVideo"
            stripped = task.strip('Przewiń listę filmów ')
            split, rest = stripped.split(' ', maxsplit=1)
            panel = get_current_panel(F2_row)
            if split == 'dwa' or "dół":
                panel = 2
            elif split == 'do':
                panel = 1
            else:
                raise ValueError(f"Unknown value {split}")
            f_index = rest.find('film')
            film = int(rest[f_index-2])
            analyzer._analyzer = analyzer._task_set_panel_and_video(film, panel)
        elif task.startswith('Zatrzymaj film'):
            analyzer.task_name = "Pause"
            analyzer._analyzer = analyzer._task_pause()
        else:
            raise ValueError(f'Unknown task "{task}"')

        analyzer._analyzer.send(None)
        return analyzer

class RegionsTaskAnalyzer(TaskAnalyzer):

    def _task_set_volume(self, target_value, starting_value):
        margin = 5
        previous = starting_value
        if self.subtasks:
            self.subtask = 'Pause'
        while not self.isFinished:
            row = yield
            if row['Task'] == 'Pause':
                if self.subtasks:
                    self.last_step_time = get_current_time(row)
                    self.last_step_stamp = get_current_stamp(row)
                    self.isFinished = True
                    self._append_result()
                else:
                    break
            else:
                self.number_of_errors += 1
        if self.subtasks:
            self.isFinished = False
            self.start_stamp = get_current_stamp(row)
            self.start_time = get_current_time(row)
            self.number_of_errors = 0               
            self.subtask = 'SetVolume'
        prev_stamp = get_current_stamp(row)
        prev_time = get_current_time(row)
        while True:
            prev_stamp = get_current_stamp(row)
            prev_time = get_current_time(row)
            row = yield
            percentage = get_volume(row)
            if row['Task'] == 'Play':
                break
            elif row['Task'] not in  ['VolumeDown', 'VolumeUp']:
                self.number_of_errors += 1
            else:
                if percentage >= (target_value - margin) and percentage <= (target_value + margin):
                    self.isFinished = True
                if abs(target_value - previous) + 1< abs(target_value - percentage):
                    self.number_of_errors += 1
                previous = percentage
        if self.subtasks:
            self.last_step_stamp = prev_stamp
            self.last_step_time = prev_time
            self._append_result()
            self.subtask = 'Play'
            self.start_time = prev_time
            self.start_stamp = prev_stamp
        self.isFinished = True
        
        while True:
            self.last_step_stamp = get_current_stamp(row)
            self.last_step_time = get_current_time(row)
            row = yield
            self.number_of_errors += 1

    def _task_time(self, target_value, starting_value):
        margin = 5
        previous = starting_value
        if self.subtasks:
            self.subtask = 'Pause'
        while not self.isFinished:
            row = yield
            if row['Task'] == 'Pause':
                if self.subtasks:
                    self.last_step_time = get_current_time(row)
                    self.last_step_stamp = get_current_stamp(row)
                    self.isFinished = True
                    self._append_result()
                else:
                    break
            else:
                self.number_of_errors += 1
        self.isFinished = False
        if self.subtasks:
            self.start_stamp = get_current_stamp(row)
            self.start_time = get_current_time(row)
            self.number_of_errors = 0
            self.subtask = 'SetTime'
        prev_stamp = get_current_stamp(row)
        prev_time = get_current_time(row)
        while True:
            prev_stamp = get_current_stamp(row)
            prev_time = get_current_time(row)
            row = yield
            percentage = get_video_percentage(row)
            if row['Task'] == 'Play':
                break
            if row['Task'] != 'FastForward' and row['Task'] != 'Rewind':
                self.number_of_errors += 1
            else:
                if percentage >= (target_value - margin) and percentage <= (target_value + margin):
                    self.isFinished = True
                if abs(target_value - previous) + 1 < abs(target_value - percentage):
                    self.number_of_errors += 1
                previous = percentage
        self.isFinished = True
        if self.subtasks:
            self.last_step_stamp = prev_stamp
            self.last_step_time = prev_time
            self._append_result()
            self.number_of_errors = 0
            self.subtask = 'Play'
            self.start_time = prev_time
            self.start_stamp = prev_stamp
        while True:
            self.last_step_stamp = get_current_stamp(row)
            self.last_step_time = get_current_time(row)
            row = yield
            self.number_of_errors += 1

columns=['Task name', 'Start stamp', 'End stamp', 'Duration', 'Number of errors', 'Completed', 'SubTask']
def parse_csv(analyzer_class, task_path, csv_path, subtasks=False, skiprows=None) -> pd.DataFrame:
    csv_dataframe = read_data(csv_path, skiprows)
    result_df = pd.DataFrame(columns=columns)
    with open(task_path, 'r', encoding="utf-8") as task_file:
        df_iterator = csv_dataframe.iterrows()
        index, data_row = next(df_iterator)
        while not isF2row(data_row):
            try:
                index, data_row = next(df_iterator)
            except StopIteration as e:
                raise ValueError(f'File "{csv_path}" does not contain F2 row') from e
        for task in task_file:
            while not isF2row(data_row):
                index, data_row = next(df_iterator)
                if isF3row(data_row):
                    raise ValueError(f"F3 row error: Check integrity of file: {csv_path} at row {index}.")
            task_analyzer = analyzer_class.get_task_analyzer(task, data_row, subtasks)
            while not isF3row(data_row):
                index, data_row = next(df_iterator)
                if is_status_start_row(data_row):
                    try:
                        task_analyzer.send(data_row)
                    except Exception as e:
                        raise Exception(f"Exception occured in {csv_path}") from e
                if isF2row(data_row):
                    raise ValueError(f"F2 row error: Check integrity of file: {csv_path} at row {index}.")
            task_analyzer.finish()
            result_df = result_df.append(task_analyzer.result_df)

    return result_df
# %%
if __name__ == '__main__': 
    import argparse
    import csv_validator
    parser = argparse.ArgumentParser(description="Based on task file and log file this script returns task file with name of task, time required to complete a task, number of errors that the participant has made, information if participant completed the task and any subtasks included in main task. For every pair of files (log and task) it will create single processed.csv file in the same directory as input files with program output.")
    parser.add_argument('path', help="Path to directory with task file and log file or path to tree like direcory structure in which scrip will look for task-log file pairs.")
    parser.add_argument("--subtask",
                        action="store_true",
                        default=False,
                        help="If set then subtasks are present in logs")
    args = parser.parse_args()
    valid = csv_validator.validate(args.path)
    analyzers = {'dwell-time_buttons': TaskAnalyzer,
                 'dwell-time_regions': RegionsTaskAnalyzer,
                 'enter-and-leave_regions': RegionsTaskAnalyzer,
                 'part_1_dwell-time_regions': RegionsTaskAnalyzer,
                 'part_1_enter-and-leave_regions': RegionsTaskAnalyzer,
                 'part_2_dwell-time_regions': RegionsTaskAnalyzer,
                 'part_2_enter-and-leave_regions': RegionsTaskAnalyzer,}
    for file, status in valid.items():
        parsed = parse_csv(analyzers[basename(dirname(file))],                       join(dirname(file), 'task.txt'),
                              file,
                              skiprows=[0,1],
                              subtasks=args.subtask)
        parsed.to_csv(join(dirname(file), 'processed.csv'))