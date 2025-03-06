from setuptools import setup

setup(
    name="NeuraFlow",  # Nome do pacote
    version="0.1",     # Versão do pacote
    py_modules=["NeuraFlow"],  # Indica o arquivo principal
    install_requires=[  # Dependências do pacote
        "numpy",
        "joblib",
        "matplotlib",
        "scikit-learn",
        "imblearn"
    ],
    author="Davi VilasBoas Ranci",
    author_email="rancidavi@gmail.com",
    description="Pacote para redes neurais e aprendizado de máquina",
    long_description=open("README.md").read(),  # Lê o conteúdo do README
    long_description_content_type="text/markdown",
    url="https://github.com/Davizoca123312",
    classifiers=[  # Classificadores de projeto no PyPI
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
