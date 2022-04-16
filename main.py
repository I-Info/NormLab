import difflib
from assignment import AssignmentPackage
from student import StudentInfoDict


def test_lib():
    s = difflib.SequenceMatcher(None,
                                "2020-01-202003340303-dch",
                                "2020-01-202001010432-lfeofe", True)
    print(round(s.ratio(), 3))


if __name__ == '__main__':
    info_dict = StudentInfoDict("student-list.csv")
    package = AssignmentPackage("Lab03-JUnit for Unit Test.zip")
    package.process_package(info_dict)
