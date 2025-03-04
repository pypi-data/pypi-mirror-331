from setuptools import setup, find_packages

with open("README.MD", "r", encoding="utf-8") as fh: 
    long_description = fh.read()

setup(
    name='ollamawebui',
    version='0.1.0',
    install_requires=[
        'Flask',
        'requests',
        'beautifulsoup4',
        'html5lib',
        'lxml',
    ],
    entry_points={
        'console_scripts': [
            'ollamawebui = ollamawebui.app:run_app', 
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/pythonxueba",
    author="PythonXueba",
    author_email="python@xueba.com",
    description="A web UI for Ollama",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)