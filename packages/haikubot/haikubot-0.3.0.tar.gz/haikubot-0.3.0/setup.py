from setuptools import setup, find_packages
from haikubot.version import __version__

setup(
    name="haikubot",
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "requests",
        "dashscope",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "haikubot=haikubot.cli:main",
        ],
    },
    author="lgy112112",
    author_email="lgy112112@gmail.com",
    description="从Bilibili视频生成俳句的命令行工具",
    keywords="bilibili, haiku, audio, transcription, llm, asr",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lgy112112/haikubot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 