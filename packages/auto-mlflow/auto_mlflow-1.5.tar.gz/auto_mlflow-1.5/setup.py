import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="auto_mlflow",
    version="1.5",
    author="Ravin Kumar",
    author_email="mr.ravin_kumar@hotmail.com",
    description="Auto MLFlow is an open-source automated MLOps library for MLFlow in Python. While MLFlow provides a UI for tracking experiments, Auto MLFlow automates and simplifies the logging process, reducing manual effort and ensuring seamless integration with ML workflows.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/mr-ravin/auto_mlflow",
    keywords=['MLFlow', 'MLOps', 'Deep Learning', 'Automation', 'Deployment', 'Deep Learning', 'Architecture'],
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
