from setuptools import setup

setup(name='civic_api_client',
      version = '0.1.0',
      description = 'Examples and tools for using the CIVIC API',
      install_requires = [
          'requests',
          'flask',
      ],
      entry_points = {
          'console_scripts': ['civic-api-client=civic_api_client.command_line:main'],
      },
      classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords = 'API client for civic',
      url = 'http://github.com/griffithlab/civic_api_client',
      author = 'Avinash Ramu',
      author_email = 'avinash3003@yahoo.co.in',
      license = 'MIT',
      packages = ['civic_api_client'],
      include_package_data = True,
      zip_safe = False)
