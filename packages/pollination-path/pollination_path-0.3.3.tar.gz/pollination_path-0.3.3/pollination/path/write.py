from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class WriteInt(Function):
    """Write an integer to a text file."""

    src = Inputs.int(
        description='Integer to write into a text file.'
    )

    @command
    def write_integer(self):
        return 'echo {{self.src}} > input_int.txt'

    dst = Outputs.file(
        description='The integer in a text file.', path='input_int.txt'
    )
