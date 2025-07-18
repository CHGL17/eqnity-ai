def format_tool_call(tool_call):
    tool_name = tool_call.get("name", "Herramienta desconocida")
    args = tool_call.get("args", {})
    formatted_args = []
    for key, value in args.items():
        if isinstance(value, str) and len(value) > 50:
            value = value[:50] + "..."
        formatted_args.append(f"  - `{key}`: `{value}`")
    return f"**{tool_name}**\n" + "\n".join(formatted_args)