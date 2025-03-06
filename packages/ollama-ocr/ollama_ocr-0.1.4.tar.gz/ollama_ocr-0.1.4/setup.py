from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ollama-ocr',
    version='0.1.4',  # Incrementing from your .gitignore
    description='OCR package using Ollama vision language models.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Anoop Maurya',
    author_email='mauryaanoop3@gmail.com',  
    url='https://github.com/imanoop7/Ollama-OCR',
    package_dir={'': 'src'},  # Tell setuptools packages are under 'src'
    packages=find_packages(where='src'),  # Specify the 'src' directory
    include_package_data=True,  # This is needed to include package_data
    install_requires=[
        'Pillow',
        'requests',
        'python-magic',
        'transformers',
        'streamlit',
        'tqdm',
        'opencv-python',
        'pdf2image',
        'numpy',
        'fitz',
        'pymupdf'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',  # Adjust as needed
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
)