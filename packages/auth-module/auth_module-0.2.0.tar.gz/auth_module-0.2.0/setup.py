from setuptools import setup, find_packages

setup(
    name="auth_module",
    version="0.2.0",
    author="Wesley",
    author_email="drunksoul2023@gmail.com",
    description="A reusable authentication module for Python applications",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/drunksoul2021/auth_module",
    packages=find_packages(),
    install_requires=[
        "pyjwt==2.8.0",
        "python-dotenv==1.0.0",
        "argon2-cffi==23.1.0",
        # "pytest"  # 仅用于开发，可不添加到正式依赖
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)