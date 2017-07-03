"""
python setup file.
taken from
http://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/creation.html#setup-py-descriptiono
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


install_requires = (
    'requests>=2.12.4'
)

setup(
    name='tumblr_image_download_script',
    version='0.1.0',
    author='leyle',
    author_email='jrh@example.com',
    scripts=['bin/tumblr-ids'],
    entry_points={
        'console_scripts': ['tumblr-ids=tumblr_ids.__main__'],
    },
    url='https://github.com/Bakkingamu/tumblr_image_download_script',
    license='MIT License',
    description='Download images from a tumblr blog (all or certain tags).',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        'License :: OSI Approved :: MIT License'
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    zip_safe=False,
    keywords='tumblr downloader cli'
)
