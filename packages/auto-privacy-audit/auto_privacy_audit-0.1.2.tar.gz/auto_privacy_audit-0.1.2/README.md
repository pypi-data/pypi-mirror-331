# AutoPrivacyAudit

**自动隐私合规检测器**  
AutoPrivacyAudit 是一个基于 Python 的静态代码分析工具，旨在帮助开发者检测代码中潜在的敏感信息泄露风险。利用 AST（抽象语法树）解析技术，本项目能够自动识别日志记录、打印输出等场景中涉及敏感数据（如 email、password、phone 等）的使用情况，从而提高代码安全性和隐私合规性。

## 特性
- **静态代码分析**  
  自动解析代码并检测敏感关键词，识别潜在的隐私泄露风险。
- **日志输出检测**  
  检查 `print` 和日志函数（如 `logging.info`、`logging.error` 等）中是否直接输出了敏感信息。
- **详细审计报告**  
  为每个检测到的问题提供所在文件、代码行号和建议的修复方案，方便开发者快速定位和修改问题。
- **CI/CD 集成**  
  提供命令行接口，便于将检测工具集成到持续集成、代码评审及部署流程中。
- **可扩展的规则系统**  
  支持用户自定义敏感数据的检测规则，满足不同项目和业务场景的需求。

## 安装
你可以通过 pip 直接安装 AutoPrivacyAudit：
```bash
pip install auto_privacy_audit
```

## 使用示例
下面是一个简单的示例，展示如何使用 AutoPrivacyAudit 检测代码中的敏感信息：
```python
from auto_privacy_audit import PrivacyAuditAnalyzer

code = '''
import logging

def test():
    print("User email is test@example.com")
    logging.info("User password: 123456")
'''

analyzer = PrivacyAuditAnalyzer(code)
issues = analyzer.analyze()
for issue in issues:
    print(f"Line {issue['lineno']}: {issue['message']}")
```

运行后，你将看到输出中标明了敏感信息所在的代码行及具体提示信息。
```bash
Line 5: 检测到敏感信息 'email' （敏感关键词 & 敏感模式） 在文本: User email is test@example.com
Line 6: 检测到敏感信息 'password' （敏感关键词） 在文本: User password: 123456
```

## 联系方式
- Email: [1257330051@qq.com]
- GitHub: [@Yantha6]