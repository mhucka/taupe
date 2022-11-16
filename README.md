# Taupe<img width="70em" align="right" src="https://github.com/mhucka/taupe/blob/main/.graphics/taupe-icon.png">

A simple program to extract the URLs of your tweets, retweets, replies, quote tweets, and "likes" from a personal Twitter archive.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Latest release](https://img.shields.io/github/v/release/mhucka/taupe.svg?style=flat-square&color=purple&label=Release)](https://github.com/mhucka/taupe/releases)


## Table of contents

* [Introduction](#introduction)
* [Installation](#installation)
* [Usage](#usage)
* [Known issues and limitations](#known-issues-and-limitations)
* [Getting help](#getting-help)
* [Contributing](#contributing)
* [License](#license)
* [Acknowledgments](#authors-and-acknowledgments)


## Introduction

When you [download your personal Twitter archive](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive), you receive a [ZIP](https://en.wikipedia.org/wiki/ZIP_(file_format)) file. The contents are not necessarily in a format convenient for doing something with them. For example, you may want to send the URLs to the [Wayback Machine at the Internet Archive](https://archive.org/web/) or do something else with the URLs. For tasks like that, you need to extract URLs from your Twitter archive. That's the purpose of Taupe.

_Taupe_ (a loose acronym of <ins><b>T</b></ins>witter <ins><b>a</b></ins>rchive <ins><b>U</b></ins>RL <ins><b>p</b></ins>ars<ins><b>e</b></ins>r) takes a Twitter archive ZIP file, extracts the URLs corresponding to your tweets, retweets, replies, quote tweets, and liked tweets, and outputs the results in a [comma-separated values (CSV)](https://en.wikipedia.org/wiki/Comma-separated_values) format that you can easily use with other software tools.


## Installation


## Usage

If the installation process described above is successful, you should end up with a program named `taupe` in a location where software is normally installed on your computer.  Running `taupe` should be as simple as running any other command-line program. For example, the following command should print a helpful message to your terminal:
```shell
taupe --help
```

If not given the option `--help` or `--version`, this program expects to be given a [personal Twitter archive file](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive), either on the command line (as an argument) or on standard input (from a pipe or file redirection). Here's an example (and note this path is fake &ndash; substitute a real path on your computer when you do this!):
```shell
taupe /path/to/twitter-archive.zip
```

The URLs produced by `taupe` will be, by default, as they appear in the archive. If you want to [normalize the URLs](https://developer.twitter.com/en/blog/community/2020/getting-to-the-canonical-url-for-a-tweet) into the canonical form `https://twitter.com/twitter/status/TWEETID`, use the option `--canonical-urls` (`-c` for short):
```shell
taupe -c /path/to/twitter-archive.zip
```


### The structure of the output

The output produced by `taupe` differs depending on whether you are extracting tweets or "likes".

#### Tweets

When using `--extract tweets` (the default), `taupe` produces a table with five columns.  Each row of the table corresponds to a type of event in the Twitter timeline: a tweet, a retweet, a reply to another tweet, or a quote tweet. The five columns of the table provide details about the event. The following is a summary of the structure:

| Column&nbsp;1 | Column&nbsp;2 | Column 3 | Column 4 | Column 5 |
|:-------------:|:-------------:|--------|--------|--------|
| date of the tweet   | time of day  | The type; one of `tweet`, `reply`, `retweet`, or `quote` | The&nbsp;URL of the tweet | (For type `reply`, `retweet` or `quote`.) The URL of the original or source tweet |

Every row of the table has a value for the first four columns. The fifth column only has a value when the event involves _someone else_'s tweet; i.e., for replies, retweets, and quote-tweets.

Here is an example of the output:
```text
2022-11-05,18:57:41 +0000,tweet,https://twitter.com/twitter/status/1588948107139895296,
2022-11-06,12:40:20 +0000,retweet,https://twitter.com/twitter/status/1284949108569235206,
...
```


#### Likes

When using the option `--extract likes`, the output will only contain one column: the URLs of the "liked" tweets. The reason `taupe` cannot provide the level of detail described above is that the Twitter archive format itself does not contain date/time information for "likes".

Here is an example of the output when using `--extract likes` in combination with `--canonical-urls`:
```
https://twitter.com/twitter/status/1588146224376463365
https://twitter.com/twitter/status/1588349144803905536
https://twitter.com/twitter/status/1590475356976578560
https://twitter.com/twitter/status/1583401617587863552
...
```


### Other options recognized by `taupe`

Running `taupe` with the option `--help` will make it print help text and exit without doing anything else.

The option `--output` controls where `taupe` writes the output. If the value given to `--output` is `-` (a single dash), the output is written to the terminal (stdout). Otherwise, the value must be a file.

If given the `--version` option, this program will print its version and other information, and exit without doing anything else.

If given the `--debug` argument, `taupe` will output a detailed trace of what it is doing. The debug trace will be sent to the given destination, which can be `-` to indicate console output, or a file path to send the debug output to a file.

### Summary




## Known issues and limitations

This program assumes that the Twitter archive ZIP file is in the format which Twitter produced in mid-November 2022. Twitter probably used a different format in the past, and may change the format again in the future, so `taupe` may or may not work on Twitter archives obtained in different historical periods.

The Twitter archive format for "likes" contains only the tweet identifier and the text of the tweet; consequently, `taupe` cannot provide date/time information for this case.

This program does all its work in memory, which means that `taupe`'s ability to process a given archive depends on its size and how much RAM the computer has. It has only been tested with modest-sized archives. It is unknown how it will behave with exceptionally large archives.


## Getting help

If you find a problem or have a request or suggestion, please submit it in [the GitHub issue tracker](https://github.com/mhucka/taupe/issues) for this repository.


## Contributing

I would be happy to receive your help and participation if you are interested.  Everyone is asked to read and respect the [code of conduct](CONDUCT.md) when participating in this project.  Please feel free to [report issues](https://github.com/mhucka/taupe/issues) or do a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) to fix bugs or add new features.


## License

This software is Copyright (C) 2022, by Michael Hucka and the California Institute of Technology (Pasadena, California, USA).  This software is freely distributed under a 3-clause BSD type license.  Please see the [LICENSE](LICENSE) file for more information.


## Acknowledgments

This work is a personal project developed by the author, using computing facilities and other resources of the [California Institute of Technology Library](https://www.library.caltech.edu).

The [vector artwork](https://thenounproject.com/icon/bird-233023/) of a bird, used as the icon for this repository, was created by [Noe Araujo](https://thenounproject.com/noearaujo/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.
