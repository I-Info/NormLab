import csv
import difflib
import zipfile
from pathlib import Path
from typing import Union, List, Tuple
from os import PathLike
import rarfile

from fileUtil import extract_file, separate_path_filename, decode_file_name
from report import Report
from source import Source, SourceAnalyzer
from student import StudentInfo, Student


class AssignmentChecker:
    def __init__(self):
        # 定义文件/目录忽略规则
        self.__ignore_dirs = [
            ".git",
            ".idea",
            "target",
            "__MACOSX"
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

    def check_both(self, file_path: str) -> bool:
        return self.check_file(file_path) and self.check_path(file_path)


class Assignment:
    """作业类
    """

    def __init__(self, lab_num: str, student: Student, base_path: PathLike[str], checker: AssignmentChecker):
        self.student: Student = student
        self.report: Report = Report()
        self.__name: str = f"Lab{lab_num}-{student}"  # 学生作业的最终名称
        self.__base_path: PathLike[str] = base_path  # 根目录
        self.src_path: str = f"{self.__base_path}/{self.__name}"  # 源代码目录
        self.__checker: AssignmentChecker = checker
        self.source: Source = Source()

    def process_assignment(self, assignment_zip: zipfile.ZipFile):
        """作业标准化处理入口
        """
        original_filename = assignment_zip.filename[:-4]
        # 遍历作业压缩包内的文件
        for file in assignment_zip.filelist:
            filename = decode_file_name(file.filename)

            # 过滤去除多于的超星平台.doc文件
            if filename[-len(original_filename) - 4:-4] == original_filename:
                # print(filename)
                continue

            self.__process_file(assignment_zip, file, Path(self.src_path))

        # 后序检查
        path = Path(self.src_path)
        if path.exists():
            remove_single_src_dir(path)
            print(path, original_filename)
            remove_single_begin_dir(path, separate_path_filename(original_filename)[1])

    def __process_file(self, archive: Union[zipfile.ZipFile, rarfile.RarFile], file: any, path: PathLike[str]):
        """处理压缩包中文件
        :param file: 压缩包文件句柄
        :param path: 指定输出路径(doc文件除外)
        """

        # archive_name = decode_file_name(archive.filename)[:-4]  # 压缩包名
        filename = decode_file_name(file.filename)

        output_path = f"{path}/{filename}"

        if file.is_dir() or not self.__checker.check_both(output_path):  # 使用特定规则忽略文件夹和文件
            return

        pure_path, filename = separate_path_filename(output_path)  # 获取纯路径

        pure_path = Path(pure_path)

        if filename[-4:] == ".doc" or filename[-5:] == ".docx":
            # 将后缀为类.doc的文件作为实验报告，每个学生有且仅有一份有效的实验报告，因此仅保留大小最大的文档。
            if self.report.cmp_update(filename, file.file_size):
                extract_file(archive, file, self.__base_path, f"{self.__name}{filename[-5:]}")  # 将实验报告移动提取到根目录

        # 处理zip文件
        if filename[-4:] == ".zip":
            with zipfile.ZipFile(archive.open(file, 'r'), 'r') as zip_file:
                self.__process_zip(zip_file, pure_path / filename[:-4])

        # 处理rar文件
        elif filename[-4:] == ".rar":
            with rarfile.RarFile(archive.open(file, 'r'), 'r') as rar_file:
                self.__process_rar(rar_file, pure_path / filename[:-4])

        # 其他文件解压输出到学生源代码代码目录
        else:
            # 将文件路径信息添加到记录中，累加大小
            self.source.append(output_path[len(self.src_path):], file.file_size)
            extract_file(archive, file, pure_path, filename)

    def __process_zip(self, archive: zipfile.ZipFile, path: Path):
        """处理zip文件
        """
        # 遍历zip中文件
        for file in archive.filelist:
            self.__process_file(archive, file, path)
        print(path, separate_path_filename(decode_file_name(archive.filename[:-4]))[1])
        remove_single_begin_dir(path, separate_path_filename(decode_file_name(archive.filename[:-4]))[1])

    def __process_rar(self, archive: rarfile.RarFile, path: Path):
        """处理rar文件
        """
        # 遍历rar中文件
        for file in archive.infolist():
            self.__process_file(archive, file, path)
        remove_single_begin_dir(path, separate_path_filename(decode_file_name(archive.filename[:-4]))[1])


class AssignmentManager:
    """作业包处理类
    """

    def __init__(self):
        self.__lab_name: str = ""
        self.__assignments: List[Assignment] = []

    def __get_lab_num(self) -> str:
        """获取实验编号
        """
        return self.__lab_name[3:5]

    def process_package(self, package: zipfile.ZipFile, stu_info: StudentInfo):
        """导入并处理作业包
        """
        check = AssignmentChecker()
        print("[Info]Processing package..")
        self.__lab_name = package.filename[:-4]  # 实验名称(根目录名)
        # 遍历所有学生作业
        for file in package.filelist:
            stu_num = file.filename[:13]  # 读取学生学号
            try:
                student: Student = Student(stu_num, stu_info[stu_num])  # 查询学生姓名缩写
            except KeyError:
                # 学生信息不存在
                print(
                    f"[Warn]Student shortname with number {stu_num} is not found in student list, using full "
                    "name instead")
                student = Student(stu_num, file.filename[14:-4])

            print("[Info]Processing Assignment:", student)

            # 处理单个学生作业
            assignment = Assignment(self.__get_lab_num(), student, self.__lab_name, check)

            with package.open(file, mode='r') as package_io:
                with zipfile.ZipFile(package_io, 'r') as assignment_zip:
                    assignment.process_assignment(assignment_zip)

            self.__assignments.append(assignment)

    def check(self):
        """作业相似度检查
        """
        print("[Info]Assignments check..")
        similar_result: List[Tuple[int, List[int]]] = []  # 结果集
        # 遍历两两检查
        for index_l in range(len(self.__assignments) - 1):
            left = self.__assignments[index_l]
            l_src = left.source
            for index_r in range(index_l + 1, len(self.__assignments)):
                flag: int = 0b000  # 相似位标记
                right = self.__assignments[index_r]
                r_src = right.source
                src_analyzer = SourceAnalyzer(l_src, r_src)
                if src_analyzer.similar_size():
                    print("[Warn]Similar upload file size")
                    flag |= 0b001  # 记录

                if src_analyzer.similar_structure():
                    print("[Warn]Similar file structure")
                    flag |= 0b010

                # 实验报告文件相似度分析
                # 去除报告中学生姓名学号
                l_report_name = left.report.original_filename \
                    .lower() \
                    .replace(left.student.name.lower(), '') \
                    .replace(left.student.num.lower(), '')
                r_report_name = right.report.original_filename \
                    .lower() \
                    .replace(right.student.num.lower(), '') \
                    .replace(right.student.name.lower(), '')
                s = difflib.SequenceMatcher(None, l_report_name, r_report_name)
                report_ratio = s.ratio()
                if report_ratio > 0.8:
                    print(f"[Warn]Similar report filename")
                    flag |= 0b100

                # 存在雷同，则根据不同雷同情况记录
                if flag > 0:
                    for f, indices in similar_result:
                        if f == flag:
                            find_l, find_r = False, False
                            for it in indices:
                                if it == index_l:
                                    find_l = True
                                elif it == index_r:
                                    find_r = True
                            if find_l and not find_r:
                                indices.append(index_r)
                                break
                            elif find_l and find_r:
                                break
                    else:
                        similar_result.append((flag, [index_l, index_r]))

        # 导出相似度分析报告
        if len(similar_result) > 0:
            print("[Info]Exporting similar report..")
            self.__export_check_report(similar_result)
            print("[Info]Export finished.")

    def __export_check_report(self, result: List[Tuple[int, List[int]]]):
        with open("./Similar-Works-Report.csv", mode="w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            max_count = 0  # 确定表头大小
            rows: List[str] = []
            count = 1
            for f, it in result:
                if len(it) > max_count:
                    max_count = len(it)
                aspects = convert_flag(f)
                rows += [[f"Group {count}", aspects] + [
                    f"{self.__assignments[i].student}" for i in it]]
                count += 1
            header = ["", "Similar Aspects"] + [f"Student {i}" for i in range(1, max_count + 1)]  # 创建表头
            writer.writerow(header)
            writer.writerows(rows)


def convert_flag(flag: int) -> str:
    """转换flag成可读形式"""
    kv_map = ["similar size, ", "similar structure, ", "similar report name"]
    result = ""
    index = 0
    while flag > 0:
        if flag % 2 == 1:
            result += kv_map[index]
        index += 1
        flag >>= 1
    return result


def remove_single_src_dir(p: Path):
    """移除单独出现的src目录"""
    exist_src = False
    count = 0
    for sub in p.iterdir():
        count += 1
        if sub.is_dir():
            if sub.name == "src":
                exist_src = True
            remove_single_src_dir(sub)
    if exist_src and count == 1:
        import shutil
        src = (p / "src")
        for sub in src.iterdir():
            shutil.move(sub, p)
        src.rmdir()


def remove_single_begin_dir(p: Path, key: str):
    """嵌套去除开头与关键词匹配的单文件夹"""
    flag = False
    for sub in p.iterdir():
        if sub.is_dir() and sub.name == key:
            flag = True
        else:
            return
    if flag:
        import shutil
        si = (p / key)
        st = (p / (key + "tmp"))
        shutil.move(si, st)
        for sub in st.iterdir():
            shutil.move(sub, p)
        st.rmdir()
        remove_single_begin_dir(p, key)


def remove_duplicate_dir(p: Path):
    """去除连续相同的单文件夹"""
    pass
