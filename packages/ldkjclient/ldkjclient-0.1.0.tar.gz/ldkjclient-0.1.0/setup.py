from setuptools import setup, find_packages

setup(
    name='ldkjclient',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "requests==2.32.3", ""
    ],
    author='xuxiadong',
    author_email='xuxiaodong@lingduyun.net',
    description='凌渡科技客户端',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://www.lingduyun.net/',
)
