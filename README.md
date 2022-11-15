# Taupe

A simple program to extract the URLs of your tweets, retweets, replies, quote tweets, and "likes" from a personal Twitter archive. _Taupe_ is a loose acronym of <ins><b>T</b></ins>witter <ins><b>a</b></ins>rchive <ins><b>U</b></ins>RL <ins><b>p</b></ins>ars<ins><b>e</b></ins>r.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Latest release](https://img.shields.io/github/v/release/mhucka/taupe.svg?style=flat-square&color=b44e88)](https://github.com/mhucka/taupe/releases)


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

When you [download your personal Twitter archive](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive), you receive a [ZIP](https://en.wikipedia.org/wiki/ZIP_(file_format)) file. The contents are complete, but not in a convenient format for doing something with them. For example, you may want to take snapshots of your tweets as they appear on Twitter, or send the URLs to the [Wayback Machine at the Internet Archive](https://archive.org/web/), or do something else with the URLs. For tasks like that, you need to extract URLs from your personal Twitter archive. That's the purpose of Taupe.

_Taupe_ (a loose acronym of <ins><b>T</b></ins>witter <ins><b>a</b></ins>rchive <ins><b>U</b></ins>RL <ins><b>p</b></ins>ars<ins><b>e</b></ins>r) takes a Twitter archive ZIP file and extracts the URLs corresponding to your original tweets, retweets, replies, and liked tweets. It can produce output in [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) format or as a [Markdown](https://en.wikipedia.org/wiki/Markdown) table.


## Installation


## Usage

Assuming the installation process described above was successful, you should end up with a program named `taupe` in a location where software is normally installed on your computer.  Running `taupe` should be as simple as running any other terminal command. For example, the following command should result in a helpful summary being printed to your terminal:
```shell
taupe --help
```


### Basic usage

If not given the option `--help` or `--version` (explained below), `taupe` requires one argument on the command line: the path to a Twitter archive file. For example, the following command,
```shell
taupe /path/to/your/twitter-archive.zip
```
will produce output on your terminal that looks like this:
```text
2022-11-05,18:57:41 +0000,tweet,https://twitter.com/someuser/status/1588948107139895296,
2022-11-06,12:40:20 +0000,retweet,https://twitter.com/someuser/status/1284949108569235206,
...
```

To save this output to a file, you can use `taupe`'s `--output` option (described below) or simply redirect stdout to a file. To change the format of the output, use the option `--format` (also described below).


### The structure of the output

No matter whether the output is CSV or Markdown, the structure is always tabular. Each row of the table corresponds to a type of event in the Twitter timeline: a tweet, a retweet, a reply to another tweet, or a "like" of a tweet. The five columns of the table provide details about the event. The following is a summary of the structure:

| Col. 1 | Col. 2 | Col. 3 | Col. 4 | Col. 5 |
|--------|--------|--------|--------|--------|
| date   | time   | `tweet`, `reply`, `retweet`, `like` | URL of original tweet, reply, or (your) retweet | URL of replied-to tweet, original retweeted tweet, or liked tweet |

Every row of the table has a value for the first three columns. The fourth column has a value for original tweets, replies to other people's tweets, or retweets of other people's tweets; it does not have a value for "likes" (because the URLs of liked tweets are in the fifth column). The fifth column only has a value when the event involves _someone else_'s tweet: replies to other people's tweets, retweets, and "likes".


### Options recognized by `taupe`

Running `taupe` with the option `--help` will make it print help text and exit without doing anything else.

The option `--format` controls what kind of output is written by `taupe`. A value of `csv` (the default) makes it produce [comma-separated value](https://en.wikipedia.org/wiki/Comma-separated_values) format; a value of `markdown` or `md` makes it produce [Markdown](https://en.wikipedia.org/wiki/Markdown).

The option `--output` controls where `taupe` writes the output. If not given, or if the value is `-`, the output is written to the terminal (stdout). Otherwise, the value can be a file to tell `taupe` to write the CSV or Markdown content to a file.

If given the `--version` option, this program will print the version and other information, and exit without doing anything else.

If given the `--debug` argument, `taupe` program will output a detailed trace of what it is doing. The debug trace will be sent to the given destination, which can be `-` to indicate console output, or a file path to send the output to a file.


## Known issues and limitations

This program assumes that the Twitter archive ZIP file is in the format which Twitter produced in mid-November 2022. Twitter probably used a different format in the past, and may change the format again in the future, so `taupe` may or may not work on Twitter archives obtained in different historical periods.

## Getting help

If you find a problem or have a request or suggestion, please submit it in [the GitHub issue tracker](https://github.com/mhucka/taupe/issues) for this repository.


## Contributing

I would be happy to receive your help and participation if you are interested.  Everyone is asked to read and respect the [code of conduct](CONDUCT.md) when participating in this project.  Please feel free to [report issues](https://github.com/mhucka/taupe/issues) or do a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) to fix bugs or add new features.


## License

This software is Copyright (C) 2022, by Michael Hucka and the California Institute of Technology (Pasadena, California, USA).  This software is freely distributed under a 3-clause BSD type license.  Please see the [LICENSE](LICENSE) file for more information.


## Acknowledgments

This work is a personal project developed by the author, using computing facilities and other resources of the [California Institute of Technology Library](https://www.library.caltech.edu).
