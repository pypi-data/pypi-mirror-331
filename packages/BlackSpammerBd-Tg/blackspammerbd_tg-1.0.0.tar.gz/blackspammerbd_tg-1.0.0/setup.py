from setuptools import setup, find_packages

setup(
    name="BlackSpammerBd_Tg",
    version="1.0.0",
    author="BLACK SPAMMER BD",
    author_email="shawponsp6@gmail.com",
    description="BlackSpammerBd_Tg - A powerful Telegram bot automation tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BLACKSPAMMERBD/BlackSpammerBd_Tg",
    packages=find_packages(),
    install_requires=[
        "termcolor",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
