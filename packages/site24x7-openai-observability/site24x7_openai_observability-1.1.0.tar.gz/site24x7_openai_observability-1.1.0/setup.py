from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='site24x7_openai_observability',
      version='1.1.0',
      description='Tool to monitor openai requests',
      url='https://site24x7.com',
      author='Zoho Corporation Pvt. Ltd.',
      author_email='apm-insight@zohocorp.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='LICENSE.txt',
      packages=find_packages(exclude=['tests', 'tests.*']),
      include_package_data = True,
      python_requires='>=3.5',
      install_requires=[
            "requests"
      ],
      zip_safe=False)

      