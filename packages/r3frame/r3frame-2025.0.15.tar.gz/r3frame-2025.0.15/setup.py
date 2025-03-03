import setuptools

version = {
    "year" :2025,
    "minor" :0,
    "patch" :15
}

setuptools.setup(
    name='r3frame',
    version=f"{version["year"]}.{version["minor"]}.{version["patch"]}",
    description='A small but powerful pygame framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Izaiyah Stokes',
    author_email='d34d0s.dev@gmail.com',
    url='https://github.com/r3shape/r3frame',
    packages=setuptools.find_packages(),
    package_data={'r3frame': ['assets/fonts/*', 'assets/images/*']},
    install_requires=[
        "pygame-ce"
    ],
    entry_points={
        'console_scripts': [
            'r3playground = r3frame.scripts.playground:playground'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)