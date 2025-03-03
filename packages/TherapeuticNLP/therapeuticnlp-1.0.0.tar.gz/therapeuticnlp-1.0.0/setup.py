from setuptools import setup, find_packages

VERSION = "1.0.0"

setup(
    name="TherapeuticNLP",
    version=VERSION,
    description="A multi-dimensional Natural Language Processing (NLP) framework for analyzing and assessing the quality of therapeutic conversations. This project presents a novel approach to evaluating therapeutic conversation quality using advanced NLP techniques and machine learning. Our framework analyzes key conversational dynamics to distinguish between high and low-quality therapeutic interactions, providing valuable insights for mental health professionals.",
    url="https://github.com/R-Niloy/Estimating-Quality-in-Therapeutic-Conversations-A-Multi-Dimensional-NLP-Framework",
    author="Roy Niloy, Sarmed Shaya, Dylan Weston and Zachary Cote",
    author_email="its.royniloy@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "nltk",
        "transformers",
        "promcse",
        "sentence_transformers",
        "scipy",
        "statistics",
        "openpyxl",
    ],
    python_requires=">=3.6",
)