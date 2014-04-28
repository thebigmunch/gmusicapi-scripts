Usage
=====

## General

``script.py [options] [input/output]``

During the first run of the scripts, you will be given a link to authorize the application with Google Music if necessary. Paste that link in your browser and click Allow. Enter the given code into the terminal prompt.


## gmsync

```
gmsync.py up [-e PATTERN]... [options] [<input>...]
gmsync.py down [-f FILTER]... [options] [<output>]
gmsync.py [-e PATTERN]... [options] [<input>...]
```

Supports **.mp3**, **.flac**, **.m4a**, **.ogg***

Options                | Description
-----------------------|-----------
-h, --help             | Show help message
-c, --cred             | Specify oauth credential file name to use/create<br>(Default: "oauth")
-U ID --uploader-id ID | A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').<br>This should only be provided when the default does not work.
-l, --log              | Enable gmusicapi logging
-m, --match            | Enable scan and match
-d, --dry-run          | Output list of songs that would be uploaded and excluded
-q, --quiet            | Don't output status messages<br>-l,--log will display gmusicapi warnings<br>-d,--dry-run will display song list
-e, -exclude           | Exclude file paths matching a Python regex pattern<br>This option can be set multiple times
-f, --filter           | Filter Google songs by field:value pair (e.g. "artist:Muse")*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-a, -all               | Songs must match all filter criteria<br>(Default: Songs can match any filter criteria)
input                  | Files, directories, or glob patterns to upload<br>Defaults to current directory if omitted
output                 | Output file or directory name which can include template patterns<br>Defaults to name suggested by Google Music in your current directory

Commands | Description
up       | 

**Examples:**

```
gmsync.py -m "/path/to/music" "/other/path/to/music.mp3" "/another/path/to/*.flac"
gmsync.py up -e "MyFolderName" "/path/to/music"
gmsync.py down -a -f 'artist:Muse' -f 'album:Black Holes' "/path/to/%artist%/%album%/%title%"
gmsync.py down -f 'artist:Muse|Modest Mouse' "/path/to/%artist%/%album%/%title%"
```


\* _Non-MP3 files are transcoded with avconv to 320kbps MP3 for uploading_


## gmupload

```
gmupload.py [-e PATTERN]... [options] [<input>...]
```

Supports **.mp3**, **.flac**, **.m4a**, **.ogg***

Options                |  Description
-----------------------|-----------
-h, --help             | Show help message
-c, --cred             | Specify oauth credential file name to use/create<br>(Default: "oauth")
-U ID --uploader-id ID | A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').<br>This should only be provided when the default does not work.
-l, --log              | Enable gmusicapi logging
-m, --match            | Enable scan and match
-d, --dry-run          | Output list of songs that would be uploaded and excluded
-q, --quiet            | Don't output status messages<br>-l,--log will display gmusicapi warnings<br>-d,--dry-run will display song list
-e, -exclude           | Exclude file paths matching a Python regex pattern<br>This option can be set multiple times
input                  | Files, directories, or glob patterns to upload<br>Defaults to current directory if omitted

**Examples:**

```
gmupload.py "/path/to/music" "/other/path/to/music.mp3" "/another/path/to/*.flac"
gmupload.py up -e "MyFolderName" "/path/to/music"
```

\* _Non-MP3 files are transcoded with avconv to 320kbps MP3 for uploading_


## gmdownload

```
gmdownload.py [-f FILTER]... [options] [<output>]
```

Options                | Description
-----------------------|-----------
-h, --help             | Show help message
-c, --cred             | Specify oauth credential file name to use/create<br>(Default: "oauth")
-U ID --uploader-id ID | A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').<br>This should only be provided when the default does not work.
-l, --log              | Enable gmusicapi logging
-d, --dry-run          | Output list of songs that would be uploaded and excluded
-q, --quiet            | Don't output status messages<br>-l,--log will display gmusicapi warnings<br>-d,--dry-run will display song list
-f, --filter           | Filter Google songs by field:value pair (e.g. "artist:Muse")*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-a, -all               | Songs must match all filter criteria<br>(Default: Songs can match any filter criteria)
output                 | Output file or directory name which can include template patterns<br>Defaults to name suggested by Google Music in your current directory

\* *Filter fields can be any of artist, title, album, or album_artist*

#### Output pattern replacements

Pattern       |  Field
--------------|-----------
%artist%      |  artist
%title%       |  title
%track%       |  tracknumber
%track2%      |  tracknumber (zero padded)
%album%       |  album
%date%        |  date
%genre%       |  genre
%albumartist% |  albumartist
%disc%        |  discnumber

**Examples:**

```
gmdownload.py -a -f 'artist:Muse' -f 'album:Black Holes' "/path/to/%artist%/%album%/%title%"
gmdownload.py -f 'artist:Muse|Modest Mouse' "/path/to/%artist%/%album%/%title%"
```
