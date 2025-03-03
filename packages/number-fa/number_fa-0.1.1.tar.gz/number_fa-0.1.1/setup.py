from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='number_fa',  # نام کتابخانه
    version='0.1.1',  # نسخه جدید
    packages=find_packages(),
    description='A library to convert numbers to Persian words',
    long_description=long_description,  # استفاده از README.md
    long_description_content_type="text/markdown",  # مشخص کردن فرمت Markdown
    author='Matin Jozi',
    author_email='m.matin.jozi@gmail.com',
    url='https://github.com/Matinjozi/number_fa',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
