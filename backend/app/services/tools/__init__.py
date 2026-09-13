from app.services.tools.registry import tool_registry

from app.services.tools.builtin import (
    HealthCheckTool,
    EchoTool,
    ListAvailableToolsTool,
)

from app.services.tools.task import (
    CreateTaskTool,
)

from app.services.tools.connectors import (
    GitHubFetchTool,
)


def register_builtin_tools():

    tools = [
        HealthCheckTool(),
        EchoTool(),
        ListAvailableToolsTool(),
        CreateTaskTool(),
        GitHubFetchTool(),
    ]

    for tool in tools:

        if tool.name not in {
            item["name"]
            for item in tool_registry.list_tools()
        }:
            tool_registry.register(tool)


register_builtin_tools()
