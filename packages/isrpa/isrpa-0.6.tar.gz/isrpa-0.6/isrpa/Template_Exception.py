class 登录失败(Exception):
    """异常：登录失败"""

    def __init__(self, message="登录失败，请检查登录步骤"):
        self.message = message
        super().__init__(self.message)


class 文件不存在(Exception):
    """异常：文件不存在"""

    def __init__(self, message="文件不存在，请检查文件路径"):
        self.message = message
        super().__init__(self.message)


class 等待超时(Exception):
    """异常：等待超时"""

    def __init__(self, message="等待超时"):
        self.message = message
        super().__init__(self.message)


class 无效参数(Exception):
    """异常：无效参数"""

    def __init__(self, message="输入参数无效"):
        self.message = message
        super().__init__(self.message)
