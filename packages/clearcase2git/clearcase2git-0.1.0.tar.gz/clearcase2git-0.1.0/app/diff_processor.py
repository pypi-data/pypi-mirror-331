import re
from pathlib import Path
from typing import List, Optional

from app import git_commands
from app.models import (
    ChangeHeader,
    DeleteHeader,
    DeleteLine,
    FileHeader,
    InsertHeader,
    InsertLine,
    Line,
    TransitionLine,
)


class DiffProcessor:
    def __init__(
        self,
        current_file: Path,
        old_file: Optional[Path] = None,
        commit: Optional[str] = None,
    ):
        self.current_file: Path = current_file
        self.old_file: Path = old_file
        self.commit: str = commit
        self.lines: List[Line] = []

    def to_clearcase_format(self) -> str:
        if self.old_file:
            git_diff = git_commands.diff_from_filesystem(self.old_file, self.current_file)
        elif self.commit:
            git_diff = git_commands.diff_from_git_history(current_file=self.current_file, commit_sha1=self.commit)
        else:
            raise ValueError("Missing a file or a git version to compare")

        git_lines = git_diff.splitlines()
        for git_line in git_lines:
            self.add_line_processor(git_line)
            self.add_transition_line_if_necessary()

        return "\n".join(line.to_clearcase_format() for line in self.lines)

    def add_line_processor(self, line: str) -> None:
        if line.startswith("diff"):
            regex = re.compile(r"diff --git [1,c](.+) [2,w](.+)")
            file1, file2 = regex.findall(line)[0]
            self.lines.append(FileHeader(file1=file1, file2=file2))

        elif line.startswith("@"):
            self.lines.append(self.get_header(line))

        elif (
            line.startswith("--- 1")
            or line.startswith("+++ 2")
            or line.startswith("index")
        ):
            # lines to be ignored
            pass

        elif line.startswith("+"):
            data = line.replace("+", "", 1)
            self.lines.append(InsertLine(statement=data))

        elif line.startswith("-"):
            data = line.replace("-", "", 1)
            self.lines.append(DeleteLine(statement=data))

        else:
            raise ValueError(f"The case is not handled for '{line}'")

    def get_header(self, line: str) -> Line:
        regex = re.compile(r"@+ -(\d+)(,(\d+))? \+(\d+)(,(\d+))? @+")
        (
            line_nb_before,
            _,
            change_size_before,
            line_nb_after,
            _,
            change_size_after,
        ) = regex.findall(line)[0]

        # convert strings to integers
        line_nb_before = int(line_nb_before)
        line_nb_after = int(line_nb_after)
        change_size_before = int(change_size_before or "-1")
        change_size_after = int(change_size_after or "-1")

        if self.is_delete(change_size_before, change_size_after):
            return DeleteHeader(
                line_nb_before=line_nb_before,
                line_nb_after=line_nb_after,
                lines_changed_before=change_size_before,
                lines_changed_after=change_size_after,
            )
        elif self.is_insert(change_size_before, change_size_after):
            return InsertHeader(
                line_nb_before=line_nb_before,
                line_nb_after=line_nb_after,
                lines_changed_before=change_size_before,
                lines_changed_after=change_size_after,
            )
        elif self.is_change(change_size_before, change_size_after):
            if change_size_before <= 0:
                change_size_before = 1
            if change_size_after <= 0:
                change_size_after = 1
            return ChangeHeader(
                line_nb_before=line_nb_before,
                line_nb_after=line_nb_after,
                lines_changed_before=change_size_before,
                lines_changed_after=change_size_after,
            )
        else:
            raise ValueError(f"The case is not handled for the header '{line}'")

    def is_delete(self, change_size_before, change_size_after) -> bool:
        return change_size_before == -1 and change_size_after == 0

    def is_insert(self, change_size_before, change_size_after) -> bool:
        return change_size_before == 0 and change_size_after > 0

    def is_change(self, change_size_before, change_size_after) -> bool:
        return (
            (change_size_before < change_size_after)
            or (change_size_before == change_size_after)
            or (change_size_before > 0 and change_size_after == -1)
        )

    def add_transition_line_if_necessary(self):
        if (
            len(self.lines) > 2
            and type(self.lines[-2]) is DeleteLine
            and type(self.lines[-1]) is InsertLine
        ):
            self.lines.insert(-1, TransitionLine())
