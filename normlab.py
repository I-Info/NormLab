import sys

from assignment import AssignmentManager
from student import StudentInfo

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage:\npython normlab.py <student list> <Lab package>")
        exit(0)
    student_list_path = sys.argv[1]
    package_path = sys.argv[2]

    info_dict = StudentInfo(student_list_path)
    manager = AssignmentManager()
    manager.process_package(package_path, info_dict)
    manager.check()
