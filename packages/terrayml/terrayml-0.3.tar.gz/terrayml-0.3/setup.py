from setuptools import setup

setup(
    name="terrayml",
    version="0.3",
    py_modules=["terrayml"],
    install_requires=["awscli", "Click", "PyYAML", "python-dotenv"],
    entry_points="""
        [console_scripts]
        terrayml=terrayml:cli
    """,
)
