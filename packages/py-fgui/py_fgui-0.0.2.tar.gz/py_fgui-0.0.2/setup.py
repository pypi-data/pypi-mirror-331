import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py_fgui",
    version="0.0.2",
    author="MisakaCirno",
    author_email="misakacirno@qq.com",
    description="A python package for parsing FGUI project files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MisakaCirno/py_fgui",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
