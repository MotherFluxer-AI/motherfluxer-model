from setuptools import setup, find_packages

setup(
    name="motherfluxer-model",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "websockets==12.0",
        "transformers==4.37.2",
        "torch==2.2.0",
        "pydantic==2.6.1",
        "pydantic-settings==2.1.0",
        "python-dotenv==1.0.1",
        "accelerate==0.31.0",
        "flash_attn==2.5.8",
        "safetensors>=0.5.2",
    ],
) 