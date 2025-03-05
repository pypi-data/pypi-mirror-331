from setuptools import setup, find_packages

setup(
    name='persian-editor',
    version='1.0.0',
    description='ویرایشگر متنی فارسی پیشرفته برای جنگو با امکانات کامل از جمله آپلود تصویر، حالت HTML، تمام صفحه و Autosave',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Mohammad_Ramezaniyan',
    author_email='pltmohammad7@gmail.com',
    url='https://github.com/SaEeD802/persian-editor',
    packages=find_packages(exclude=["persian_editor.static*", "persian_editor.templates*"]),
    include_package_data=True,
    classifiers=[
         'Development Status :: 5 - Production/Stable',
         'Framework :: Django',
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
    ],
    install_requires=[
         'Django>=2.2',
         'bleach>=3.1.0',
    ],
)
