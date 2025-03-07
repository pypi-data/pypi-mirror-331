from attr import dataclass
from dotenv import load_dotenv
from common_utils.web.oauth2_handler import OAuth2Data, OAuth2Handler
from common_utils.web.api_request import post_request, get_request
from common_utils.logger import create_logger
from docs.conf import project

load_dotenv()


@dataclass
class TickTickProject:
    name: str
    id: str | None = None
    sortOrder: int = 0
    viewMode: str = "list"
    kind: str = 'TASK'
    groupId: str | None = None
    color: str | None = None
    permission: str | None = None
    closed: bool | None = None


class TickTickTaskHandler:
    log = create_logger("TickTick TaskHandler")
    oauth_data = OAuth2Data(
        client_id_env="TICKTICK_CLIENT_ID",
        client_secret_env="TICKTICK_CLIENT_SECRET",
        redirect_uri_env="TICKTICK_REDIRECT_URI",
        scope_env="TICKTICK_SCOPE",
        authorize_url="https://ticktick.com/oauth/authorize",
        token_url="https://ticktick.com/oauth/token",
    )

    urls = {
        "projects": "https://api.ticktick.com/open/v1/project",
        "post_task": "https://api.ticktick.com//open/v1/task",
    }

    def __init__(self):
        self.oauth_handler = OAuth2Handler(self.oauth_data)
        self.token = self.oauth_handler.get_token()
        self.headers = {"Authorization": f"Bearer {self.token['access_token']}"}
        self.projects = self.get_projects()

    def get_projects(self) -> list[TickTickProject]:
        response = get_request("https://api.ticktick.com/open/v1/project", headers=self.headers)
        projects = [TickTickProject(**project) for project in response]
        self.log.debug(f"Received projects: {projects}")
        return projects

    def update_project(self):  # TODO
        raise NotImplementedError

    def create_project(self, project: TickTickProject):  # TODO
        raise NotImplementedError

    def get_project_tasks(self, project_id: str):  # TODO
        data = get_request(f"{self.urls['projects']}/{project_id}/data", headers=self.headers)
        print(data)

    def get_task(self):  # TODO
        raise NotImplementedError

    def create_task(self):  # TODO
        raise NotImplementedError

    def update_task(self):  # TODO
        raise NotImplementedError

    def complete_task(self):  # TODO
        raise NotImplementedError

    def delete_task(self):  # TODO
        raise NotImplementedError


if __name__ == "__main__":
    tasks_handler = TickTickTaskHandler()
    for project in tasks_handler.projects:
        tasks_handler.get_project_tasks(project.id)

