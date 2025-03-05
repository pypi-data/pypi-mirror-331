import re
from os.path import (
    abspath,
    dirname,
    join,
)

from pkg_resources import (
    Requirement,
)
from setuptools import (
    find_packages,
    setup,
)


_COMMENT_RE = re.compile(r'(^|\s)+#.*$')


def _get_requirements(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            line = _COMMENT_RE.sub('', line)
            line = line.strip()

            if line.startswith('-r '):
                for req in _get_requirements(join(dirname(abspath(file_path)), line[3:])):
                    yield req

            elif line:
                req = Requirement(line)
                req_str = req.name + str(req.specifier)

                if req.marker:
                    req_str += '; ' + str(req.marker)

                yield req_str


def _read(file_path):
    with open(file_path, 'r') as infile:
        return infile.read()


setup(
    name='m3-gar-client',
    url='https://stash.bars-open.ru/projects/M3/repos/m3-gar-client',
    license='MIT',
    author='BARS Group',
    description=u'UI клиент для сервера ГАР m3-rest-gar',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=tuple(_get_requirements('requirements/prod.txt')),
    long_description=_read('README.rst'),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.9',
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.2',
    ],
    extras_require={
        'oauth2': (
            'oauthlib>=2,<3',
            'requests-oauthlib<1',
        ),
    },
    dependency_links=(
        'http://pypi.bars-open.ru/simple/m3-builder',
    ),
    setup_requires=(
        'm3-builder>=1.2,<2',
    ),
    set_build_info=dirname(__file__),
)
