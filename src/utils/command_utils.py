import subprocess  # noqa: S404

from pydantic import BaseModel


class CommandExecutor(BaseModel):
    commands: list[str]

    def run(self) -> tuple[str, str]:
        connection_result = subprocess.run(self.commands, capture_output=True, text=True)  # noqa: S603
        stdout = connection_result.stdout
        stderr = connection_result.stderr
        return stdout, stderr

    def popen(self) -> tuple[str, str]:
        connection_result_popen = subprocess.Popen(  # noqa: S603
            self.commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = connection_result_popen.communicate()
        return stdout, stderr
