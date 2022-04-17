import csv


class Student:
    """学生类
    """

    def __init__(self, num: str = "", name: str = ""):
        self.num = num
        self.name = name

    def __str__(self) -> str:
        return f"{self.num}-{self.name}"


class StudentInfo:
    """学生信息
    """

    def __init__(self, input_path: str):
        # 从CSV文件中读取学生信息
        self.__data: dict = {}
        with open(input_path, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            reader.__next__()  # 去除表头
            for row in reader:
                self.__data[row[0]] = row[2]

    def __getitem__(self, item: str) -> str:
        """通过学号查询姓名简称，找不到则抛出异常
        """
        return self.__data[item]
