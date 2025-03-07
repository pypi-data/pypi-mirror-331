# TODO if python version >= 3.10: inherit from a class, eg. LineHeader
from abc import ABC
from dataclasses import dataclass


# Before python3.10, dataclasses cannot be inherited, that's why there is no
# parent class for the headers.
class Line(ABC):
    def to_clearcase_format(self):
        pass


@dataclass
class InsertHeader(Line):
    line_nb_before: int
    line_nb_after: int
    lines_changed_before: int
    lines_changed_after: int

    def to_clearcase_format(self):
        end_line_after = self.line_nb_after + self.lines_changed_after - 1
        return f"-----[after {self.line_nb_before} inserted {self.line_nb_after}-{end_line_after}]-----"


@dataclass
class DeleteHeader(Line):
    line_nb_before: int
    line_nb_after: int
    lines_changed_before: int
    lines_changed_after: int

    def to_clearcase_format(self):
        return f"-----[deleted {self.line_nb_before} after {self.line_nb_after}]-----"


@dataclass
class ChangeHeader(Line):
    line_nb_before: int
    line_nb_after: int
    lines_changed_before: int
    lines_changed_after: int

    def to_clearcase_format(self):
        if self.lines_changed_before > 1:
            end_line_before = self.line_nb_before + self.lines_changed_before - 1
            before = f"{self.line_nb_before}-{end_line_before}"
        else:
            before = self.line_nb_before

        if self.lines_changed_after > 1:
            end_line_after = self.line_nb_after + self.lines_changed_after - 1
            after = f"{self.line_nb_after}-{end_line_after}"
        else:
            after = self.line_nb_after
        return f"-----[{before} changed to {after}]-----"


@dataclass
class InsertLine(Line):
    statement: str

    def to_clearcase_format(self):
        return f"> {self.statement}"


@dataclass
class DeleteLine(Line):
    statement: str

    def to_clearcase_format(self):
        return f"< {self.statement}"


@dataclass
class FileHeader(Line):
    file1: str
    file2: str

    def to_clearcase_format(self):
        return f"""********************************
<<< file 1: {self.file1}
>>> file 2: {self.file2}
********************************"""


class TransitionLine(Line):
    def to_clearcase_format(self):
        return "---"
