from setuptools import setup, find_packages
import os

# Read README.md with error handling
long_description = ""
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    try:
        with open(readme_path, "r", encoding="utf-8") as fh:
            long_description = fh.read()
    except Exception:
        long_description = "The open, local alternative to ManusAI"
else:
    long_description = "The open, local alternative to ManusAI"

setup(
    name="agenticSeek",
    version="0.1.0",
    author="Fosowl",
    author_email="mlg.fcu@gmail.com",
    description="The open, local alternative to ManusAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fosowl/agenticSeek",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Web frameworks
        "fastapi>=0.115.12",
        "flask>=3.1.0",
        "uvicorn>=0.34.0",
        "celery>=5.5.1",
        # HTTP/Networking
        "requests>=2.31.0",
        "httpx>=0.27,<0.29",
        "anyio>=3.5.0,<5",
        # ML/AI frameworks
        "torch>=2.4.1",
        "transformers>=4.46.3",
        "numpy>=1.24.4",
        "scipy>=1.9.3",
        "adaptive-classifier>=0.0.10",
        "ollama>=0.4.7",
        "openai",
        # NLP libraries
        "sacremoses>=0.0.53",
        "text2emotion>=0.0.5",
        "langid>=1.1.6",
        "sentencepiece>=0.2.0",
        # Audio processing
        "librosa>=0.10.2.post1",
        "soundfile>=0.13.1",
        "playsound>=1.3.0",
        "kokoro>=0.7.12",
        # Web scraping
        "selenium>=4.29.0",
        "selenium_stealth>=1.0.6",
        "undetected-chromedriver>=3.5.5",
        "chromedriver-autoinstaller>=0.6.4",
        "markdownify>=1.1.0",
        "fake_useragent>=2.1.0",
        # Data validation and serialization
        "pydantic>=2.10.6",
        "pydantic_core>=2.27.2",
        "protobuf>=3.20.3",
        # Utilities
        "aiofiles>=24.1.0",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
        "termcolor>=2.5.0",
        "ipython>=8.34.0",
        "distro>=1.7.0,<2",
        "jiter>=0.4.0,<1",
        "sniffio",
        "tqdm>4",
    ],
    extras_require={
        "chinese": [
            "ordered_set",
            "pypinyin",
            "cn2an",
            "jieba",
        ],
    },
    entry_points={
        "console_scripts": [
            "agenticseek=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
)
