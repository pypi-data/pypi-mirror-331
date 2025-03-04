from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class Copy(Function):
    """Copy a file or folder to a destination."""

    src = Inputs.path(
        description='Path to a input file or folder.', path='input_path'
    )

    @command
    def copy_path(self):
        return 'echo copying input path...'

    dst = Outputs.path(
        description='Output file or folder.', path='input_path'
    )


@dataclass
class CopyMultiple(Function):
    """Copy a file or folder to multiple destinations."""

    src = Inputs.path(
        description='Path to a input file or folder.', path='input_path'
    )

    @command
    def copy_path(self):
        return 'echo copying input path...'

    dst_1 = Outputs.path(description='Output 1 file or folder.', path='input_path')

    dst_2 = Outputs.path(description='Output 2 file or folder.', path='input_path')

    dst_3 = Outputs.path(description='Output 3 file or folder.', path='input_path')

    dst_4 = Outputs.path(description='Output 4 file or folder.', path='input_path')

    dst_5 = Outputs.path(description='Output 5 file or folder.', path='input_path')

    dst_6 = Outputs.path(description='Output 6 file or folder.', path='input_path')


@dataclass
class CopyFile(Function):
    """Copy a file to a destination."""

    src = Inputs.file(
        description='Path to a input file.', path='input.path'
    )

    @command
    def copy_file(self):
        return 'echo copying input file...'

    dst = Outputs.file(
        description='Output file.', path='input.path'
    )


@dataclass
class CopyFileMultiple(Function):
    """Copy a file to multiple destinations."""

    src = Inputs.file(
        description='Path to a input file.', path='input.path'
    )

    @command
    def copy_file(self):
        return 'echo copying input path...'

    dst_1 = Outputs.file(description='Output 1 file.', path='input.path')

    dst_2 = Outputs.file(description='Output 2 file.', path='input.path')

    dst_3 = Outputs.file(description='Output 3 file.', path='input.path')

    dst_4 = Outputs.file(description='Output 4 file.', path='input.path')

    dst_5 = Outputs.file(description='Output 5 file.', path='input.path')

    dst_6 = Outputs.file(description='Output 6 file.', path='input.path')


@dataclass
class CopyFolder(Function):
    """Copy a folder to a destination."""

    src = Inputs.folder(
        description='Path to a input folder.', path='input.path'
    )

    @command
    def copy_folder(self):
        return 'echo copying input folder...'

    dst = Outputs.folder(
        description='Output folder.', path='input.path'
    )


@dataclass
class CopyFolderMultiple(Function):
    """Copy a folder to multiple destinations."""

    src = Inputs.folder(
        description='Path to a input folder.', path='input.path'
    )

    @command
    def copy_folder(self):
        return 'echo copying input path...'

    dst_1 = Outputs.folder(description='Output 1 folder.', path='input.path')

    dst_2 = Outputs.folder(description='Output 2 folder.', path='input.path')

    dst_3 = Outputs.folder(description='Output 3 folder.', path='input.path')

    dst_4 = Outputs.folder(description='Output 4 folder.', path='input.path')

    dst_5 = Outputs.folder(description='Output 5 folder.', path='input.path')

    dst_6 = Outputs.folder(description='Output 6 folder.', path='input.path')
