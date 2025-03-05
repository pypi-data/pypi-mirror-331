from setuptools import setup, find_packages

setup(
    name='mag_test',
    version='0.1.207',
    packages=find_packages(where='.'),
    install_requires=[],
    author='xlcao',
    author_email='xl_cao@hotmail.com',
    description='测试工具包',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='http://gitlab.magnetitech.com:8088/sources/frame/py-frame/mag_test.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)