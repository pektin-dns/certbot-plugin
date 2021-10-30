import os
import sys

from setuptools import find_packages
from setuptools import setup

version = '0.1.0'

install_requires = [
    'setuptools>=39.0.1',
    'requests>=2.22.0'
]

if not os.environ.get('SNAP_BUILD'):
    install_requires.extend([
        # This is the version that is available in the Ubuntu 20.04 LTS repositories.
        f'acme>=0.40.0',
        f'certbot>=0.40.0',
    ])
elif 'bdist_wheel' in sys.argv[1:]:
    raise RuntimeError('Unset SNAP_BUILD when building wheels '
                       'to include certbot dependencies.')
if os.environ.get('SNAP_BUILD'):
    install_requires.append('packaging')

docs_extras = [
    'Sphinx>=1.0',  # autodoc_member_order = 'bysource', autodoc_default_flags
    'sphinx_rtd_theme',
]

setup(
    name='certbot-dns-pektin',
    version=version,
    description="Pektin DNS Authenticator plugin for Certbot",
    url='https://git.y.gy/pektin/certbot-plugin',
    author="Max von Forell",
    author_email='max@vonforell.de',
    license='Apache License 2.0',
    python_requires='>=3.6',

    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'docs': docs_extras,
    },
    entry_points={
        'certbot.plugins': [
            'dns-pektin = certbot_dns_pektin._internal.dns_pektin:Authenticator',
        ],
    },
)
