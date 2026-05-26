def tool_invocation_efficiency(invoked_tools, required_tools):
    invoked_tools = invoked_tools or []
    required_tools = required_tools or []

    if not required_tools:
        return 0.0

    useful = len([
        tool for tool in invoked_tools
        if tool in required_tools
    ])

    unnecessary = len([
        tool for tool in invoked_tools
        if tool not in required_tools
    ])

    score = (useful / len(required_tools)) - (0.1 * unnecessary)

    return max(0.0, round(score, 4))