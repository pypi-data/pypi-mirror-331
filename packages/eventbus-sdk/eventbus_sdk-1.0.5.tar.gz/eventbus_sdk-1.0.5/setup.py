from setuptools import setup, find_packages

setup(
    name="eventbus_sdk",
    version="1.0.5",
    packages=find_packages(),
    install_requires=[
        "django",
        "celery",
        "kombu",
        "python-dotenv",
    ],
    description="Internal SDK for event-driven microservices communication",
    url="https://github.com/WildWildLeads/eventbus",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
