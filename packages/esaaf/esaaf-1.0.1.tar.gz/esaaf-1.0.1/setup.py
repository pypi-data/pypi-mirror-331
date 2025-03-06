from setuptools import setup, find_packages

setup(
    name="esaaf",
    version="1.0.1",
    author="Lawson Tanner",
    author_email="lawson.tanner@endemolshine.com.au",
    description="A custom converter for Descript sequences from Premiere XML to Avid AAF",
    packages=find_packages(where="src"),  # Automatically find and include packages
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
    python_requires='>=3.7',
    install_requires=[
        'pyaaf2>=1.7.1',
    
    ],
    include_package_data=True,
)