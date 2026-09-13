from app.services.tools.registry import tool_registry

from app.services.tools.builtin import (
    HealthCheckTool,
    EchoTool,
    ListAvailableToolsTool,
)

from app.services.tools.task import (
    CreateTaskTool,
)


def register_tools():

    tools = [
        HealthCheckTool(),
        EchoTool(),
        ListAvailableToolsTool(),
        CreateTaskTool(),
    ]

    existing = {
        tool["name"]
        for tool in tool_registry.list_tools()
    }

    for tool in tools:

        if tool.name not in existing:
            tool_registry.register(tool)
            existing.add(tool.name)
