from setuptools import setup


setup(
    name='pytest-cli2-ansible',
    version='4.3.0',
    setup_requires='setupmeta',
    author='James Pic',
    author_email='jamespic@gmail.com',
    url='https://yourlabs.io/oss/cli2',
    include_package_data=True,
    license='MIT',
    keywords='cli',
    python_requires='>=3.6',
    entry_points={
        'pytest11': [
            'cli2-ansible-fixtures = pytest_cli2_ansible',
        ],
    },
)
