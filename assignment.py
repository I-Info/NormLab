import zipfile
from typing import Union
import rarfile

from student import StudentInfoDict, Student
from fileUtil import extract_file, get_output_path, separate_path_filename


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

    def __init__(self, lab_num: str, student: Student, check: AssignmentCheck):
        self.__student: Student = student
        self.__name: str = f"{lab_num}-{student}"  # 学生作业的最终名称
        self.__base_path: str = ""  # 根目录
        self.__report_size: int = -1  # 记录实验报告大小
        self.__report_original_filename: str = ""  # 记录实验报告原始名称
        self.__check: AssignmentCheck = check

    def __get_src__path(self) -> str:
        """ 获取学生源代码目录
        """
        return f"{self.__base_path}/{self.__name}"

    def process_assignment(self, base_path: str, package: zipfile.ZipFile, file_info: zipfile.ZipInfo):
        """ 作业处理入口
        """
        self.__base_path = base_path
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

                    self.__process_file(assignment_zip, file, self.__get_src__path())

    def __process_file(self, archive: Union[zipfile.ZipFile, rarfile.RarFile], file: any, path: str):
        """ 处理压缩包中文件
        :param file: 压缩包文件句柄
        :param path: 指定输出路径(doc文件除外)
        """

        archive_name = archive.filename[:-4]  # 压缩包名
        filename = file.filename
        output_path = path + "/" + get_output_path(filename, archive_name)  # 获取处理后的路径

        if file.is_dir() or not self.__check.double_check(output_path):  # 使用特定规则忽略文件夹和文件
            return

        pure_path, filename = separate_path_filename(output_path)  # 获取纯路径

        if filename[-4:] == ".doc" or filename[-5:] == ".docx":
            # 将后缀为类.doc的文件作为实验报告，每个学生有且仅有一份有效的实验报告，因此仅保留大小最大的文档。
            file_size = file.file_size
            if file_size > self.__report_size:
                self.__report_size = file.file_size
                self.__report_original_filename = file.filename
                # 将实验报告移动提取到根目录
                extract_file(archive, file, self.__base_path, f"{self.__name}{filename[-5:]}")

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
                extract_file(archive, file, pure_path, filename)

    def __process_zip(self, archive: zipfile.PyZipFile, path: str):
        """ 处理zip文件
        """
        # 遍历zip中文件
        for file in archive.filelist:
            self.__process_file(archive, file, path)

    def __process_rar(self, archive: rarfile.RarFile, path: str):
        """ 处理rar文件
        """
        # 遍历rar中文件
        for file in archive.infolist():
            self.__process_file(archive, file, path)


class AssignmentPackage:
    """作业包类
    """

    def __init__(self, path: str):
        self.__lab_name: str = ""
        self.__file_path: str = path

    # 获取实验编号
    def __get_lab_num(self) -> str:
        return self.__lab_name[3:5]

    def process_package(self, stu_info: StudentInfoDict):
        check = AssignmentCheck()
        with zipfile.ZipFile(file=self.__file_path, mode="r") as package:
            print("[Info]Processing package..")
            self.__lab_name = package.filename[:-4]  # 输出根目录名
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
                assignment = Assignment(self.__get_lab_num(), student, check)
                assignment.process_assignment(self.__lab_name, package, file)
