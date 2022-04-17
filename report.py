class Report:
    """实验报告类
    """

    def __init__(self, filename: str = "", file_size: int = -1):
        self.original_filename = filename
        self.file_size = file_size

    def cmp_update(self, filename: str, file_size: int) -> bool:
        """比较与更新
        如果新的文件大于当前文件大小，则替换。

        :return: 如果修改了则返回Ture
        """
        if self.file_size != -1:
            print("[Warn]Multiple lab report file detected, reserve bigger one.")
        if file_size > self.file_size:
            self.file_size = file_size
            self.original_filename = filename
            return True
        return False
