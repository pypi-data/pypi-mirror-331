from setuptools import setup, find_packages

setup(
    name="add_confidence_score_and_coordinates",
    version="1.0.2",
    description="A package for updating openai JSON response with confidence score and coordinates",
    author="Shubham Kumar",
    packages=find_packages(),
    install_requires=[
        "Pillow",
        "numpy",
        "python-dotenv",
        "azure-core",
        "azure-ai-documentintelligence==1.0.0",
        "amazon-textract-textractor==1.7.10",
        "PyMuPDF",
        "pytest",
        "fastapi",
        "fuzzywuzzy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)