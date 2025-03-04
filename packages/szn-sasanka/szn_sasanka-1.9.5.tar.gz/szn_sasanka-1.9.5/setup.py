from setuptools import setup, find_packages

setup(
    name="szn-sasanka",
    version="1.9.5",
    packages=find_packages(),
    description="Balíček pro szn sasanku interni system ktery funguje a automaticky stahuje manual k balicku",
    author="Pen Test",
    author_email="test.skvara@seznam.cz",
    url="https://example.com/szn-sasanka",
    entry_points={
        "console_scripts": [
            "szn_sasanka=szn_sasanka.__init__:main",
        ],
    },
)
