gmusicapi-scripts
=================

A collection of scripts for [gmusicapi](https://github.com/simon-weber/Unofficial-Google-Music-API).

## Description

### gmsync

[gmsync.py](https://github.com/thebigmunch/gmusicapi-scripts/blob/master/gmsync.py) is a smart syncing script. It will only make an upload request for songs that are not already in your Google Music library.

### gmupload

[gmupload.py](https://github.com/thebigmunch/gmusicapi-scripts/blob/master/gmupload.py) is a blind upload script. It will make an upload request for all files matching the input.

## Usage

### gmsync

During your first run of the script, you will be given a link to authorize the application. Paste that link in your browser and click Allow. Enter the given code into the terminal prompt.

* Upload all files of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462) in your current directory and all subdirectories not already in your Google Music library

        gmsync.py

* Upload all files of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462) in the specified directory and all its subdirectories not already in your Google Music library

        gmsync.py /path/to/directory

* Upload the specified file of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462) not already in your Google Music library

        gmsync.py /path/to/song.mp3

* Upload all files of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462) from the specified directories and/or list of files not already in your Google Music library (this will handle directories recursively as above)

        gmsync.py /path/to/directory1 /path/to/directory2 ...
        gmsync.py /path/to/song1.mp3 /path/to/song2.mp3 ...
        gmsync.py /path/to/directory1 /path/to/song1.mp3 ...

* Upload all files of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462) matching pattern(s) not already in your Google Music library

        gmsync.py /path/to/*.mp3 ...

### gmupload

During your first run of the script, you will be given a link to authorize the application. Paste that link in your browser and click Allow. Enter the given code into the terminal prompt.

* Upload all files of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462) in your current directory and all subdirectories

        gmupload.py

* Upload all files of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462) in the specified directory and all its subdirectories

        gmupload.py /path/to/directory

* Upload the specified file of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462)

        gmupload.py /path/to/song.mp3

* Upload all files of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462) from the specified directories and/or list of files (this will handle directories recursively as above)

        gmupload.py /path/to/directory1 /path/to/directory2 ...
        gmupload.py /path/to/song1.mp3 /path/to/song2.mp3 ...
        gmupload.py /path/to/directory1 /path/to/song1.mp3 ...

* Upload all files of a [supported format](https://support.google.com/googleplay/bin/answer.py?hl=en&answer=1100462) matching pattern(s)

        gmupload.py /path/to/*.mp3 ...

### Contact

You can contact the author (thebigmunch) in ``#gmusicapi`` on ``irc.freenode.net``