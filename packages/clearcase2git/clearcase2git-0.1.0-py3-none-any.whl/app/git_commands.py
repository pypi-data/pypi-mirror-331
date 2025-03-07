import subprocess
from pathlib import Path


def diff_from_filesystem(file_v1: Path, file_v2: Path) -> str:
    # base command
    command = ["git", "diff"]
    # makes git display only changed lines
    command.append("--unified=0")
    # indicate that the comparison is between files from the filesystem and not from Git
    command.append("--no-index")
    # add the 2 files to compare
    command.append(str(file_v1.absolute()))
    command.append(str(file_v2.absolute()))
    # run the command
    response = subprocess.run(command, capture_output=True)
    # return the result as string
    return response.stdout.decode("utf-8")


def diff_from_git_history(current_file: Path, commit_sha1: str) -> str:
    # base command
    command = ["git", "diff"]
    # makes git display only changed lines
    command.append("--unified=0")
    # add the sha1 of the revision to compare
    command.append(commit_sha1)
    # add the files to compare
    command.append(str(current_file.absolute()))
    # run the command
    response = subprocess.run(command, capture_output=True)
    # return the result as string
    return response.stdout.decode("utf-8")
