from setuptools import setup, find_packages

setup(
    name='VisualShape3D',
    version='1.1.7',
    author='Liqun He',
    author_email='heliqun@ustc.edu.cn',
    description='A package of seting up a 3D polygon provided with its dimensions as well as its orietation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/yourusername/my_package',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        # List your package dependencies here
        'numpy',
        'pandas',
        'matplotlib'
    ],
)