from setuptools import setup, find_packages

setup(
    name="portfolio",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'gunicorn>=20.1.0',
        'python-dotenv>=0.19.0',
        'pydantic>=1.8.0,<2.0.0',
        'langchain-groq>=0.1.0',
        'langchain-core>=0.2.2',
    ],
)
