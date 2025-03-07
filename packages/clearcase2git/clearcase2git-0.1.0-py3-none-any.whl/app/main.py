from pathlib import Path, PosixPath

from app.diff_processor import DiffProcessor
from app.rtf_writer import RtfWriter

app_dir = Path(__file__).parent
tests_dir = app_dir.parent / "tests"
data_dir = tests_dir / "data"
colour_diff_dir = data_dir / "Produces colour diff"

rtf_writer = RtfWriter(Path(__file__).parent / "tmp")


def main():
    files = [
        (
            colour_diff_dir / "CNF_AntiMalwareGacf_V01.00_v1.xsd",
            colour_diff_dir / "CNF_AntiMalwareGacf_V01.00_v2.xsd",
            True,
        ),
        (
            colour_diff_dir / "GAL-GMS-MGF_MM_MissionMntData_V02.00.asn",
            colour_diff_dir / "GAL-GMS-MGF_MM_MissionMntData_V03.00.asn",
            True,
        ),
        (
            "e6c7b70",
            colour_diff_dir / "MGF-MIB_V03.00.mib",
            False,
        ),
    ]
    for file1, file2, is_file in files:
        if is_file:
            diff_processor = DiffProcessor(current_file=file2, old_file=file1)
            filename = f"diff-{file1.name}-{file2.name}.rtf"
            diff = diff_processor.to_clearcase_format()
            rtf_writer.write(diff, filename, file1, file2)
        else:
            diff_processor = DiffProcessor(current_file=file2, commit=file1)
            filename = f"diff-{file1}-{file2.name}.rtf"
            diff = diff_processor.to_clearcase_format()
            rtf_writer.write(diff, filename, file2)
        # rtf_writer.display(filename)


if __name__ == "__main__":
    main()
