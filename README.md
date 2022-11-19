# Taupe<img width="70em" align="right" src="https://raw.githubusercontent.com/mhucka/taupe/main/.graphics/taupe-icon.png">

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

There are multiple ways of installing Taupe.  Please choose the alternative that suits you.

### _Alternative 1: installing Taupe using `pipx`_

You can use [pipx](https://pypa.github.io/pipx/) to install Taupe. Pipx will install it into a separate Python environment that isolates the dependencies needed by Taupe from other Python programs on your system, and yet the resulting `taupe` command wil be executable from any shell &ndash; like any normal program on your computer. If you do not already have `pipx` on your system, it can be installed in a variety of easy ways and it is best to consult [Pipx's installation guide](https://pypa.github.io/pipx/installation/) for instructions. Once you have pipx on your system, you can install Taupe with the following command:
```sh
pipx install taupe
```

Pipx can also let you run Taupe directly using `pipx run taupe`, although in that case, you must always prefix every Taupe command with `pipx run`.  Consult the [documentation for `pipx run`](https://github.com/pypa/pipx#walkthrough-running-an-application-in-a-temporary-virtual-environment) for more information.


### _Alternative 2: installing Taupe using `pip`_

You should be able to install `taupe` with [`pip`](https://pip.pypa.io/en/stable/installing/) for Python&nbsp;3.  To install `taupe` from the [Python package repository (PyPI)](https://pypi.org), run the following command:
```sh
python3 -m pip install taupe
```

As an alternative to getting it from [PyPI](https://pypi.org), you can use `pip` to install `taupe` directly from GitHub:
```sh
python3 -m pip install git+https://github.com/mhucka/taupe.git
```

_If you already installed Taupe once before_, and want to update to the latest version, add `--upgrade` to the end of either command line above.


### _Alternative 3: installing Taupe from sources_

If  you prefer to install Taupe directly from the source code, you can do that too. To get a copy of the files, you can clone the GitHub repository:
```sh
git clone https://github.com/mhucka/taupe
```

Alternatively, you can download the software source files as a ZIP archive directly from your browser using this link: <https://github.com/mhucka/taupe/archive/refs/heads/main.zip>

Next, after getting a copy of the files,  run `setup.py` inside the code directory:
```sh
cd taupe
python3 setup.py install
```


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

When using `--extract tweets` (the default), `taupe` produces a table with four columns.  Each row of the table corresponds to a type of event in the Twitter timeline: a tweet, a retweet, a reply to another tweet, or a quote tweet. The values in the columns provide details about the event. The following is a summary of the structure:

| Column&nbsp;1 | Column 2 | Column 3 | Column 4 |
|:-------------:|----------|--------|--------|
| tweet timestamp in ISO format  | The&nbsp;URL of the tweet | The type; one of `tweet`, `reply`, `retweet`, or `quote` | (For type `reply` or `quote`.) The URL of the original or source tweet |

The last column only has a value for replies and quote-tweets; in those cases, the URL in the column refers to the tweet being replied to or the tweet being quoted.  The fourth column does not have a value for retweets even though it would be desirable, because the Twitter archive &ndash; strangely &ndash; does not provide the URLs of retweeted tweets.

Here is an example of the output:
```text
2022-09-21T22:36:29+00:00,https://twitter.com/mhucka/status/1572716422857658368,quote,https://twitter.com/poppy_northcutt/status/1572714310077673472
2022-10-10T22:04:20+00:00,https://twitter.com/mhucka/status/1579593701965582336,reply,https://twitter.com/arfon/status/1579572453726355456
2022-10-14T04:17:01+00:00,https://twitter.com/mhucka/status/1580774654217625600,tweet
2022-10-25T14:49:06+00:00,https://twitter.com/mhucka/status/1584919989307715586,retweet
...
```


#### Likes

When using the option `--extract likes`, the output will only contain one column: the URLs of the "liked" tweets. `taupe` cannot provide more detail because the Twitter archive format does not contain date/time information for "likes".

Here is an example of the output when using `--extract likes` in combination with `--canonical-urls`:
```
https://twitter.com/twitter/status/1588146224376463365
https://twitter.com/twitter/status/1588349144803905536
https://twitter.com/twitter/status/1590475356976578560
...
```


### Other options recognized by `taupe`

Running `taupe` with the option `--help` will make it print help text and exit without doing anything else.

The option `--output` controls where `taupe` writes the output. If the value given to `--output` is `-` (a single dash), the output is written to the terminal (stdout). Otherwise, the value must be a file.

If given the `--version` option, this program will print its version and other information, and exit without doing anything else.

If given the `--debug` argument, `taupe` will output a detailed trace of what it is doing. The debug trace will be sent to the given destination, which can be `-` to indicate console output, or a file path to send the debug output to a file.

### _Summary of command-line options_

The following table summarizes all the command line options available.

| Short&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   | Long&nbsp;form&nbsp;opt&nbsp;&nbsp; | Meaning | Default |  |
|---------|--------------------|----------------------|---------|---|
| `-c`    | `--canonical-urls` | Normalize Twitter URLs | Leave URLs unnormalized| |
| `-h`    | `--help`           | Print help info and exit | | |
| `-e`_E_ | `--extract`_E_     | Extract `tweets` or `likes`? | `tweets` | |
| `-o`_O_ | `--output`_O_      | Write output to file _O_ | Write to the terminal | ✦ |
| `-V`    | `--version`        | Print program version info and exit | | |
| `-@`_OUT_ | `--debug`_OUT_   | Debugging mode; write trace to _OUT_ | Normal mode | ⚐ |

✦ &nbsp; To write to the console, you can also use the character `-` as the value of _O_; otherwise, _O_ must be the name of a file where the output should be written.<br>
⚐ &nbsp; To write to the console, use the character `-` as the value of _OUT_; otherwise, _OUT_ must be the name of a file where the output should be written.


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

The [vector artwork](https://thenounproject.com/icon/bird-233023/) of a bird, used as the icon for this repository, was created by [Noe Araujo](https://thenounproject.com/noearaujo/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license. I manually changed the color to be a shade of taupe.

Taupe uses multiple other open-source packages, without which it would have taken much longer to write the software. I want to acknowledge this debt. In alphabetical order, the packages are:
* [Aenum](https://github.com/ethanfurman/aenum) &ndash; Python package for advanced enumerations
* [CommonPy](https://github.com/caltechlibrary/commonpy) &ndash; a collection of commonly-useful Python functions
* [Plac](https://github.com/ialbert/plac) &ndash; a command line argument parser
* [Rich](https://github.com/Textualize/rich) &ndash; library for writing styled text to the terminal
* [Sidetrack](https://github.com/caltechlibrary/sidetrack) &ndash; simple debug logging/tracing package
* [Twine](https://github.com/pypa/twine) &ndash; utilities for publishing Python packages on [PyPI](https://pypi.org)
