import os
import zipfile
import rarfile
from typing import Union


def extract_file(archive: Union[rarfile.RarFile, zipfile.ZipFile], name: any, output_path: os.PathLike[str],
                 output_filename: str):
    """从压缩包中提取文件，并自动创建目录
    """
    os.makedirs(output_path, exist_ok=True)  # 创建目录
    with archive.open(name, 'r') as io_input:
        with open(f"{output_path}/{output_filename}", 'wb') as io_output:
            io_output.write(io_input.read())


def get_output_path(path: str, key: str) -> str:
    """获取去除重复关键词后的路径
    用于实现递归去除重复路径的功能
    """
    index = path.find(f"{key}/")
    if index == -1:
        return path
    else:
        return get_output_path(path[len(key) + 1:], key)


def separate_path_filename(path: str) -> (str, str):
    """分离路径和文件名 返回(路径, 文件名)
    """
    index = path.find("/")
    current = index
    while not index == -1:
        current = index
        index = path.find("/", current + 1)
    return path[:current], path[current + 1:]


def decode_file_name(name: str) -> str:
    """重新编码解码zip中文件名，去除中文乱码
    """
    try:
        e = name.encode("cp437")
        e = e.decode("utf-8")
        return e
    except UnicodeDecodeError:
        try:
            e = name.encode("cp437")
            e = e.decode("gbk")
            return e
        except UnicodeDecodeError:
            return name
