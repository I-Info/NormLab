import os
import zipfile
from typing import Union, List
import rarfile

from student import StudentInfoDict, Student
from fileUtil import extract_file, get_output_path, separate_path_filename
from report import Report


class AssignmentCheck:
    def __init__(self):
        # 定义文件/目录忽略规则
        self.__ignore_dirs = [
            ".git",
            ".idea",
            "target",
        ]
        self.__ignore_file_suffixes = [
            ".class",
            ".gitignore",
            ".DS_Store",
        ]

    # 检查路径
    def check_path(self, path: str) -> bool:
        for i_dir in self.__ignore_dirs:
            if i_dir in path:
                return False
        return True

    # 检查文件
    def check_file(self, filename: str) -> bool:
        for suffix in self.__ignore_file_suffixes:
            if filename[-len(suffix):] == suffix:
                return False
        return True

    def double_check(self, file_path: str) -> bool:
        return self.check_file(file_path) and self.check_path(file_path)


class Assignment:
    """作业类
    """

    def __init__(self, lab_num: str, student: Student, base_path: str, check: AssignmentCheck):
        self.student: Student = student
        self.report: Report = Report()
        self.files: List[str] = []
        self.src_size: int = 0
        self.__name: str = f"{lab_num}-{student}"  # 学生作业的最终名称
        self.__base_path: str = base_path  # 根目录
        self.src_path: str = f"{self.__base_path}/{self.__name}"  # 源代码目录
        self.__check: AssignmentCheck = check

    def process_assignment(self, package: zipfile.ZipFile, file_info: zipfile.ZipInfo):
        """作业标准化处理入口
        """
        # 从包中处理单个作业
        with package.open(file_info, mode='r') as package_io:
            with zipfile.PyZipFile(package_io, 'r') as assignment_zip:
                original_filename = file_info.filename[:-4]  # 初始作业名称
                # 遍历作业压缩包内的文件
                for file in assignment_zip.filelist:
                    filename = file.filename

                    # 过滤去除多于的超星平台.doc文件
                    if filename[-len(original_filename) - 4:-4] == original_filename:
                        continue

                    self.__process_file(assignment_zip, file, self.src_path)

    def __process_file(self, archive: Union[zipfile.ZipFile, rarfile.RarFile], file: any, path: str):
        """处理压缩包中文件
        :param file: 压缩包文件句柄
        :param path: 指定输出路径(doc文件除外)
        """

        archive_name = archive.filename[:-4]  # 压缩包名
        filename = file.filename
        # 获取处理后的路径: 去除与压缩包重名目录
        output_path = path + "/" + get_output_path(filename, archive_name)

        if file.is_dir() or not self.__check.double_check(output_path):  # 使用特定规则忽略文件夹和文件
            return

        pure_path, filename = separate_path_filename(output_path)  # 获取纯路径

        if filename[-4:] == ".doc" or filename[-5:] == ".docx":
            # 将后缀为类.doc的文件作为实验报告，每个学生有且仅有一份有效的实验报告，因此仅保留大小最大的文档。
            if self.report.cmp_update(filename, file.file_size):
                extract_file(archive, file, self.__base_path, f"{self.__name}{filename[-5:]}")  # 将实验报告移动提取到根目录

        else:
            # 处理zip文件
            if filename[-4:] == ".zip":
                with zipfile.PyZipFile(archive.open(file, 'r'), 'r') as zip_file:
                    self.__process_zip(zip_file, pure_path)

            # 处理rar文件
            elif filename[-4:] == ".rar":
                with rarfile.RarFile(archive.open(file, 'r'), 'r') as rar_file:
                    self.__process_rar(rar_file, pure_path)

            # 其他文件解压输出到学生源代码代码目录
            else:
                self.files.append(pure_path[len(self.src_path):] + "/" + filename)  # 将文件路径信息添加到记录中
                self.src_size += file.file_size  # 累加文件大小
                extract_file(archive, file, pure_path, filename)

    def __process_zip(self, archive: zipfile.PyZipFile, path: str):
        """处理zip文件
        """
        # 遍历zip中文件
        for file in archive.filelist:
            self.__process_file(archive, file, path)

    def __process_rar(self, archive: rarfile.RarFile, path: str):
        """处理rar文件
        """
        # 遍历rar中文件
        for file in archive.infolist():
            self.__process_file(archive, file, path)


class AssignmentManager:
    """作业包处理类
    """

    def __init__(self):
        self.__lab_name: str = ""
        self.__reports: List[Report] = []
        self.__assignments: List[Assignment] = []

    def __get_lab_num(self) -> str:
        """获取实验编号
        """
        return self.__lab_name[3:5]

    def process_package(self, package_path: str, stu_info: StudentInfoDict):
        """导入并处理作业包
        """
        check = AssignmentCheck()
        with zipfile.ZipFile(file=package_path, mode="r") as package:
            print("[Info]Processing package..")
            self.__lab_name = package.filename[:-4]  # 实验名称(根目录名)
            # 遍历所有学生作业
            for file in package.filelist:
                stu_num = file.filename[:13]  # 读取学生学号
                student: Student
                try:
                    student = Student(stu_num, stu_info[stu_num])  # 查询学生姓名缩写
                except KeyError:
                    # 学生信息不存在
                    print(
                        f"[Warn] Student shortname with number {stu_num} is not found in student list, using full "
                        "name instead")
                    student = Student(stu_num, file.filename[14:-4])

                print("[Info]Processing Assignment:", student)

                # 处理单个学生作业
                assignment = Assignment(self.__get_lab_num(), student, self.__lab_name, check)
                assignment.process_assignment(package, file)
                self.__assignments.append(assignment)

    def check(self):
        """作业检查
        """
        print("[Info]Assignments check..")
        # 遍历检查
        for assignment in self.__assignments:
            print(assignment.src_size, assignment.files)
            for other in self.__assignments:
                if other == assignment:
                    continue
