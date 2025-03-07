from setuptools import setup, find_packages

setup(
    name="fiaduzai",  # Replace with your package name
    version="0.2.2",  # Start with a version
    packages=find_packages(),  # Automatically find all packages in the directory
    install_requires=[
        "google-generativeai>=0.3.0",
        "IPython>=8.0.0"
    ],
    author="Fiaduz Zaman",  # Replace with your name
    author_email="fiaduzzaman2014@gmail.com",  # Replace with your email
    description="A library to generate content using Google's Gemini model.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/fiaduz/fiaduzai",  # Replace with your GitHub repository URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # Specify the required Python version
)
