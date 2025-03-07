from setuptools import setup, find_packages

setup(
    name="resume-copilot-lib",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    author="ResumeCopilot",
    author_email="support@resumecopilot.net",
    description="A Python library to interact with the Resume Copilot API, allowing job search integration into applications.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://resumecopilot.net/",
    project_urls={
        "Homepage": "https://resumecopilot.net/",
        "Documentation": "https://api.resumecopilot.net/swagger/index.html",
        "Source Code": "https://github.com/resumecopilot-net/resume-copilot-lib-python",
        "Bug Tracker": "https://github.com/resumecopilot-net/resume-copilot-lib-python/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)