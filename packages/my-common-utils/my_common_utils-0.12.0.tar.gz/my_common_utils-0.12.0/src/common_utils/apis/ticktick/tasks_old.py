import datetime
import os
from datetime import timedelta
from requests.exceptions import RetryError
import pandas as pd
from pandas import DataFrame
from ticktick.oauth2 import OAuth2  # OAuth2 Manager
from ticktick.api import TickTickClient as TickTick

from common_utils.config import secret, ROOT_DIR
from common_utils.logger import create_logger


class TickTickClient:
    """Wrapper for the TickTick API. Supports creating, getting and deleting tasks.

    Data is not converted to keep the original 'TickTick' format. This is to make this class more
    versatile, and to allow for more flexibility in the future.
    # TODO: convert to a more standard format

    Currently only supports start dates, as TickTick automatically sets the due date if not present.
    This makes handling due dates more difficult in conjunction with other tools like Notion.

    Attributes:
        api: TickTickClient object
        projects: dict, project ids as keys, project names as values
    """

    log = create_logger("TickTick")
    date_format = "%Y-%m-%dT%H:%M:%S.%f+0000"

    def __init__(self, cache_file: str = "ticktick_token.json") -> None:
        self.log = create_logger("TickTick")
        self.tz_offset = "+0100"
        auth_client = OAuth2(
            client_id=os.environ["TICKTICK_CLIENT_ID"],
            client_secret=os.environ["TICKTICK_CLIENT_SECRET"],
            redirect_uri=os.environ["TICKTICK_REDIRECT_URI"],  # TODO: set in env
            cache_path=f"{ROOT_DIR}/{cache_file}",
        )
        self.api = TickTick(username=os.environ["TICKTICK_EMAIL"],
                            password=os.environ["TICKTICK_PASSWORD"],
                            oauth=auth_client)
        self.projects = {project["id"]: project["name"] for project in self.api.state["projects"]}
        self.log.info(f"TickTickClient initialized with projects: {self.projects.values()}")

    def _get_project_name(self, project_id: str) -> str:
        """Return the project name corresponding to the given project id"""
        return self.projects[project_id] if project_id in self.projects else "Inbox"

    def _get_project_id(self, project_name: str) -> str:
        """Return the project id corresponding to the given project name"""
        for project_id, name in self.projects.items():
            if name == project_name:
                return project_id
        raise ValueError(f"Project {project_name} not found in TickTick")

    def _convert_date(self, date: str | datetime.date | datetime.datetime | None) -> str | None:
        """Convert a date to the TickTick format, if it isn't already"""
        if date is None or date == "" or pd.isna(date):
            return None
        elif isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            return date.strftime("%Y-%m-%dT%H:%M:%S+0000")
        elif isinstance(date, str) and len(date) == 10:
            return date + "T00:00:00+0000"
        elif isinstance(date, str) and len(date) == 24:
            return date
        else:
            raise TypeError(f"Date seems to be misconfigured, check type {type(date)} and len: 24")

    def create_task(
        self,
        title: str,
        project: str,
        content: str = "",
        start_date=None,
        due_date=None,
        all_day=True,
    ) -> str:
        """Create a task with the given title and project name, and optional content & due date

        Currently only supports one date in ticktick, to show in the "today" list. Therefore, tasks
        are created with the start date as the due date.

        Args:
            title: Title of the task
            project: Name of the project to create the task in
            content: Content of the task. Defaults to "".
            due_date: Due date of the task. Defaults to None.
                Will be converted to format: "2020-07-06T02:30:00+0100"
        """
        start_date = self._convert_date(start_date)
        due_date = self._convert_date(due_date)
        new_task = {
            "title": title,
            "content": content,
            "startDate": start_date,
            "dueDate": due_date,
            "isAllDay": all_day,
            "projectId": self._get_project_id(project),
        }
        try:
            new_task_result = self.api.task.create(task=new_task)
        except RetryError:
            raise RetryError("Apparent API throttling, could not create task")
        # self.log.debug(f"Created task: {new_task_result}")
        return new_task_result["id"]

    def create_tasks(self, titles: list[str], start_dates: list[str], project: str) -> list[str]:
        """Create tasks in TickTick from a given project. Return the ids of the created tasks.

        Expects a dataframe with the following columns:
            title: str, title of the task
            start_date: str|datetime|nan, start date of the task
            due_date: str|datetime|nan, due date of the task
        """
        assert len(titles) == len(start_dates), "titles and start_dates must be of equal length"
        self.log.info(f"Creating {len(titles)} tasks in project: {project}")
        created_ids = []
        for title, start_date in zip(titles, start_dates):
            created_id = self.create_task(
                title=title,
                start_date=start_date,
                # due_date=task["due_date"],
                project=project,
            )
            created_ids.append(created_id)
        return created_ids

    def _fix_timezones(self, tasks: DataFrame) -> DataFrame:
        """Checks if any dates are not 00:00 and add the timezone offset from the config.

        Converts to datetime, adds the offset, and converts back to string (can be improved)"""

        tasks["startDate"] = pd.to_datetime(tasks["startDate"], format=self.date_format)

        wrong_dates = tasks[(tasks["isAllDay"] == True) & tasks["startDate"].isna() == False]  # noqa
        wrong_dates = wrong_dates[
            (wrong_dates["startDate"].dt.hour != 0) | (wrong_dates["startDate"].dt.minute != 0)
        ]

        # add the timezone offset to the tasks that are in wrong_dates
        tasks.loc[wrong_dates.index, "startDate"] = wrong_dates["startDate"] + timedelta(
            hours=self.tz_offset[0], minutes=self.tz_offset[1]
        )
        tasks["startDate"] = tasks["startDate"].dt.strftime(self.date_format)
        tasks["startDate"] = tasks["startDate"].str[:-8] + tasks["startDate"].str[-5:]

        return tasks

    def get_all_tasks(self, project=None) -> DataFrame:
        """Return all tasks from TickTick as a DataFrame. Optionally, filter by project

        The dataframe is in the original 'TickTick' format."""
        tasks_df = DataFrame()
        for task in self.api.state["tasks"]:
            task["project"] = self._get_project_name(task["projectId"])
            tasks_df = tasks_df._append(task, ignore_index=True)
        if project is not None:
            tasks_df = tasks_df[tasks_df["project"] == project]
        self.log.info(f"Loaded {len(tasks_df)} tasks from TickTick (project: {project})")
        tasks_df = self._fix_timezones(tasks_df)
        return tasks_df

    def change_task_titles(self, task_ids: str | list[str], new_titles: str | list[str]) -> None:
        """Change the titles of a list of tasks"""
        if isinstance(task_ids, str) and isinstance(new_titles, str):
            task_ids = [task_ids]
            new_titles = [new_titles]
        assert len(task_ids) == len(new_titles), "task_ids and new_titles must be of equal length"
        for task_id, new_title in zip(task_ids, new_titles):
            task = self.api.get_by_id(task_id)
            task["title"] = new_title
            self.api.task.update(task)
            self.log.debug(f"Changed title of task {task_id} to {new_title}")

    def change_task_dates(self, task_ids: str | list[str], new_dates: str | list[str]) -> None:
        """Change the start dates of a list of tasks"""
        if isinstance(task_ids, str) and isinstance(new_dates, str):
            task_ids = [task_ids]
            new_dates = [new_dates]
        assert len(task_ids) == len(new_dates), "task_ids and new_dates must be of equal length"
        for task_id, new_date in zip(task_ids, new_dates):
            task = self.api.get_by_id(task_id)
            task["startDate"] = self._convert_date(new_date)
            self.api.task.update(task)
            self.log.debug(f"Changed start date of task {task_id} to {new_date}")

    def delete_all_tasks_in_project(self, project: str) -> None:
        """From a given project, delete all tasks"""
        project_tasks = self.get_all_tasks(project=project)
        self.log.info(f"Deleting all tasks in project: {project}")
        task_list = project_tasks.to_dict(orient="records")
        self.api.task.delete(task_list)

    def delete_tasks(self, task_ids: str | list[str]) -> None:
        # get the task objects via their ids
        if isinstance(task_ids, str):
            task_ids = [task_ids]
        self.log.info(f"Deleting {len(task_ids)} tasks")
        tasks = [self.api.get_by_id(task_id) for task_id in task_ids]
        self.api.task.delete(tasks)


if __name__ == "__main__":
    ticktick = TickTickClient()
    all_tasks = ticktick.get_all_tasks()
    notion_tasks = all_tasks[all_tasks["project"] == "Notion"]
    print(all_tasks)