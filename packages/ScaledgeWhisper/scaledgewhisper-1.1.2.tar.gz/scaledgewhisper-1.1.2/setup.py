import os
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

def get_long_description():
    readme_path = os.path.join(base_dir, "README.md")
    with open(readme_path, encoding="utf-8") as readme_file:
        return readme_file.read()


def get_project_version():
    version_path = os.path.join(base_dir, "ScaledgeWhisper", "version.py")
    version = {}
    with open(version_path, encoding="utf-8") as fp:
        exec(fp.read(), version)
    return version["__version__"]


def get_requirements(path):
    with open(path, encoding="utf-8") as requirements:
        return [requirement.strip() for requirement in requirements]


install_requires = get_requirements(os.path.join(base_dir, "requirements.txt"))
conversion_requires = get_requirements(
    os.path.join(base_dir, "requirements-conversion.txt")
)

setup(
    name="ScaledgeWhisper",
    version=get_project_version(),
    license="MIT",
    description="Faster Whisper transcription with CTranslate2 with Live Capabilities for Edge Devices",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="ScaledgeTechnology",
    author_email="Scaledge.ml@gmail.com",
    entry_points={
        'console_scripts': [
            'Scaledgewhisper = ScaledgeWhisper.cli:main',  
        ],
    },         
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],  
    keywords="openai whisper faster-whisper speech ctranslate2 inference quantization transformer",
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require={
        "conversion": conversion_requires,
        "dev": [
            "black==23.*",
            "flake8==6.*",
            "isort==5.*",
            "pytest==7.*",
        ],
    },
    packages=find_packages(),
    package_data={
        "ScaledgeWhisper": ["assets/*.onnx", "test/data/*.mp3", "test/data/*.wav", "test/data/*.flac"]
    },
    include_package_data=True,
)