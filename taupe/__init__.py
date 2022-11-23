'''
Taupe: Extract the URLs from your personal Twitter archive

Authors
-------

Michael Hucka <mhucka@caltech.edu>

Copyright
---------

Copyright (c) 2022 by Michael Hucka.
This code is open-source software released under the MIT license.
Please see the file "LICENSE" for more information.
'''

# Package metadata ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  ╭────────────────────── Notice ── Notice ── Notice ─────────────────────╮
#  |    The following values are automatically updated at every release    |
#  |    by the Makefile. Manual changes to these values will be lost.      |
#  ╰────────────────────── Notice ── Notice ── Notice ─────────────────────╯

__version__     = '1.1.0'
__description__ = 'Taupe: a tool to extract URLs from your personal Twitter archive'
__url__         = 'https://github.com/mhucka/taupe'
__author__      = 'Mike Hucka'
__email__       = 'mhucka@caltech.edu'
__license__     = 'MIT license'


# Miscellaneous utilities.
# .............................................................................

def print_version():
    print(f'{__name__} version {__version__}')
    print(f'Authors: {__author__}')
    print(f'URL: {__url__}')
    print(f'License: {__license__}')
