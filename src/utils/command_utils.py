import subprocess

from pydantic import Field, BaseModel


class CommandExecutor(BaseModel):
    """A class for executing shell commands.

    Attributes:
        commands (list[str]): A list of commands to be executed.

    Methods:
        run: Executes the command and captures the output.
        popen: Executes the command using subprocess.Popen and returns the stdout and stderr outputs
    """

    commands: list[str] = Field(
        ..., description="The list of commands to be executed.", frozen=True, deprecated=False
    )

    def run(self) -> tuple[str, str]:
        """Executes the command and captures the output.

        Returns:
            A tuple containing the stdout and stderr as strings.
        """
        connection_result = subprocess.run(self.commands, capture_output=True, text=True)  # noqa: S603
        stdout = connection_result.stdout
        stderr = connection_result.stderr
        return stdout, stderr

    def popen(self) -> tuple[str, str]:
        """Executes the command using subprocess.Popen and returns the stdout and stderr outputs.

        Returns:
            A tuple containing the stdout and stderr outputs as strings.
        """
        connection_result_popen = subprocess.Popen(  # noqa: S603
            self.commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = connection_result_popen.communicate()
        return stdout, stderr
