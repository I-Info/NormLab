import sys
import zipfile
from pathlib import Path

from assignment import AssignmentManager
from student import StudentInfo

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage:\npython normlab.py <student list> <Lab package>")
        exit(0)
    student_list_path = sys.argv[1]
    package_path = Path(sys.argv[2])

    info_dict = StudentInfo(student_list_path)
    manager = AssignmentManager(package_path.name[:-len(package_path.suffix)])
    with zipfile.ZipFile(package_path, "r") as package:
        manager.process_package(package, info_dict)
        manager.check()
