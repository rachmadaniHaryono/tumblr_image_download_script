"""
python setup file.
taken from
http://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/creation.html#setup-py-descriptiono
"""
from distutils.core import setup

setup(
    name='tumblr_image_download_script',
    version='0.1',
    author='leyle',
    author_email='jrh@example.com',
    # packages=['towelstuff', 'towelstuff.test'],
    scripts=['general_run.py'],
    url='https://github.com/Bakkingamu/tumblr_image_download_script',
    license='LICENSE.txt',
    description='Download images from a tumblr blog (all or certain tags).',
    long_description=open('README.md').read(),
    # install_requires=[],
)
