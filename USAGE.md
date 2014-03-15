Usage
=====

## General

``script.py [args] [input]``

During the first run of the scripts, you will be given a link to authorize the application with Google Music if necessary. Paste that link in your browser and click Allow. Enter the given code into the terminal prompt.


## gmsync

Supports **.mp3**, **.flac**, **.m4a**, **.ogg***

Args         |  Description
-------------|-----------
-h, --help   |  Show help message
-c, --cred   |  Specify oauth credential file name to use/create<br>(Default: "oauth")
-l, --log    |  Enable gmusicapi logging
-m, --match  |  Enable scan and match
-e, -exclude |  Exclude file paths matching a Python regex pattern<br>This option can be set multiple times
-d, --dry-run|  Output list of songs that would be uploaded and excluded
-q, --quiet  |  Don't output status messages<br>-l,--log will display gmusicapi warnings<br>-d,--dry-run will display song list
input        |  Files, directories, or glob patterns to upload<br>Defaults to current directory if omitted

**Example:** ``gmsync.py -m /path/to/music /other/path/to/music.mp3 /another/path/to/*.flac``

\* _Non-MP3 files are transcoded with avconv to 320kbps MP3 for uploading_


## gmupload

Supports **.mp3**, **.flac**, **.m4a**, **.ogg***

Args         |  Description
-------------|-----------
-h, --help   |  Show help message
-c, --cred   |  Specify oauth credential file name to use/create<br>(Default: "oauth")
-l, --log    |  Enable gmusicapi logging
-m, --match  |  Enable scan and match
-e, -exclude |  Exclude file paths matching a Python regex pattern<br>This option can be set multiple times
-d, --dry-run|  Output list of songs that would be uploaded and excluded
-q, --quiet  |  Don't output status messages<br>-l,--log will display gmusicapi warnings<br>-d,--dry-run will display song list
input        |  Files, directories, or glob patterns to upload<br>Defaults to current directory if omitted

**Example:** ``gmupload.py -m /path/to/music /other/path/to/music.mp3 /another/path/to/*.flac``

\* _Non-MP3 files are transcoded with avconv to 320kbps MP3 for uploading_
