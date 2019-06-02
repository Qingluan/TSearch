
from setuptools import setup, find_packages


setup(name='TSearch',
    version='0.0.0',
    description='a searcher in terminal',
    url='https://github.com/xxx',
    author='auth',
    author_email='xxx@gmail.com',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=['aiohttp','x_menu','aiohttp-socks','bs4','lxml'],
    entry_points={
        'console_scripts': ['d-cli=TSearch_src.cmd:main']
    },

)
