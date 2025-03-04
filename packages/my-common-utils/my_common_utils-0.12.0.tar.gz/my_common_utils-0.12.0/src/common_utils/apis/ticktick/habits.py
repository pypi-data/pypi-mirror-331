import requests
import json
from datetime import datetime, timezone, timedelta
from common_utils.logger import create_logger
from common_utils.web.cookies_handler import CookiesManager, LoginData, LoginSelectors


# TODO: dataclass for habit metadata
# TODO: dataclass for habit checkin

class TicktickHabitHandler:
    """Class that accesses the TickTick habits API. Used to post habit checkins.

    Definitions:
    - Habit: A habit is a task that can be checked in multiple times a day, with a goal value.
             Habits have a unique name and id, stored in their metadata.
    - Checkin: A checkin is a single entry of a habit, with a status and a value.
    """

    status_codes = {0: "Not completed", 1: "Failed", 2: "Completed"}
    urls = {
        "habit": "https://api.ticktick.com/api/v2/habits",
        "query_checkin": "https://api.ticktick.com/api/v2/habitCheckins/query",
        "batch_checkin": "https://api.ticktick.com/api/v2/habitCheckins/batch",
    }
    cookies_manager = CookiesManager(
        login_data=LoginData(
            username_env="TICKTICK_EMAIL",
            password_env="TICKTICK_PASSWORD",
            sign_in_url="https://www.ticktick.com/signin",
            selectors=LoginSelectors(
                username='input[placeholder="Email"]',
                password='#password',
                login_button='#app div[class^=body] button'
            )
        ),
        test_cookies_url="https://api.ticktick.com/api/v2/habits",
        test_cookies_response_fn=lambda data: "errorCode" not in data,
        min_num_cookies=5
    )

    def __init__(self, cookies_path: str | None = None):
        self.log = create_logger("Ticktick Habits")
        if cookies_path:
            self.cookies_manager.cookies_path = cookies_path
        self.headers = self.cookies_manager.get_headers_with_cookies()
        self.habits, self.habit_ids = self._get_all_habits_metadata()

    def _make_api_post_request(self, url_name, payload) -> dict[str, str] | None:
        """Returns response or None if an error occurs"""
        try:
            response = requests.post(url=self.urls[url_name],
                                     data=json.dumps(payload),
                                     headers=self.headers
                                     ).json()
            return response
        except Exception as e:
            self.log.error(f"Error sending API request: {e}")
            return None

    def _get_all_habits_metadata(self) -> tuple[dict, dict]:
        """Get the metadata of all habits and their ids"""
        habit_data = requests.get(self.urls["habit"], headers=self.headers).json()
        if "errorId" in habit_data:
            error_message = f"Error loading habits: {habit_data}"
            self.log.error(error_message)
            raise ValueError(error_message)
        habits = {habit["id"]: habit for habit in habit_data}
        habit_ids = {habit["name"]: habit["id"] for habit in habit_data}
        return habits, habit_ids

    def _post_habit_metadata(self, habit_id):
        # todo: update a single habit metadata, to update checkins quickly
        raise NotImplementedError

    def _get_current_utc_time(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + ".000+0000"

    def _aggregate_single_checkin_data(
        self, habit_name: str, date_stamp: str, status: int | None = None, value: int | None = None
    ) -> dict[str, str | int]:
        """Collect all data needed for a single habit checkin."""
        assert not status and value, "You can only provide status or value, not both"
        assert status is not None or value is not None, "You need to provide either status or value"
        assert habit_name in self.habit_ids, f"Habit {habit_name} not found in habits"

        habit_id = self.habit_ids[habit_name]
        habit_goal = int(self.habits[habit_id]["goal"])
        if not value:
            value = habit_goal if status == 2 else 0
        if not status:
            status = 2 if value >= habit_goal else 0

        return {
            "checkinStamp": date_stamp,
            "checkinTime": self._get_current_utc_time(),
            "goal": habit_goal,
            "habitId": habit_id,
            "opTime": self._get_current_utc_time(),
            "status": status,
            "value": value,
        }

    def post_checkin(self,
                     habit_name: str,
                     date_stamp: str,
                     status: int | None = None,
                     value: int | None = None
                     ) -> None:
        """Post a single habit checkin to the TickTick API.

        Args:
            habit_name: Name of the habit to check-in
            date_stamp: Date of the check-in, in the format YYYYMMDD
            status: Status of the check-in. 0: Not completed, 1: Failed, 2: Completed
            value: The value amount to check in. for habits who require multiple units
        """
        checkin_data = self._aggregate_single_checkin_data(habit_name, date_stamp, status, value)
        self.log.info(
            f"Checking {habit_name} on {date_stamp} as {status}: {value}/{checkin_data['habit_goal']}"
        )
        # create payload depending on if a checkin for that day already exists
        existing_checkin_entry = self.get_checkin(checkin_data["habit_id"], date_stamp)
        payload: dict[str, list[dict[str, str | int]]] = {"add": [], "update": [], "delete": []}
        if existing_checkin_entry:
            checkin_data["id"] = existing_checkin_entry["id"]
            payload["update"].append(checkin_data)
        else:
            payload["add"].append(checkin_data)
        response = self._make_api_post_request("batch_checkin", payload)
        if response:
            self.log.info(f"Checkin for {habit_name} successful with response: {response}")

    def get_checkin(self, habit_id, date_stamp):
        """Retrieve a single checkin entry for a habit on a specific date, or None if not found"""
        date = datetime.strptime(date_stamp, "%Y%m%d")
        after_stamp = (date - timedelta(days=1)).strftime("%Y%m%d")
        payload = {"habitIds": [habit_id], "afterStamp": after_stamp}
        response = self._make_api_post_request(self.urls["checkin"], payload)
        assert response, "No response from API for get_checkin"
        habit_entries = response["checkins"][habit_id]
        for entry in habit_entries:
            if entry["checkinStamp"] == int(date_stamp):
                return entry
        return None

    def get_all_checkins(self,
                         after_stamp: str = "19700101",
                         habit_names: list[str] | str | None = None
                         ) -> list[dict[str, str]]:
        """Get all checkins of all habits (or those provided), after a specific date stamp."""
        assert len(after_stamp) == 8, "Date stamp should be in the format YYYYMMDD"
        if not habit_names:
            habits_ids = list(self.habit_ids.values())
        else:
            habit_names = [habit_names] if isinstance(habit_names, str) else habit_names
            habits_ids = [self.habit_ids[habit] for habit in habit_names]
        payload = {"habitIds": habits_ids, "afterStamp": after_stamp}
        response = self._make_api_post_request("query_checkin", payload)
        assert response, "No response from API"
        habit_entries = response["checkins"]
        flattened_habit_entries_list = [
            {**entry, "habitName": self.habits[habit_id]["name"]}
            for habit_id, entries in habit_entries.items()
            for entry in entries
        ]
        return flattened_habit_entries_list


if __name__ == "__main__":
    pass
