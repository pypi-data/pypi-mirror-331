from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='bod',
      version='0.0.1a1',
      description='Blob and Object Dumper',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/ebob9/bod',
      author='Aaron Edwards',
      author_email='bod-util@ebob9.com',
      license='MIT',
      install_requires=[
            'beautifulsoup4'
      ],
      packages=['bod'],
      classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Operating System :: OS Independent"
      ]
      )