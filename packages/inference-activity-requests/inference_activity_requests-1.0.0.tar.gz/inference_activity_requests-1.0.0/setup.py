from setuptools import setup, find_packages

setup(
    name="inference-activity-requests",
    version="1.0.0",
    description="Requests hooks for tracking inference activities on Heroku AI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0"
    ],
    author="Add Co",
    license="MIT",
    keywords=[
        "requests",
        "hooks",
        "heroku",
        "inference",
        "tracking"
    ],
)