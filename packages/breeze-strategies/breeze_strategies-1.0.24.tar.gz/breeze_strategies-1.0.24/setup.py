import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="breeze_strategies",
    version="1.0.24",
    author="ICICI Direct Breeze",
    author_email="breezeapi@icicisecurities.com",
    description="ICICIDIRECT's breezeconnect strategies in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['breeze_connect','nest_asyncio','IPython'],
    url="https://github.com/Idirect-Tech/python_strategies/tree/master",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
