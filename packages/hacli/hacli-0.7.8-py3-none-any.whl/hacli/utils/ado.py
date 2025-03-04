import json
import os
from os import environ
from string import Template
from typing import Union, List

import typer
from azure.devops.connection import Connection
from azure.devops.exceptions import AzureDevOpsServiceError
from azure.devops.v7_0.dashboard import TeamContext, Dashboard, DashboardClient, Widget
from azure.devops.v7_0.git import GitClient
from azure.devops.v7_0.pipelines import PipelinesClient, Pipeline, Run
from azure.devops.v7_0.work_item_tracking import WorkItemTrackingClient, WorkItemReference, Wiql, WorkItemQueryResult, \
    WorkItem
from msrest.authentication import BasicAuthentication
from rich.prompt import Confirm


class ADOPipelineClient:
    """Azure DevOps 流水线客户端"""

    def __init__(self, client: PipelinesClient, project: str):
        self.client = client
        self.project = project

    def trigger_pipeline(self, pipeline_id: int, run_parameters: dict) -> Run:
        """触发流水线执行"""
        return self.client.run_pipeline(
            pipeline_id=pipeline_id,
            project=self.project,
            run_parameters=run_parameters
        )

    def get_pipeline(self, pipeline_id: int) -> Pipeline:
        """获取指定 ID 的流水线"""
        return self.client.get_pipeline(self.project, pipeline_id=pipeline_id)

    def list_pipelines(self) -> list[Pipeline]:
        """列出所有流水线"""
        return self.client.list_pipelines(self.project, top=9999)

    def get_pipeline_by_name(self, pipeline_name: str) -> Union[Pipeline, None]:
        """根据名称获取流水线"""
        pipelines: list[Pipeline] = self.list_pipelines()
        for pipeline in pipelines:
            if pipeline.name == pipeline_name:
                return pipeline
        return None


class ADODashboardClient:
    """Azure DevOps 仪表板客户端"""

    def __init__(self, client: DashboardClient, project: str):
        self.client = client
        self.project = project

    def get_dashboard(self, team: str, dashboard_id: str) -> Dashboard:
        """获取指定团队的仪表板"""
        team_context = TeamContext(project=self.project, team=team)
        return self.client.get_dashboard(team_context, dashboard_id=dashboard_id)

    def get_widget_from_dashboard(self, team: str, dashboard_id: str, widget_id: str) -> Widget:
        """获取仪表板中的小部件"""
        team_context = TeamContext(project=self.project, team=team)
        return self.client.get_widget(team_context, dashboard_id=dashboard_id, widget_id=widget_id)


class ADOGitClient:
    """Azure DevOps Git 客户端"""

    def __init__(self, client: GitClient, project: str):
        self.client = client
        self.project = project

    def check_release_branch(self, repository_id: str, release_branch_name: str) -> bool:
        """检查发布分支是否存在"""
        try:
            self.client.get_branch(
                repository_id=repository_id,
                name=release_branch_name,
                project=self.project
            )
            return True
        except AzureDevOpsServiceError:
            return False


class ADOWorkItemTrackingClient:

    def __init__(self, client: WorkItemTrackingClient, project: str):
        self.client = client
        self.project = project
        self.team_context = TeamContext(self.project)

    def query_first_work_item_reference(self, wiql_query: str) -> Union[WorkItemReference, None]:
        try:
            wiql = Wiql(query=wiql_query)
            query_result: WorkItemQueryResult = self.client.query_by_wiql(wiql, team_context=self.team_context, top=1)
            if query_result.work_items:
                return query_result.work_items[0]
            return None
        except AzureDevOpsServiceError:
            return None

    def query_work_item_reference(self, wiql_query: str) -> Union[List[WorkItemReference], None]:
        try:
            wiql = Wiql(query=wiql_query)
            query_result: WorkItemQueryResult = self.client.query_by_wiql(wiql, team_context=self.team_context)
            if query_result.work_items:
                return query_result.work_items
            return None
        except AzureDevOpsServiceError:
            return None

    def query_working_items(self, work_item_ids: list[int], fields: list[str]) -> list[WorkItem]:
        try:
            return self.client.get_work_items(work_item_ids, project=self.project, fields=fields)
        except AzureDevOpsServiceError:
            return []

    def query_working_item(self, work_item_id: int, fields: list[str]) -> Union[WorkItem, None]:
        try:
            return self.client.get_work_item(work_item_id, project=self.project, fields=fields)
        except AzureDevOpsServiceError:
            return None


class AzureDevOpsClient:
    """Azure DevOps 客户端主类"""

    def __init__(self, project: str):
        self.org_url = environ["ORG_URL"]
        self.personal_access_token = environ["PERSONAL_ACCESS_TOKEN"]
        self.project = project

        # 初始化连接
        self.credentials = BasicAuthentication('', self.personal_access_token)
        self.connection = Connection(base_url=self.org_url, creds=self.credentials)

        # 初始化子客户端
        self.pipeline = ADOPipelineClient(
            self.connection.clients.get_pipelines_client(),
            self.project
        )
        self.dashboard = ADODashboardClient(
            self.connection.clients.get_dashboard_client(),
            self.project
        )
        self.git = ADOGitClient(
            self.connection.clients.get_git_client(),
            self.project
        )
        self.work_items = ADOWorkItemTrackingClient(
            self.connection.clients.get_work_item_tracking_client(),
            self.project
        )


def execute_pipeline(
        release: str,
        pipeline_name_env_key: str,
        pipeline_parameter_env_key: str,
        project_name_env_key: str = "PROJECT_LOCAL_NAME",
        project_repo_env_key: str = "PROJECT_LOCAL_REPO",
        **kwargs
) -> Union[dict, None]:
    """
    执行 Azure DevOps 流水线。

    Args:
        release: 发布版本
        pipeline_name_env_key: 流水线名称环境变量键
        pipeline_parameter_env_key: 流水线参数环境变量键
        project_name_env_key: 项目名称环境变量键
        project_repo_env_key: 项目仓库环境变量键
        **kwargs: 其他参数
    """
    kwargs["release"] = release
    client = AzureDevOpsClient(environ[project_name_env_key])

    # 检查发布分支是否存在
    release_branch_name = release if release == "master" else os.environ[
        "RELEASE_GIT_LOCAL_RELEASE_NAME_TEMPLATE"].format(release=release)
    release_branch_exist = client.git.check_release_branch(
        environ[project_repo_env_key],
        release_branch_name
    )
    if not release_branch_exist:
        raise Exception(f"Release branch [red]{release_branch_name}[/red] does not exist")

    # 获取并检查流水线
    pipeline_name = Template(environ[pipeline_name_env_key]).safe_substitute(**kwargs)
    pipeline = client.pipeline.get_pipeline_by_name(pipeline_name)
    if not pipeline:
        raise Exception(f"Pipeline {pipeline_name} is not existed")

    # 准备流水线参数
    pipeline_parameter_template = environ[pipeline_parameter_env_key]
    run_parameters = json.loads(Template(pipeline_parameter_template).safe_substitute(**kwargs))

    # 确认并触发流水线
    if not Confirm.ask(f"Are you sure to trigger pipeline [red]{pipeline_name}[/red]?"):
        return None

    web_url: str = pipeline._links.additional_properties.get("web").get('href')
    typer.launch(web_url)
    trigger_pipeline: Run = client.pipeline.trigger_pipeline(pipeline_id=pipeline.id, run_parameters=run_parameters)
    return trigger_pipeline.as_dict()
