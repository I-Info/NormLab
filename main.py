from assignment import AssignmentManager
from student import StudentInfoDict

if __name__ == '__main__':
    info_dict = StudentInfoDict("student-list.csv")
    manager = AssignmentManager()
    manager.process_package("Lab03-JUnit for Unit Test.zip", info_dict)
    manager.check()
