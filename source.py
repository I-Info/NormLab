from typing import List, Tuple


class Source:
    """源代码类"""

    def __init__(self):
        self.size = 0  # 源码大小
        self.files: List[str] = []  # 文件列表

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, item: int) -> str:
        return self.files[item]

    def __iter__(self):
        return self.files.__iter__()

    def append(self, file: str, size: int):
        self.files.append(file)
        self.size += size


class SourceAnalyzer:
    """源码分析类
    """

    def __init__(self, left: Source, right: Source, size_ratio=0.10, count_ratio=0.6, similar_ratio=0.8):
        # 左手侧为较大的数组
        if len(left) > len(right):
            self.__left = left
            self.__right = right
        else:
            self.__left = right
            self.__right = left
        self.__size_ratio = size_ratio  # 相似大小比阈值
        self.__count_ratio = count_ratio  # 相似数量比阈值
        self.__similar_ratio = similar_ratio  # 相似度阈值
        self.__similar_analysis: List[(int, int, int)] = []  # 分析结果

    def similar_size(self) -> bool:
        """大小相似"""
        if self.__left.size != 0:
            return (abs(self.__left.size - self.__right.size) / self.__left.size) < self.__size_ratio
        else:
            return False

    def similar_structure(self) -> bool:
        """检查文件结构是否相似(包含文件名)"""

        import difflib
        if self.__left.size == 0 or self.__right.size == 0:
            return False

        similar_count = 0
        result = []
        for i in range(len(self.__left)):
            max_ratio = 0
            max_r_index: int = 0
            for j in range(len(self.__right)):
                s = difflib.SequenceMatcher(None, self.__left[i], self.__right[j])
                ratio = s.ratio()
                if ratio > max_ratio:
                    max_ratio = ratio
                    max_r_index = j
            if max_ratio > self.__similar_ratio:
                result.append((i, max_r_index, max_ratio))
                similar_count += 1
        self.__similar_analysis = result  # 保存比较结果

        return similar_count / len(self.__left) > self.__count_ratio

    def get_analysis(self) -> List[Tuple[str, str, int]]:
        """返回相似度分析详情信息"""
        return [(self.__left[x], self.__right[y], z) for x, y, z in self.__similar_analysis]
