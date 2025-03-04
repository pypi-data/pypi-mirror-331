
### 5. **setup.py**


from setuptools import setup, find_packages

setup(
    name='aiassistant-raayan',
    version='0.1.0',
    description='A Python module for AI functionalities like sentiment analysis, text summarization, and question answering using Hugging Face Transformers.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'transformers',
        'torch'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
