from setuptools import setup, find_packages

setup(
    name="auto_privacy_audit",
    version="0.1.2",
    author="yangtianhan",
    author_email="1257330051@qq.com",
    description="自动隐私合规检测器：基于 AST 的静态代码分析工具，帮助检测代码中的敏感信息泄露风险",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Yantha6/AutoPrivacyAudit",
    packages=find_packages(),
    install_requires=[],  # 如有需要可添加第三方依赖
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
