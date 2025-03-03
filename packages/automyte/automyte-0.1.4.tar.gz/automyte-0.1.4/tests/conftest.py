import os
import typing as t
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

_DirName: t.TypeAlias = str
_FileName: t.TypeAlias = str
_FileContents: t.TypeAlias = str
_ProjectStructure: t.TypeAlias = dict[_DirName | _FileName, t.Union[_FileContents, "_ProjectStructure"]]


@pytest.fixture
def tmp_local_project_factory():
    """Setup a tmp project structure with folders, files and their contents for testing.

    Returns a factory function which accepts dictionary structure where we specify project structure.
    All projects are created in tmp folders which are cleaned up automatically after each run.

    Don't pass "dir" argument, as it is only used for recursive call for internal implementation.

    Example:
        tmp_local_project_factory(structure={
            'src': {
                'subdir1': {
                    'hello.txt': 'this will be the text for src/subdir1/hello.txt file',
                    'bye.py': 'print("good bye")',
                },
                'subdir2': {...},
            ...
            }
        })
    """
    rootdirs = []
    try:

        def _create_tmp_project(structure: _ProjectStructure, dir: str | None = None):
            if dir:  # Recursive call, just need to create child dirs.
                os.mkdir(dir)
                current_dir = dir
            else:  # First call, need to create TMP dir as parent and add it to array for removal.
                new_tmp_dir = TemporaryDirectory()
                rootdirs.append(new_tmp_dir)
                current_dir = new_tmp_dir.name

            for name, content in structure.items():
                if isinstance(content, str):  # Encountered a file.
                    with open(Path(current_dir) / name, "w") as f:
                        f.write(content)
                else:  # Encoruntered a folder, so need to generate the whole structure again, recursively.
                    _create_tmp_project(structure=content, dir=f"{current_dir}/{name}")

            return current_dir

        yield _create_tmp_project

    finally:
        for dir in rootdirs:
            dir.cleanup()
