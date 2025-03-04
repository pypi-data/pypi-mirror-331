from setuptools import setup

with open('README.MD', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ollamawebui',
    version='2.0.0',
    description='OllamaWebUI-A Simple Flask WebUI, You Can Chat With Ollama On Web|Flask聊天界面，可以自定义设置Ollama Api（python学霸公众号）',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Python学霸',
    author_email='python@xueba.com',
    py_modules=['ollamawebui'],
    install_requires=[
'Flask',
'requests',
'beautifulsoup4',
],
    entry_points={
        'console_scripts': [
            'ollamawebui=ollamawebui:run_app',
        ]
    }
)