'''
exit_codes.py: define exit codes for program return values

This file is part of https://github.com/mhucka/taupe/.

Copyright (c) 2022 by Michael hucka.
This code is open-source software released under the MIT license.
Please see the file "LICENSE" for more information.
'''

from aenum import Enum, MultiValue


# I adapted the clever approach posted by the author of the Python aenum
# package, Ethan Furman, to Stack Overflow on 2016-03-13 at
# https://stackoverflow.com/a/35964875/743730
# The most important bit is realizing you can define __int__().

class ExitCode(Enum):
    '''Class of exit codes that this program may return.

    The numeric value of a given code can be obtained by using int().  For
    example, int(ExitCode.success) will produce 0.
    '''

    _init_ = 'value meaning'
    _settings_ = MultiValue

    success        = 0, "success -- program completed normally"
    user_interrupt = 1, "the user interrupted the program's execution"
    bad_arg        = 2, "encountered a bad or missing value for an option"
    file_error     = 3, "encountered a problem with a file or directory"
    exception      = 4, "a miscellaneous exception or fatal error occurred"

    def __int__(self):
        return self.value
