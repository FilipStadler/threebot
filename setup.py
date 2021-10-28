import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="threebot",
    version="0.2",
    author="Justin Stanley",
    author_email="jtst@iastate.edu",
    description="A modular mumble bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codeandkey/threebot",
    project_urls={
        "Bug Tracker": "https://github.com/codeandkey/threebot/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "threebot"},
    packages=setuptools.find_packages(where="threebot"),
    python_requires=">=3.6",
    install_requires=[
        'pyaudio',
        'pymumble'
    ],
    scripts=['bin/threebot']
)