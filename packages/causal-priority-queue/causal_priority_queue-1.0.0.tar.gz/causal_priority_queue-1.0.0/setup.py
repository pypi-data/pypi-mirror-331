from setuptools import setup, find_packages

setup(
    name='causal-priority-queue',  # Package name on PyPI
    version='1.0.0',
    packages=find_packages(),
    install_requires=[],  # No external dependencies
    author='Joy Mukerjee',
    author_email='mukerjeejoy@protonmail.com',
    description='A dynamically adjusting priority queue with causal influences.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/mukerjeejoy-github/causal-priority-queue',  # Link to GitHub repo
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
