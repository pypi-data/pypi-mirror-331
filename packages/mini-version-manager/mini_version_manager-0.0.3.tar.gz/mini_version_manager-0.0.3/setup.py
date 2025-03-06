from setuptools import setup, find_packages

setup(
    name="mini_version_manager",
    version="0.0.3",
    packages=find_packages(),
    install_requires=[
        # 列出你的项目依赖
        "shutil",
        "os",
        "re",
        "logging",
        "datetime"
    ],
    entry_points={
        'console_scripts': [
            'mini_version_manager=mini_version_manager.mini_version_manager:version_manager',
        ],
    },
    author="bjk",
    author_email="228558063@qq.com",
    description="A simple version management tool",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bjkjy/UART-analysis-scheme-based-on-RT-Thread-operating-system.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)