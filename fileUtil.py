import os
import zipfile
from typing import Union


# 创建目录
def mkdir(path: str):
    if not os.path.exists(path):
        os.mkdir(path)


def zip_extract_file(archive: zipfile.PyZipFile, name: Union[str, zipfile.ZipInfo], output_path: str,
                     output_filename: str):
    """
    从zip中提取文件，并自动创建目录
    """
    # 创建目录
    os.makedirs(output_path, exist_ok=True)
    with archive.open(name, 'r') as io_input:
        with open(f"{output_path}/{output_filename}", 'wb') as io_output:
            io_output.write(io_input.read())


# 获取去除重复关键词后的路径
def get_output_path(path: str, key: str) -> str:
    index = path.find(f"{key}/")
    if index == -1:
        return path
    else:
        return get_output_path(path[len(key) + 1:], key)


# 分离路径和文件名 返回(路径, 文件名)
def separate_path_filename(path: str) -> (str, str):
    index = path.find("/")
    current = index
    while not index == -1:
        current = index
        index = path.find("/", current + 1)
    return path[:current + 1], path[current + 1:]
