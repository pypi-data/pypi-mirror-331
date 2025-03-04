from setuptools import setup, find_packages

setup(
    name="blackspammerbd1",
    version="1.0",
    packages=find_packages(),
    install_requires=["requests", "cryptography", "flask"],
    entry_points={
        "console_scripts": [
            "bsb=blackspammerbd1.main:main"
        ]
    }
)
