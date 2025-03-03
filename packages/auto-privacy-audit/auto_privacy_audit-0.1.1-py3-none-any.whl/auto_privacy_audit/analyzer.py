# auto_privacy_audit/analyzer.py
import ast
import re

class PrivacyAuditAnalyzer(ast.NodeVisitor):
    """
    自动隐私合规检测器 - AST 静态代码分析器
    扩展检测：
      - 函数调用（print、logging 等）中的字符串（包括 f-string 和字符串拼接）
      - 变量赋值、字典和列表中的字符串
      - 使用关键词检测和正则模式检测敏感数据
    """
    # 默认敏感关键词
    DEFAULT_SENSITIVE_KEYWORDS = ['email', 'phone', 'password', 'ssn', 'address']
    
    # 默认敏感数据正则模式
    DEFAULT_SENSITIVE_PATTERNS = {
        'email': r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        'phone': r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(\d{1,4}\)|\d{1,4})[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b",
        'credit_card': r"\b(?:\d[ -]*?){13,16}\b",
        'ssn': r"\b\d{3}-\d{2}-\d{4}\b",
    }
    
    def __init__(self, source_code, extra_keywords=None, extra_patterns=None):
        """
        :param source_code: 要检测的源代码字符串
        :param extra_keywords: 用户自定义的额外敏感关键词列表
        :param extra_patterns: 用户自定义的额外正则模式（字典：模式名称->模式字符串）
        """
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        self.issues = []
        # 敏感关键词：默认 + 用户额外关键词
        self.sensitive_keywords = self.DEFAULT_SENSITIVE_KEYWORDS.copy()
        if extra_keywords:
            self.sensitive_keywords.extend(extra_keywords)
        # 敏感数据正则模式：默认 + 用户额外模式
        self.sensitive_patterns = self.DEFAULT_SENSITIVE_PATTERNS.copy()
        if extra_patterns:
            self.sensitive_patterns.update(extra_patterns)
    
    def analyze(self):
        """启动 AST 遍历，返回检测到的问题列表"""
        self.visit(self.tree)
        return self.issues

    def visit_Call(self, node):
        """
        检测函数调用中（如 print 和 logging 系列函数）的字符串参数，
        包括 f-string 和字符串拼接。
        """
        func_name = self.get_func_name(node)
        if func_name in ['print', 'logging.info', 'logging.debug', 'logging.warning', 'logging.error']:
            for arg in node.args:
                text = self._extract_string_value(arg)
                if text:
                    self._check_sensitive_string(node.lineno, text)
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """
        检测变量赋值：
          - 如果变量名中包含敏感关键词，并且赋值为字符串常量或拼接后的字符串，
          则记录风险。
          - 同时对赋值的字符串内容进行正则检测。
        """
        text = self._extract_string_value(node.value)
        if text:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id.lower()
                    for keyword in self.sensitive_keywords:
                        if keyword in var_name:
                            self._add_issue(
                                node.lineno,
                                keyword,
                                f"变量 '{target.id}' 赋值中包含敏感关键词 '{keyword}'"
                            )
            # 检查赋值文本中的敏感数据
            self._check_sensitive_string(node.lineno, text)
        self.generic_visit(node)
    
    def visit_Dict(self, node):
        """
        检测字典中键和值，如果为字符串则进行检测。
        """
        for key, value in zip(node.keys, node.values):
            key_text = self._extract_string_value(key)
            if key_text:
                self._check_sensitive_string(node.lineno, key_text)
            value_text = self._extract_string_value(value)
            if value_text:
                self._check_sensitive_string(node.lineno, value_text)
        self.generic_visit(node)
    
    def visit_List(self, node):
        """
        检测列表中所有字符串元素。
        """
        for elem in node.elts:
            elem_text = self._extract_string_value(elem)
            if elem_text:
                self._check_sensitive_string(node.lineno, elem_text)
        self.generic_visit(node)
    
    def _extract_string_value(self, node):
        """
        尝试从 AST 节点中提取完整的字符串内容。
        支持：
          - 常量字符串
          - f-string（JoinedStr）：拼接所有常量部分
          - 字符串拼接（BinOp with Add）：递归提取左右侧的字符串
        """
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        elif isinstance(node, ast.JoinedStr):
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    parts.append(value.value)
            return ''.join(parts) if parts else None
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._extract_string_value(node.left)
            right = self._extract_string_value(node.right)
            if left is not None and right is not None:
                return left + right
        return None

    def _check_sensitive_string(self, lineno, text):
        """
        检查给定文本是否包含敏感关键词或符合敏感数据的正则模式，
        如果匹配则添加风险记录。
        """
        # 关键词检测（忽略大小写）
        for keyword in self.sensitive_keywords:
            if re.search(keyword, text, re.IGNORECASE):
                self._add_issue(
                    lineno,
                    keyword,
                    f"检测到敏感关键词 '{keyword}' 在文本: {text}"
                )
        # 正则模式检测（区分大小写）
        for pattern_name, pattern in self.sensitive_patterns.items():
            if re.search(pattern, text):
                self._add_issue(
                    lineno,
                    pattern_name,
                    f"检测到敏感模式 '{pattern_name}' 在文本: {text}"
                )
    
    def _add_issue(self, lineno, identifier, message):
        """
        添加检测问题，避免重复记录相同问题
        """
        issue = {'lineno': lineno, 'identifier': identifier, 'message': message}
        if issue not in self.issues:
            self.issues.append(issue)
    
    def get_func_name(self, node):
        """
        获取函数调用名称，支持直接调用和通过模块调用的形式
        """
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            value = node.func.value
            if isinstance(value, ast.Name):
                return f"{value.id}.{node.func.attr}"
        return ""
