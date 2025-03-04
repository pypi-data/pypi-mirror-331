from setuptools import setup

setup(
    name='ezdrawing',
    version='0.0.10',
    py_modules=['ezdrawingpg', 'ezdrawingtk'],
    install_requires=[
        'pygame>=2.6',
    ],
    python_requires='>=3.10',
    author='Empika',
    description=open('README.md').read(),
    long_description=open('README.md').read(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
)