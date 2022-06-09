class Report:
    """实验报告类
    """

    def __init__(self, filename: str = "", file_size: int = -1):
        self.original_filename = filename
        self.file_size = file_size
        self.count = 0

    def cmp_update(self, filename: str, file_size: int) -> bool:
        """比较与更新
        如果新的文件大于当前文件大小，则替换。

        :return: 如果修改了则返回Ture
        """
        if file_size > self.file_size:
            self.file_size = file_size
            self.original_filename = filename
        self.count += 1
        if self.count > 1:
            print("[Warn]Multiple lab report file detected, reserve bigger one.")
            return True
        return False
