from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="arpit",
    version="2.0.1",
    author="Arpit Sengar (arpy8)",
    author_email="arpitsengar99@gmail.com",
    description="We're so fucking back.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arpy8/arpit",
    packages=find_packages(),
    install_requires=["pygame", "moviepy", "termcolor", "pyautogui", "opencv-python", "keyboard", "setuptools"],
    entry_points={
        "console_scripts": [
            "arpit=arpit.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={'arpit': ['assets/*']},
    include_package_data=True,
    license="MIT"
)