# Copyright (C) 2023 Jahanzeb Ahmed
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# AutoxEDA any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# For Guidance reach me out through email jahanzebahmed.mail@gmail.com, or through my website <https://jahanzebahemd.netlify.app/>

from setuptools import setup, find_packages

setup(
    name='autoxeda',
    version='0.1.0',
    description='An automated and dynamic exploratory data analysis (EDA) library for streamlined data insights using Large Language Model.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jahanzeb Ahmed',
    author_email='jahanzebahmed.mail@gmail.com',
    url='https://github.com/Jahanzeb-git/autoxeda',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'requests',
        'seaborn',
        'statsmodels',
        'scipy',
        'langchain',
        'tqdm',
        'python-dotenv'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
