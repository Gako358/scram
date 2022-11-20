from distutils.core import setup

setup(
    name="scramgit",
    version="0.1",
    description="A simple git wrapper",
    author="MerrinX",
    author_email="gako358@outlook.com",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "scramgit = main:Scram.run",
        ]
    },
)
