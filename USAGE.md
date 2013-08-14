Usage
=====

## General

``script.py [args] [input]``

During the first run of the scripts, you will be given a link to authorize the application with Google Music if necessary. Paste that link in your browser and click Allow. Enter the given code into the terminal prompt.

## gmsync

Supports **.mp3**, **.flac**, **.m4a**, **.ogg***

Input can be any number/combination of directories, files, and glob patterns separated by a space. Directories will be scanned recursively. If omitted, your current directory will be used.

Args         |Description
-------------|-----------
-h, --help   |  show this help message and exit
-c, --cred   |  Specify oauth credential file name to use/create<br>(Default: "oauth")
-l, --log    |  Enable gmusicapi logging
-m, --match  |  Enable scan and match
-d, --dry-run|  Output list of songs that would be uploaded
-q, --quiet  |  Don't output status messages<br>-l,--log will display gmusicapi warnings<br>-d,--dry-run will display song list

**Example:** ``gmsync.py -m /path/to/music /other/path/to/music.mp3 /another/path/to/*.flac``


## gmupload

Supports **.mp3**, **.flac**, **.m4a**, **.ogg***

Input can be any number/combination of directories, files, and glob patterns separated by a space. Directories will be scanned recursively. If omitted, your current directory will be used.

Args         |Description
-------------|-----------
-h, --help   |  show this help message and exit
-c, --cred   |  Specify oauth credential file name to use/create<br>(Default: "oauth")
-l, --log    |  Enable gmusicapi logging
-m, --match  |  Enable scan and match
-d, --dry-run|  Output list of songs that would be uploaded
-q, --quiet  |  Don't output status messages<br>-l,--log will display gmusicapi warnings<br>-d,--dry-run will display song list

**Example:** ``gmupload.py -m /path/to/music /other/path/to/music.mp3 /another/path/to/*.flac``

\* _Non-MP3 files are transcoded with avconv to 320kbps MP3 for uploading_
