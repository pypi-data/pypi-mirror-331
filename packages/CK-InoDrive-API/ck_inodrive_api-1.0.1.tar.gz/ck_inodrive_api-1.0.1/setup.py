import sys

from setuptools import setup

# reading long description from file
try:
    with open('description.md') as file:
        long_description = file.read()
except FileNotFoundError:
    from pkginfo import UnpackedSDist
    package = UnpackedSDist(__file__)
    long_description = package.description

# specify requirements of your package here
REQUIREMENTS = [
    'websocket-client==1.8.0', 
    'ifaddr==0.2.0', 
    'msgpack==1.1.0'
]

# some more details
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows',
    'Topic :: Scientific/Engineering',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.12',
]

# reading version number from file
try:
    from versions import get_latest_number
    latest_version_number = get_latest_number()
except ImportError:
    latest_version_number = package.version

for option in sys.argv:
    if option == "sdist":
        # append version number into __init__.py
        with open("CkInoDriveAPI/__init__.py", "a") as file:
            file.write(f"__version__ = '{latest_version_number}'\n")
            file.close()

# calling the setup function
setup(name='CK-InoDrive-API',
      version=latest_version_number,
      description='InoDrive API Library',
      license_files=['LICENSE.txt', 'README.txt'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://cardinalkinetic.com',
      author='Cardinal Kinetic',
      author_email='support@cardinalkinetic.com',
      license='https://www.cardinalkinetic.com/user-manual/api/inodrive-py',
      packages=['CkInoDriveAPI'],
      package_data={"": ['*.crt']},
      project_urls={
        'Documentation': 'https://www.cardinalkinetic.com/user-manual/api/inodrive-py'
      },
      classifiers=CLASSIFIERS,
      install_requires=REQUIREMENTS,
      keywords='InoWorx InoDrive InoSync MotionControl ServoControl'
      )
