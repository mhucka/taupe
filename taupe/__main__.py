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
    '''Taupe extracts URLs from your downloaded personal Twitter archive.

At its most basic, taupe ("Twitter Archive Url ParsEr") expects to be given
the path to a Twitter archive ZIP file from which it should extract the URLs
of tweets, replies, retweets, and quote tweets, and print the results:

  taupe /path/to/twitter-archive.zip

If instead you want taupe to extract the URLs of "liked" tweets (see the next
section for the difference), use the optional argument --extract likes:

  taupe --extract likes /path/to/twitter-archive.zip

The URLs produced by taupe will be, by default, as they appear in the archive,
which means they will have account names in them. If you prefer to normalize
the URLs to the form https://twitter.com/twitter/status/TWEETID, use the
optional argument --canonical-urls:

  taupe --canonical-urls /path/to/twitter-archive.zip

If you want to send the output to a file instead of the terminal, you can use
the option --output and give it a destination file:

  taupe --output /tmp/urls.txt --canonical-urls /path/to/twitter-archive.zip

The structure of the output
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using --extract tweets (the default), taupe produces a table with four
columns.  Each row of the table corresponds to a tweet of some kind. The
values in the columns provide details:

  Column 1    Column 2    Column 3        Column 4
  --------    --------    -------------   ---------------------------------
  timestamp   tweet URL   type of tweet   URL of quoted or replied-to tweet

The last column only has a value for replies and quote-tweets; in those cases,
it provides the URL of the tweet being replied to or the tweet being quoted.
(The fourth column does not have a value for retweets even though it would be
desirable, because the Twitter archive -- strangely -- does not provide the
URLs of retweeted tweets.)

When using --extract likes, the output will only contain one column: the URLs
of the "liked" tweets. Taupe cannot provide more details (not even timestamps)
because the Twitter archive format does not contain the information.

Other options recognized by taupe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Running taupe with the option --help will make it print help text and exit
without doing anything else.

The option --output controls where taupe writes the output. If the value
given to --output is "-" (a single dash), the output is written to the
terminal (stdout). Otherwise, the value must be a file.

If given the --version option, this program will print its version and other
information, and exit without doing anything else.

If given the --debug argument, taupe will output a detailed trace of what it
is doing. The debug trace will be sent to the given destination, which can be
"-" to indicate console output, or a file path to send the debug output to a
file.

Return values
~~~~~~~~~~~~~

Taupe exits with a return code of 0 if no problem is encountered. Otherwise,
it returns a nonzero value. The following table lists the possible values:

    0 = success -- program completed normally
    1 = the user interrupted the program's execution
    2 = encountered a bad or missing value for an option
    3 = file error -- encountered a problem with a file
    4 = an exception or fatal error occurred

Command-line options summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
            stop(f'File is not readable: {archive_file}', ExitCode.file_error)

    output = '-' if output == 'O' else output
    if output != '-':
        from commonpy.file_utils import writable
        if not writable(output):
            stop(f'Unable to write to destination: {output}', ExitCode.file_error)

    # Do the main work --------------------------------------------------------

    exit_code = ExitCode.success
    try:
        if archive_file == '-':
            log('reading archive from stdin')
            import io
            archive_file = io.BytesIO(sys.stdin.buffer.read())

        log(f'parsing {archive_file} to extract {extract}')
        data = parsed_data(archive_file, extract, canonical_urls)

        log(f'writing output to {output}')
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
            line = 'unknown'
            tb = ex.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
                line = tb.tb_lineno
            stop('Oh no! Taupe encountered an error. Please consider reporting'
                 f' this to the developer. Your version of {taupe.__name__} is'
                 f' {taupe.__version__} and the error occurred on line {line}.'
                 f' For information about how to report this, please see the'
                 f' project page at ' + taupe.__url__)

    # Exit with status code ---------------------------------------------------

    log(f'exiting with exit code {int(exit_code)}.')
    sys.exit(int(exit_code))


# Miscellaneous helpers.
# .............................................................................

def username_from(account_file):
    '''Return the "username" from the account.js file in a Twitter archive.'''
    import json
    # The file starts w/ "window.YTD.account.part0 = ". Skip it; rest is json.
    account_json = json.loads(account_file[27:])
    username = account_json[0]['account']['username']
    log(f'found username "{username}"')
    return username


def likes_from(likes_file, username, canonical_urls = False):
    '''Return the URLs from the likes.js file in a Twitter archive.'''
    import json
    # The file starts with "window.YTD.like.part0 = ". Skip that and it's json.
    likes_json = json.loads(likes_file[23:])
    log(f'extracted {len(likes_json)} likes from the likes file')
    likes_urls = (item['like']['expandedUrl'] for item in likes_json)
    account = 'twitter' if canonical_urls else username
    return (url.replace('i/web', account) for url in likes_urls)


def tweets_from(tweets_file, username, canonical_urls = False):
    '''Return the tweet URLs from the tweets.js file in a Twitter archive.'''
    from dateutil.parser import parse
    import json
    import re

    ending_in_twitter_url = re.compile(r'.*(https://t.co/\S+)$')

    # Helper functions.

    def tweet_url(tweet):
        account = 'twitter' if canonical_urls else username
        return 'https://twitter.com/' + account + '/status/' + tweet['id_str']

    def tweet_date(tweet):
        date = parse(tweet['created_at'])
        return date.isoformat()

    def tweet_data(tweet):
        tdate = tweet_date(tweet)
        turl  = tweet_url(tweet)
        ttype = 'tweet'
        tref  = ''

        # Now the hard part: figuring out the type & extracting reference URLs.
        if tweet.get('in_reply_to_status_id_str', None):
            # Easiest case: replies.
            ttype = 'reply'
            if canonical_urls:
                author = 'twitter'
            elif 'in_reply_to_screen_name' not in tweet:
                # This happens if the tweet being replied to has been deleted.
                log(f'reply tweet {tweet["id"]} refers to a deleted tweet')
                author = 'twitter'
            else:
                author = tweet['in_reply_to_screen_name']
            tweet_id = tweet['in_reply_to_status_id_str']
            tref = 'https://twitter.com/' + author + '/status/' + tweet_id
        elif tweet['full_text'].startswith('RT @'):
            ttype = 'retweet'
            # In my archive, the full_text of retweeted tweets is truncated,
            # and the tweet object doesn't contain the retweeted tweet's id
            # or a URL. (This despite that when I look up my retweet on
            # Twitter, it shows info about the original tweet.) The archive is
            # thus incomplete and I see no way to get the retweeted tweet's id.
            tref = ''
        elif (match := ending_in_twitter_url.match(tweet['full_text'])):
            # This can be either a quote tweet or just a tweet with media in it.
            embedded_url = match.group(1)
            for item in tweet['entities']['urls']:
                if item['url'] == embedded_url:
                    expanded_url = item['expanded_url']
                    if expanded_url.startswith('https://twitter.com'):
                        # Looks like it's a quote tweet.
                        if canonical_urls:
                            author = 'twitter'
                        else:
                            author = user_from_tweet_url(expanded_url)
                    else:
                        # Surprise! Not a quote tweet.
                        break
                    tweet_id = expanded_url[expanded_url.rfind('/') + 1:]
                    ttype = 'quote'
                    tref = 'https://twitter.com/' + author + '/status/' + tweet_id
                    break
            # Default case is normal tweets, possibly with embedded media.

        if tref:
            return [tdate, turl, ttype, tref]
        else:
            return [tdate, turl, ttype]

    # Skip the "window.YTD.tweets.part0 =" at the start of the file.
    all_tweets = json.loads(tweets_file[26:])
    log(f'found a total of {len(all_tweets)} tweets in the tweets file')
    tweets = []
    for tweet_json in all_tweets:
        tweet = tweet_json['tweet']
        tweets.append(','.join(tweet_data(tweet)))
    return sorted(tweets)


def user_from_tweet_url(url):
    # URL of the form https://twitter.com/USERNAME/status/TWEETID
    fragment = url[20:]
    return fragment[: fragment.find('/')]


def parsed_data(source_zip, extract_what, canonical_urls):
    from zipfile import is_zipfile, ZipFile, BadZipFile, LargeZipFile
    if not is_zipfile(source_zip):
        stop('The input does not appear to be a ZIP file.', ExitCode.bad_arg)
    try:
        username = None
        extract_likes = (extract_what != 'tweets')
        log('parsing Twitter data')
        with ZipFile(source_zip) as zf:
            # First find the account name because we need it to construct URLs.
            for item in zf.namelist():
                if item == 'data/account.js':
                    with zf.open(item) as file_:
                        username = username_from(file_.read())
                    break
            if not username:
                stop('Cannot find account.js file in ' + source_zip, ExitCode.file_error)

            # Now extract the tweets.
            for item in zf.namelist():
                if item == 'data/like.js' and extract_likes:
                    with zf.open(item) as file_:
                        return likes_from(file_.read(), username, canonical_urls)
                    break
                elif item == 'data/tweets.js':
                    with zf.open(item) as file_:
                        return tweets_from(file_.read(), username, canonical_urls)
                    break
        log('done parsing Twitter data')
    except BadZipFile:
        stop('Unable to parse ZIP archive.', ExitCode.file_error)
    except LargeZipFile:
        stop('Unable to parse very large ZIP archive.', ExitCode.file_error)


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
    print('[red]' + msg + '[/]')
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
