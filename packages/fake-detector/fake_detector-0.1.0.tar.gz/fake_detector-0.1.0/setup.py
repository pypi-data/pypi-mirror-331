from setuptools import setup, find_packages

setup(
    name="fake_detector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "transformers",
        "torch",
        "flask",
        "flask-cors",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "fake-detector-api = fake_detector.api:app.run"
        ]
    },
    author="Nexora Innovexa LTD",
    description="A simple Fake News and Fake Product detection API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fake_detector",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7, <3.13",
)
