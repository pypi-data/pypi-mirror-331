from setuptools import setup, find_packages

setup(
    name='pygrafical',
    version='0.0.11',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'pygrafical': ['lib.so'],
        'pygrafical.hooks': ['*.py']# Укажите путь к вашему файлу библиотеки
    },
    install_requires=[
        # Список зависимостей, если есть
    ],
    author='tetredial_9274',
    author_email='system32@mail.ru',
    description='графическая библиотека основаная на Windows API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Ananimys784/Kingurio',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)