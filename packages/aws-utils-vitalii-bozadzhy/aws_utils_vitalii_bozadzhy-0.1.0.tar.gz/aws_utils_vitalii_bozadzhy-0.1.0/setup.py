import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws_utils_vitalii_bozadzhy",
    version="0.1.0",
    author="Vitalii Bozadzhy",
    author_email="VitaliiBozadzhy@icloud.com",
    description="Utility package for AWS operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VitaliiBozadzhy88/aws_utils",
    py_modules=["aws_utils"],  
    install_requires=[
        "boto3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
