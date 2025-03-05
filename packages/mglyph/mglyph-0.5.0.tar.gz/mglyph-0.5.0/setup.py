from setuptools import setup

setup(
    name='mglyph',
    version='0.5.0',    
    description='The MGlyph package',
    homepage='https://tmgc.fit.vutbr.cz/',
    url='https://git.fit.vutbr.cz/herout/mglyph',
    author='Adam Herout, Vojtech Bartl, ',
    author_email='herout@vutbr.cz, ibartl@fit.vut.cz',
    license='MIT',
    packages=['mglyph'],
    package_dir={'mglyph': 'src'},
    install_requires=[
                    'skia-python',
                    'colour'
                    ],
    python_requires='>=3.7',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
)