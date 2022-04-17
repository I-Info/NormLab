from pathlib import Path

from student import StudentInfoDict

package_filename = "Lab03-JUnit for Unit Test.zip"
base_dir = package_filename[:-4]
lab_num = package_filename[3:4]
student_list_file = "student-list.csv"
student_infos = StudentInfoDict(student_list_file)
suffix_blacklist = [".class", ".gitignore", ".DS_Store"]
dirname_blacklist = [".git", ".idea", "target"]


def test_base_dir():
    """测试根目录是否存在且符合规范"""
    assert Path(base_dir).exists()


def test_report_csv():
    """测试生成的相似度报告"""
    path = Path(base_dir) / "Similar-Report.csv"
    assert path.exists()
    import csv
    with open(path, "r") as csvfile:
        reader = csv.reader(csvfile)
        header = reader.__next__()
        assert header[1] == "Similar Aspects"
        assert header[2] == "Student 1"
        count = 1
        for it in reader:
            assert it[0] == f"Group {count}"
            count += 1
            assert "similar" in it[1]
            check_file_name(it[2])


def test_lab_reports():
    """测试规范化后的实验报告文件名"""
    path = Path(base_dir)
    for file in path.iterdir():
        if file.is_file():
            if file.name[-5] == ".docx":
                assert file.name[:1] == lab_num
                check_file_name(file.name[3:-7])
            elif file.name[-4] == ".doc":
                assert file.name[:1] == lab_num
                check_file_name(file.name[3:-6])


def test_src_dirs():
    """测试源码目录"""
    path = Path(base_dir)
    for sub in path.iterdir():
        if sub.is_dir():
            # 测试目录名
            assert sub.name[:1] == lab_num
            check_file_name(sub.name[3:])
            check_dir(sub)


def check_file_name(f_name: str):
    """检查命名规范"""
    part = f_name.split("-")
    assert len(part) == 2
    assert student_infos[part[0]] == part[1]


def check_dir(p: Path):
    """检查上传文件处理情况"""
    exist_src = False
    count = 0
    for sub in p.iterdir():
        count += 1
        if sub.is_file():
            for ban in suffix_blacklist:
                assert sub.name[-len(ban):] != ban
        elif sub.is_dir():
            if sub.name == "src":
                exist_src = True
            check_dir(sub)
    if exist_src:
        # 测试是否存在单src的目录
        assert count != 1
    else:
        # 测试是否存在空目录
        assert count != 0
