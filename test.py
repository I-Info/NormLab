import os
import shutil
import zipfile
from pathlib import Path

import assignment
import student
from student import StudentInfo


class TestNormLab:
    """测试类"""

    def test_case_01_inner(self):
        path = Path("test-case-01")
        output_path = path / "ZipInner/Output"
        shutil.rmtree(output_path)
        ass = assignment.Assignment("01", student.Student("", "中文"), output_path,
                                    assignment.AssignmentChecker(), True)
        with zipfile.ZipFile(path / "ZipInner/Lab01-中文.zip") as package:
            ass.process_assignment(package)
        rm_docs(output_path)
        expect_path = path / "ExpectedOutput"
        assert check_output_expected(expect_path, output_path)

    def test_case_01_outer(self):
        path = Path("test-case-01")
        output_path = path / "ZipOuter/Output"
        shutil.rmtree(output_path)
        ass = assignment.Assignment("01", student.Student("", "中文"), output_path,
                                    assignment.AssignmentChecker(), True)
        with zipfile.ZipFile(path / "ZipOuter/Lab01-中文.zip") as package:
            ass.process_assignment(package)
        rm_docs(output_path)
        expect_path = path / "ExpectedOutput"
        assert check_output_expected(expect_path, output_path)

    def test_case_02(self):
        path = Path("test-case-02")
        info_dict = StudentInfo("student-list.csv")
        manager = assignment.AssignmentManager("Lab03-JUnit for Unit Test")
        output_path = path / "Output"
        shutil.rmtree(output_path)
        with zipfile.ZipFile(path / "Lab03-JUnit for Unit Test.zip", "r") as package:
            manager.process_package(package, info_dict, output_path)
            manager.check(output_path)
        expect_path = path / "Output-Expected"
        assert check_output_expected(expect_path, output_path)

    def test_case_03(self):
        path = Path("test-case-03")
        info_dict = StudentInfo("student-list.csv")
        manager = assignment.AssignmentManager("Lab03-JUnit for Unit Test")
        output_path = path / "Output"
        shutil.rmtree(output_path)
        with zipfile.ZipFile(path / "Lab03-JUnit for Unit Test.zip", "r") as package:
            manager.process_package(package, info_dict, output_path)
        expect_path = path / "Output-Expected"
        assert check_output_expected(expect_path, output_path)


# Remove unnecessary docs
def rm_docs(path: Path):
    for sub in path.iterdir():
        if sub.is_file() and sub.suffix in [".doc", ".docx"]:
            sub.unlink()


def check_output_expected(exp: Path, out: Path) -> bool:
    exp_files = []
    for root, dirs, files in os.walk(exp):
        for name in files:
            exp_files.append(os.path.join(root, name)[len(str(exp)):])

    for root, dirs, files in os.walk(out):
        for name in files:
            out_file = os.path.join(root, name)[len(str(out)):]
            if out_file not in exp_files:
                return False

    return True
