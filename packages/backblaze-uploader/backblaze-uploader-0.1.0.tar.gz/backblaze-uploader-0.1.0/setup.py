from setuptools import setup, find_packages

setup(
    name="backblaze-uploader",
    version="0.1.0",
    author="Sizning ismingiz",
    author_email="email@example.com",
    description="Backblaze B2 bucket'ga fayl yuklash uchun Python library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/backblaze-uploader",  # GitHub URL
    packages=find_packages(),
    install_requires=[
        "b2sdk>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
