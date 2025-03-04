from setuptools import setup, find_packages

setup(
    name="aiaf",
    version="0.2.1",
    description="AI Agent Firewall: Prevents prompt injection and adversarial attacks on AI chatbots.",
    author="Your Name",
    author_email="nathanrampersaud@gmail.com",
    url="https://github.com/Nathan8044/aiaf",
    packages=find_packages(),
    install_requires=[
        "openai",  # Required for OpenAI Moderation API
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)