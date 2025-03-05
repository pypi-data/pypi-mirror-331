from setuptools import setup, find_packages

setup(
    name="seaturtle_simulator",
    version="0.1",
    packages=find_packages(),
    install_requires=["ttkbootstrap","numpy","pillow","matplotlib"],
    entry_points={
        "console_scripts": [
            "seaturtle-simulator=seaturtle_simulator.main:run"
        ]
    }
)