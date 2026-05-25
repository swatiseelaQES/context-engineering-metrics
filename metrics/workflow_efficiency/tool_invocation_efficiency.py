def tool_invocation_efficiency(tools_called: list[str], required_tools: list[str]) -> float:
    if not required_tools and not tools_called:
        return 1.0
    if not tools_called:
        return 0.0
    useful = sum(tool in required_tools for tool in tools_called)
    unnecessary = max(0, len(tools_called) - useful)
    return max(0.0, useful / len(required_tools) - 0.1 * unnecessary)
