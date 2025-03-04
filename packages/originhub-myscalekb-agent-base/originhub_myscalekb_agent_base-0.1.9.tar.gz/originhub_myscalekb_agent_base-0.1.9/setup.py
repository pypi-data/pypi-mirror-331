from setuptools import setup, find_packages

setup(
    name="originhub-myscalekb-agent-base",
    version="0.1.9",
    author="jiachengs",
    author_email="jiachengs@myscale.com",
    description="Base classes for MyScaleKB Agent APP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/myscale/myscalekb-agent-base",
    packages=find_packages(include=["myscalekb_agent_base", "myscalekb_agent_base.*"]),
    package_data={},
    python_requires=">=3.12",
    install_requires=[
        # app required
        "pydantic~=2.8.2",
        # langchain family
        "langchain==0.3.19",
        "langchain-openai==0.3.7",
        "langchain-community==0.3.18",
        "langgraph==0.2.35",
        # others
        "nanoid~=2.0.0",
        "clickhouse-connect~=0.7.18",
        "json5~=0.9.25",
        "json_repair~=0.30.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
)
