from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="gguf-converter",
    version="0.3.1",
    description="Advanced Hugging Face to GGUF Converter with Quantization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kunaalgadhalay/gguf-converter",
    author="Your Name",
    author_email="kunaalgadhalay93@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="gguf, quantization, transformers, llm",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9, <4",
    install_requires=[
        "numpy>=1.22",
        "torch>=2.0.1",
        "transformers>=4.31.0",
        "accelerate>=0.21.0",
        "safetensors>=0.3.3",
        "tqdm>=4.66.1",
        "psutil>=5.9.5",
    ],
    extras_require={
        "gpu": ["cudnn>=8.9.5", "nvidia-cublas-cu12>=12.1.3.1"],
        "quantization": ["bitsandbytes>=0.41.1", "scipy>=1.11.1"],
        "testing": ["pytest>=7.4.0", "pytest-benchmark>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "gguf-convert=gguf_converter.cli:main",
        ],
    },
    package_data={
        "gguf_converter": ["architecture_maps/*.py", "utils/*.py"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourorg/gguf-converter/issues",
        "Source": "https://github.com/yourorg/gguf-converter",
    },
)