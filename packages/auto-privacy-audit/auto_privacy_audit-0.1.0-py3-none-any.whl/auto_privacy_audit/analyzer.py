import ast
import re

class PrivacyAuditAnalyzer:
    """
    自动隐私合规检测器 - 基于 AST 的静态代码分析器
    检测代码中是否存在潜在的敏感信息泄露风险
    """
    # 定义需要检测的敏感关键词
    SENSITIVE_KEYWORDS = ['email', 'phone', 'password', 'ssn', 'address']

    def __init__(self, source_code):
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        self.issues = []

    def analyze(self):
        """
        分析源代码中的敏感信息使用情况，返回检测到的问题列表。
        每个问题包含代码行号、敏感关键词和提示信息。
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                func_name = self.get_func_name(node)
                # 检查函数调用是否为打印或日志记录相关函数
                if func_name in ['print', 'logging.info', 'logging.debug', 'logging.warning', 'logging.error']:
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            for keyword in self.SENSITIVE_KEYWORDS:
                                if re.search(keyword, arg.value, re.IGNORECASE):
                                    self.issues.append({
                                        'lineno': node.lineno,
                                        'keyword': keyword,
                                        'message': f"在输出中检测到敏感关键词 '{keyword}'"
                                    })
        return self.issues

    def get_func_name(self, node):
        """
        获取函数调用的名称，支持直接调用和通过模块调用的情况
        """
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            value = node.func.value
            if isinstance(value, ast.Name):
                return f"{value.id}.{node.func.attr}"
        return ""
