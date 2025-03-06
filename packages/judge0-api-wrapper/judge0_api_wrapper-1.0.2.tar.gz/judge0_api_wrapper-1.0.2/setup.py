from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent.resolve()
REQUIRED = (HERE / "requirements.txt").read_text().splitlines()

setup(
    name='judge0-api-wrapper',
    version='1.0.2',
    description='API wrapper for Judge0 service',
    long_description=(HERE / "README.md").read_text(),
    long_description_content_type='text/markdown',
    author='Fabul0n',  # Например: 'your_github_username'
    author_email='fabulon@mail.ru',  # Опционально
    url='https://github.com/Fabul0n/judge0-api-wrapper',  # Ссылка на репозиторий
    packages=find_packages(),    # Автоматически находит пакеты
    install_requires=REQUIRED,   # Зависимости из requirements.txt
    license='MIT',               # Указание лицензии
    classifiers=[                # Классификаторы для PyPI
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)