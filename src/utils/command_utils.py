import subprocess  # noqa: S404

import logfire
from pydantic import BaseModel


class CommandExecutor(BaseModel):
    commands: list[str]

    def run(self) -> tuple[str, str]:
        connection_result = subprocess.run(self.commands, capture_output=True, text=True)  # noqa: S603
        stdout = connection_result.stdout
        stderr = connection_result.stderr
        if stderr:
            logfire.error("Error on executing", stderr=stderr, _exc_info=True)
        logfire.info("Success on executing", stdout=stdout, _exc_info=True)
        return stdout, stderr

    def popen(self) -> tuple[str, str]:
        connection_result_popen = subprocess.Popen(  # noqa: S603
            self.commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = connection_result_popen.communicate()
        if stderr:
            logfire.error("Error on executing", stderr=stderr, _exc_info=True)
        logfire.info("Success on executing", stdout=stdout, _exc_info=True)
        return stdout, stderr
