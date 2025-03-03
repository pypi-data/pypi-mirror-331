from setuptools import setup, find_packages

setup(
    name="cifer",
    version="1.0.0",
    author="Cifer.ai",
    author_email="support@cifer.ai",
    description="Federated Learning Client & Server API for AI Model Training",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cifer-ai/cifer",
    packages=find_packages(),
    install_requires=[
        "requests",
        "tensorflow>=2.0",
        "numpy",
        "flask",  # สำหรับ API Server
        "uvicorn",  # สำหรับ API Server
        "pydantic",  # ตรวจสอบข้อมูล API
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
