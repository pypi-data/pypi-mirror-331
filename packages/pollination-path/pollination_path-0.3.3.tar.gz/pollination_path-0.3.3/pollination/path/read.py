from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class ReadJSON(Function):
    """Read content of a JSON file as a dictionary."""

    src = Inputs.path(
        description='Path to a input JSON file.', path='input_path'
    )

    @command
    def list_dir(self):
        return 'echo parsing JSON information to a dictionary...'

    data = Outputs.dict(
        description='The content of JSON file as a dictionary.', path='input_path'
    )


@dataclass
class ReadJSONList(Function):
    """Read the content of a JSON file as a list."""

    src = Inputs.path(
        description='Path to a input JSON file.', path='input_path'
    )

    @command
    def list_dir(self):
        return 'echo parsing JSON information to a list...'

    data = Outputs.list(
        description='The content of JSON file as a list.', path='input_path'
    )


@dataclass
class ReadInt(Function):
    """Read content of a text file as an integer."""

    src = Inputs.path(
        description='Path to a input text file.', path='input_path'
    )

    @command
    def read_integer(self):
        return 'echo parsing text information to an integer...'

    data = Outputs.int(
        description='The content of text file as an integer.', path='input_path'
    )
