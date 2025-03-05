import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="auto_mlflow",
    version="1.4",
    author="Ravin Kumar",
    author_email="mr.ravin_kumar@hotmail.com",
    description="Auto MLFlow is an open-source automated MLOps library for MLFlow in Python. It simplifies the logging and tracking of machine learning experiments by providing an intuitive and easy-to-use interface for interacting with MLFlow servers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/mr-ravin/auto_mlflow",
    keywords=['MLFlow', 'MLOps', 'Deep Learning', 'Automation'],
    install_requires=[  
        'mlflow>=2.9.2,<=2.20.3',
        'opencv-contrib-python>=4.7.0.72',
        'opencv-python>=4.7.0.72',
        'opencv-python-headless>=4.8.0.74',      
    ],
    python_requires='>=3.8,<3.13',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
