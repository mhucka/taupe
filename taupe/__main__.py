'''
Taupe: Extract the URLs from your personal Twitter archive

This file is part of https://github.com/mhucka/taupe/.

Copyright (c) 2022 by Michael Hucka.
This code is open-source software released under the MIT license.
Please see the file "LICENSE" for more information.
'''

import sys
if sys.version_info <= (3, 8):
    print('taupe requires Python version 3.8 or higher,')
    print('but the current version is ' + str(sys.version_info.major)
          + '.' + str(sys.version_info.minor) + '.')
    exit(1)

# Note: this code uses lazy loading.  Additional imports are made later.
from   commonpy.data_structures import CaseFoldDict
import errno
import plac
from   sidetrack import set_debug, log

from   .exit_codes import ExitCode


# Constants.
# .............................................................................

# Mapping of recognized --extract argument values to canonical names.
EXTRACT_OPTIONS = CaseFoldDict({'all-tweets'     : 'all-tweets',
                                'tweets'         : 'all-tweets',
                                'my-tweets'      : 'my-tweets',
                                'my-tweet'       : 'my-tweets',
                                'my'             : 'my-tweets',
                                'mine'           : 'my-tweets',
                                'retweets'       : 'retweets',
                                'retweet'        : 'retweets',
                                'quoted-tweets'  : 'quote-tweets',
                                'quote-tweets'   : 'quote-tweets',
                                'quoted'         : 'quote-tweets',
                                'replied-tweets' : 'reply-tweets',
                                'reply-tweets'   : 'reply-tweets',
                                'replied'        : 'reply-tweets',
                                'reply'          : 'reply-tweets',
                                'likes'          : 'likes',
                                'liked'          : 'likes',
                                'like'           : 'likes'})

# Main program.
# .............................................................................

@plac.annotations(
    canonical_urls = ('convert URLs to canonical Twitter URL form'       , 'flag'  , 'c'),
    extract        = ('extract info "E" (default: tweets)'               , 'option', 'e'),
    output         = ('write output to destination "O" (default: stdout)', 'option', 'o'),
    version        = ('print program version info and exit'              , 'flag'  , 'V'),
    debug          = ('write debug trace to "OUT" ("-" for console)'     , 'option', '@'),
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
section for the difference), use the optional argument '--extract likes':

  taupe --extract likes /path/to/twitter-archive.zip

The URLs produced by taupe will be, by default, as they appear in the archive,
which means they will have account names in them. If you prefer to normalize
the URLs to the canonical form https://twitter.com/twitter/status/TWEETID, use
the optional argument '--canonical-urls':

  taupe --canonical-urls /path/to/twitter-archive.zip

If you want to send the output to a file instead of the terminal, you can use
the option '--output' and give it a destination file:

  taupe --output /tmp/urls.txt --canonical-urls /path/to/twitter-archive.zip

The structure of the output
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The option '--extract' controls both the content and the format of the output.
The following options are recognized:

  Value           Synonym       Output
  ------------    -------       -----------------------------------------------
  all-tweets      tweets        CSV table with all tweets and details (default)
  my-tweets                     list of URLs of only your original tweets
  retweets                      list of URLs of tweets that are retweets
  quoted-tweets   quote-tweets  list of URLs of (other) tweets you quoted
  replied-tweets  reply-tweets  list of URLs of (other) tweets you replied to

  liked           likes         list of URLs of tweets you "liked"

When using '--extract all-tweets' (the default), taupe produces a table with
four columns.  Each row of the table corresponds to a tweet of some kind. The
values in the columns provide details:

  Column 1    Column 2    Column 3        Column 4
  --------    --------    -------------   ---------------------------------
  timestamp   tweet URL   type of tweet   URL of quoted or replied-to tweet

The last column only has a value for replies and quote-tweets; in those cases,
it provides the URL of the tweet being replied to or the tweet being quoted.
The fourth column does not have a value for retweets even though it would be
desirable, because the Twitter archive (strangely) does not provide the
URLs of retweeted tweets. Note also that this format does NOT include your
"liked" tweets; those are available using a different option described below.

When using '--extract my-tweets', the output is just a single column (a list)
of URLs, one per line, corresponding to just your original tweets. This list
corresponds exactly to column 2 in the '--extract all-tweets' case above.

When using '--extract retweets', the output is a single column (a list) of
URLs, one per line, of tweets that are retweets of other tweets. This list
corresponds to the values of column 2 above when the type is 'retweet'.
IMPORTANT: the Twitter archive does not contain the original tweet's URL,
only the URL of your retweet. Consequently, the output of '--extract retweets'
is YOUR retweet's URL, not the URL of the source tweet.

When using '--extract quoted-tweets', the output is a list of the URLs of
other people's tweets that you have quoted. It corresponds to the subset of
column 4 values above when the type is "quote"; i.e., the source tweet URL,
not the URL of your tweet.

When using '--extract replied-tweets', the output is a list of the URLs of
other people's tweets that you have replied to. It corresponds to the subset
of column 4 values above when the type is "reply"; i.e., the source tweet URL,
not the URL of your tweet.

Finally, when using '--extract likes', the output will contain a list of the
URLs of tweets you have "liked" on Twitter. Taupe cannot provide more details
(not even timestamps) because the Twitter archive format does not contain the
information.

Other options recognized by taupe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Running taupe with the option '--help' will make it print help text and exit
without doing anything else.

The option '--output' controls where taupe writes the output. If the value
given to '--output' is "-" (a single dash), the output is written to the
terminal (stdout). Otherwise, the value must be a file.

If given the '--version' option, this program will print its version and other
information, and exit without doing anything else.

If given the '--debug' argument, taupe will output details about what it is
doing. The debug trace will be sent to the given destination, which can be "-"
to indicate console output, or a file path to send the debug output to a file.

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

    extract = 'all-tweets' if extract == 'E' else extract
    if extract not in EXTRACT_OPTIONS:
        stop('Unrecognized value for --extract option: ' + extract, ExitCode.bad_arg)
    else:
        requested = EXTRACT_OPTIONS[extract]

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

        data = parsed_data(archive_file, requested, canonical_urls)
        filtered_data = filter(None, map(data_filter(requested), data))
        write_data(filtered_data, output)
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

# The functions for extracting URLs from the .js files (currently only likes.js
# and tweets.js) return a common intermediate format consisting of a generator
# that produces 4-tuples:
#
#    (date,  url of my tweet,  type,  url of referenced tweet)
#
# The "type" can be one of "tweet", "reply", "retweet", "quote", or "like".
# Some of the slots in the tuple are not filled in for all types. Notably, if
# the type is "likes", the date and tweet url are empty (because for a "liked"
# tweet, it only makes sense to talk about the referenced tweet's URL).
# Conversely, if we're not extracting "likes", then the referenced tweet url
# slot only has a value for types "quote" and "retweet".
#
# This kind of funneling of all types into a common intermediate form, even
# though there is heterogeneity in the underlying data, is done to shorten
# and simplify the code and not really for performance reasons. Performance
# is currently not a concern because the expectation is that users won't run
# this program very often anyway.

def data_filter(requested):
    return {
        'all-tweets'  : lambda row: ','.join(row),
        'my-tweets'   : lambda row: row[1],
        'retweets'    : lambda row: row[1] if row[2] == 'retweet' else '',
        'quote-tweets': lambda row: row[3] if row[2] == 'quote' else '',
        'reply-tweets': lambda row: row[3] if row[2] == 'reply' else '',
        'likes'       : lambda row: row[3],
    }.get(requested)


def likes_from(likes_file, username, canonical_urls = False):
    '''Return the URLs from the likes.js file in a Twitter archive.'''
    import json
    # The file starts with "window.YTD.like.part0 = ". Skip that and it's json.
    likes_json = json.loads(likes_file[23:])
    log(f'extracted {len(likes_json)} likes from the likes file')
    likes_urls = (item['like']['expandedUrl'] for item in likes_json)
    account = 'twitter' if canonical_urls else username
    # Return the same 4-tuple format as tweets_from(...).
    return (('', '', 'like', url.replace('i/web', account)) for url in likes_urls)


def tweets_from(tweets_file, username, canonical_urls = False):
    '''Return tuples of parsed data from tweets.js in a Twitter archive.'''
    from dateutil.parser import parse
    import json
    import re

    ending_in_twitter_url = re.compile(r'.*(https://t.co/\S+)$')

    # Helper functions.

    def user_from_tweet_url(url):
        if canonical_urls:
            return 'twitter'
        else:
            # Extract USERNAME from https://twitter.com/USERNAME/status/TWEETID
            fragment = url[20:]
            return fragment[: fragment.find('/')]

    def tweet_url(tweet):
        account = 'twitter' if canonical_urls else username
        return 'https://twitter.com/' + account + '/status/' + tweet['id_str']

    def tweet_date(tweet):
        date = parse(tweet['created_at'])
        return date.isoformat()

    def tweet_data(tweet):
        tdate = tweet_date(tweet)
        turl  = tweet_url(tweet)

        # Figure out the type & extracting reference URLs. Look for specific
        # cases; default case is normal tweet, possibly with embedded media.
        ttype = 'tweet'
        tref  = ''
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
            for entity in tweet['entities']['urls']:
                if entity['url'] != embedded_url:
                    continue
                # Found the entity info for the URL we pulled from the text.
                expanded_url = entity['expanded_url']
                if not expanded_url.startswith('https://twitter.com'):
                    # This is not a quote tweet after all.
                    break
                author = user_from_tweet_url(expanded_url)
                tweet_id = expanded_url[expanded_url.rfind('/') + 1:]
                tref = 'https://twitter.com/' + author + '/status/' + tweet_id
                ttype = 'quote'
                break

        return (tdate, turl, ttype, tref)

    # The 26 is to skip the "window.YTD.tweets.part0 =" text at the start.
    all_tweets = json.loads(tweets_file[26:])
    log(f'found a total of {len(all_tweets)} tweets in the tweets file')
    return sorted(tweet_data(tweet_json['tweet']) for tweet_json in all_tweets)


def username_from(account_file):
    '''Return the "username" from the account.js file in a Twitter archive.'''
    import json
    # The file starts w/ "window.YTD.account.part0 = ". Skip it; rest is json.
    account_json = json.loads(account_file[27:])
    username = account_json[0]['account']['username']
    log(f'found username "{username}"')
    return username


def parsed_data(source_zip, requested, canonical_urls):
    from zipfile import is_zipfile, ZipFile, BadZipFile, LargeZipFile
    if not is_zipfile(source_zip):
        stop('The input does not appear to be a ZIP file.', ExitCode.bad_arg)
    log(f'parsing Twitter data to extract {requested}')
    try:
        username = None
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
                if item == 'data/like.js' and requested == 'likes':
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
    log(f'writing output to {dest}')
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
