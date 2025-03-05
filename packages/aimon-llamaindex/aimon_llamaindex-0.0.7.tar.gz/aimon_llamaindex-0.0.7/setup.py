from setuptools import setup, find_packages

# Read the content of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='aimon-llamaindex',
    python_requires='>3.8.0',
    packages=find_packages(),
    version="0.0.7",
    install_requires=[
        "aimon==0.9.2",
        "llama-index-core==0.12.15",
    ],
    author='AIMon',
    author_email='info@aimon.ai',
    description='The AIMon SDK for LlamaIndex related functionalities.',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
