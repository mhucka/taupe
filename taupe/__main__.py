'''
Taupe: Extract the URLs from your personal Twitter archive

Authors
-------

Michael Hucka <mhucka@caltech.edu>

Copyright
---------

Copyright (c) 2022 by Michael Hucka and the California Institute of Technology.
This code is open-source software released under a 3-clause BSD license.
Please see the file "LICENSE" for more information.
'''

import sys
if sys.version_info <= (3, 8):
    print('taupe requires Python version 3.8 or higher,')
    print('but the current version is ' + str(sys.version_info.major)
          + '.' + str(sys.version_info.minor) + '.')
    exit(1)

# Note: this code uses lazy loading.  Additional imports are made later.
import errno
import plac
from   sidetrack import set_debug, log

from   .exit_codes import ExitCode


# Main program.
# .............................................................................

@plac.annotations(
    canonical_urls = ('convert URLs to canonical Twitter URL form'    , 'flag'  , 'c'),
    extract        = ('extract tweets or likes? (default: tweets)'    , 'option', 'e'),
    output         = ('write the output to file "O" (default: stdout)', 'option', 'o'),
    version        = ('print program version info and exit'           , 'flag'  , 'V'),
    debug          = ('write debug trace to "OUT" ("-" for console)'  , 'option', '@'),
    archive_file   = 'path to Twitter archive ZIP file',
)
def main(canonical_urls = False, extract = 'E', output = 'O', version = False,
         debug = 'OUT', *archive_file):
    '''
    Taupe: extract the URLs from your personal Twitter archive.
    '''

    # Process arguments & handle early exits ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    debugging = (debug != 'OUT')
    if debugging:
        set_debug(True, debug)
        import faulthandler
        faulthandler.enable()

    if version:
        from taupe import print_version
        print_version()
        sys.exit(int(ExitCode.success))

    log('starting.')
    log('command line: ' + str(sys.argv))

    extract = 'tweets' if extract == 'E' else extract
    if extract not in ('tweets', 'likes'):
        stop('Unrecognized value for --extract option: ' + extract, ExitCode.bad_arg)

    archive_file = '-' if not archive_file else archive_file[0]
    if archive_file == '-' and sys.stdin.isatty():
        stop('Need archive as argument or via pipe/redirection.', ExitCode.bad_arg)
    elif archive_file != '-':
        from commonpy.file_utils import readable
        from os.path import exists, isfile
        if not exists(archive_file):
            stop(f'Path does not appear to exist: {archive_file}', ExitCode.bad_arg)
        if not isfile(archive_file):
            stop(f'Path is not a file: {archive_file}', ExitCode.bad_arg)
        if not readable(archive_file):
            stop(f'File is not readable: {archive_file}')

    output = '-' if output == 'O' else output
    if output != '-':
        from commonpy.file_utils import writable
        if not writable(output):
            stop(f'Unable to write to destination: {output}')

    # Do the main work --------------------------------------------------------

    exit_code = ExitCode.success
    try:
        if archive_file == '-':
            log('reading archive from stdin')
            import io
            archive_file = io.BytesIO(sys.stdin.buffer.read())

        log(f'parsing {archive_file} to extract {extract}')
        data = extract_data(archive_file, extract, canonical_urls)

        log('writing output to {output}')
        write_data(data, output)
    except KeyboardInterrupt:
        # Catch it, but don't treat it as an error; just stop execution.
        log('keyboard interrupt received')
        exit_code = ExitCode.user_interrupt
    except Exception as ex:             # noqa: PIE786
        exit_code = ExitCode.exception
        import traceback
        exception = sys.exc_info()
        details = ''.join(traceback.format_exception(*exception))
        log('exception: ' + str(ex) + '\n\n' + details)
        if debugging and debug == '-':
            from rich.console import Console
            Console().print_exception()
        else:
            import taupe
            line = traceback.extract_stack()[-1][1]
            stop('Oh no! Taupe encountered an error. Please consider reporting'
                 ' this to the developer. For information about how, please'
                 ' see the project page:\n    ' + taupe.__url__ + '\nYou are'
                 f' running {taupe.__name__} version {taupe.__version__} and'
                 f' the error occurred on line {line}:\n    "' + str(ex) + '"')

    # And exit ----------------------------------------------------------------

    log(f'exiting with exit code {int(exit_code)}.')
    sys.exit(int(exit_code))


# Miscellaneous helpers.
# .............................................................................

def likes_from(likes_file, canonical_urls = False):
    import json
    # The file starts with "window.YTD.like.part0 = ". Skip that and it's json.
    likes_json = json.loads(likes_file[23:])
    log(f'extracted {len(likes_json)} likes from the likes file')
    likes_urls = (data['like']['expandedUrl'] for data in likes_json)
    if canonical_urls:
        log('converting https://twitter.com/i/web URLs')
        return (url.replace('i/web', 'twitter') for url in likes_urls)
    else:
        return likes_urls


def tweets_from(tweets_file, canonical_urls = False):
    import json
    # The file starts with "window.YTD.tweets.part0". Skip that part.
    tweets_json = json.loads(tweets_file[26:])
    log(f'extracted {len(tweets_json)} tweets from the tweets file')


def extract_data(source_zip, extract_what, canonical_urls):
    extract_likes = (extract_what != 'tweets')
    import zipfile
    if not zipfile.is_zipfile(source_zip):
        stop('The input does not appear to be a ZIP file.')
    try:
        with zipfile.ZipFile(source_zip) as zf:
            for item in zf.namelist():
                if item == 'data/like.js' and extract_likes:
                    with zf.open(item) as file_:
                        return likes_from(file_.read(), canonical_urls)
                    break
                elif item == 'data/tweets.js':
                    with zf.open(item) as file_:
                        return tweets_from(file_.read(), canonical_urls)
                    break
    except zipfile.BadZipFile:
        stop('Unable to parse ZIP archive due to data corruption or format error.')
    except zipfile.LargeZipFile:
        stop('Unable to parse very large ZIP archive.')


def write_data(rows, dest):
    try:
        if dest == '-':
            print(*rows, flush = True, sep = '\n')
            sys.stdout.flush()
        else:
            with open(dest, 'w') as output:
                output.write('\n'.join(rows))
    except IOError as ex:
        # Check for broken pipe, as happens when the output is sent to "head".
        if ex.errno == errno.EPIPE:
            log('broken pipe')
            import os
            # This solution comes from a 2015-05-07 posting by user "mklement0"
            # to Stack Overflow at https://stackoverflow.com/a/30091579/743730.
            # Python flushes standard streams on exit, so redirect remaining
            # output to devnull to avoid another BrokenPipeError at shutdown.
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
        else:
            # A real error, not merely a broken pipe. Bubble up to caller.
            raise


def stop(msg, err = ExitCode.exception):
    '''Print an error message and exit with an exit code.'''
    log('printing to terminal: ' + msg)
    from rich import print
    from rich.text import Text
    from rich.style import Style
    print(Text(msg, style = Style.parse('red')))
    log(f'exiting with exit code {int(err)}.')
    sys.exit(int(err))


# Main entry point.
# .............................................................................

# The following entry point definition is for the console_scripts keyword
# option to setuptools. The entry point for console_scripts has to be a
# function that takes zero arguments.
def console_scripts_main():
    plac.call(main)


# The following allows users to invoke this using "python3-m taupe" and also
# pass it an argument of "help" to get the help text.
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'help':
        plac.call(main, ['-h'])
    else:
        plac.call(main)


# For Emacs users
# .............................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
