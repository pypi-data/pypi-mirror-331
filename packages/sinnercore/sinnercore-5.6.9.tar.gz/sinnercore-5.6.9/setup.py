from setuptools import setup, find_packages

setup(
    name="sinnercore",
    version="5.6.9",  # Keep this in sync with __init__.py
    author="Sinner Murphy",
    author_email="sinnermurphy@hi2.in",
    description="A Powerful And Advance Telegram Bot By Sinner Murphy. Latest Version As Of 05 March 2025. Fantastic Package With Awesome Features.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourgithub/SinnerMurphy",
    packages=find_packages(),
    install_requires=[
        "telethon",
        "sqlalchemy",
        "pg8000",
        "googletrans==4.0.0-rc1",
        "google",
        "instaloader",
        "requests",
        "emoji",
        "gtts",
        "pytz",
    ],
    license="MIT",  # License type
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

