import getpass

import logfire

logfire.configure(
    send_to_logfire=True,
    token="t5yWZMmjyRH5ZVqvJRwwHHfm5L3SgbRjtkk7chW3rjSp",
    project_name="auto-click",
    service_name=f"{getpass.getuser()}",
    trace_sample_rate=1.0,
    show_summary=True,
    data_dir=".logfire",
    collect_system_metrics=True,
    fast_shutdown=True,
    inspect_arguments=True,
    pydantic_plugin=logfire.PydanticPlugin(record="failure"),
)
