from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name = 'willphanpy',
    version = '0.0.1',
    packages=find_packages(),
    install_requires=[
        "numpy",
        "torch",
        "matplotlib",
        "pandas"
    ],
    # entry_points={
    #     "console_scripts": [
    #         "will = will:Wpy",
    #     ]
    # },
    long_description=description,
    long_description_content_type = "text/markdown"
)