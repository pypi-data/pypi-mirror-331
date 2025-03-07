from setuptools import setup, find_packages
setup(
    name='bible-chichewa',
    version='1.0.4',
    packages=find_packages('src'),
    package_dir = {'':'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    author_email="m2kdevelopments@gmail.com",
    author="M2K Developments",
    fullname="Chichewa Bible",
    description=" Access and integrate the Chichewa translation of the Bible into your python applications with ease",
    keywords=["bible", "chichewa", 'm2kdevelopments', 'malawi'],
    install_requires=[
        # Add dependencies here...
    ]
)