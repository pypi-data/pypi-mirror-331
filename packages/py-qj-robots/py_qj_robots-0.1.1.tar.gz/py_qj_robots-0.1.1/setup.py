from setuptools import setup, find_packages

setup(
    name="py-qj-robots",
    version="0.1.1",
    author="QJ ROBOTS",
    author_email="github@qj-robots.com",
    description="千诀机器人 Python SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/py-qj-robots",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.1",
        "numpy>=1.19.0",
        "opencv-python>=4.5.0"
    ],
)