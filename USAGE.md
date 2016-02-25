Usage
=====

- [General](#General)
- [Output pattern replacements](#Output pattern replacements)
- [gmsearch](#gmsearch)
- [gmdelete](#gmdelete)
- [gmsync](#gmsync)
- [gmupload](#gmupload)
- [gmdownload](#gmdownload)

## General

``script [options] [input/output]``

During the first run of the scripts, you will be given a link to authorize the application with Google Music if necessary. Paste that link in your browser and click Allow. Enter the given code into the terminal prompt.

## Output pattern replacements

Pattern       | Field
--------------|--------
%artist%      | artist
%title%       | title
%track%       | tracknumber
%track2%      | tracknumber (zero padded)
%album%       | album
%date%        | date
%genre%       | genre
%albumartist% | albumartist
%disc%        | discnumber
%suggested%   | Filename suggested by Google

## gmsearch

```
gmsearch (-h | --help)
gmsearch [options] [-f FILTER]... [-F FILTER]...
```

Options                      | Description
-----------------------------|--------------
-h, --help                   | Show help message
-u USERNAME, --user USERNAME | Your Google username or e-mail address
-p PASSWORD, --pass PASSWORD | Your Google or app-specific password
-I ID --android-id ID        | An Android device id.
-l, --log                    | Enable gmusicapi logging
-q, --quiet                  | Don't output status messages<br>With -l,--log will display gmusicapi warnings
-f, --include-filter         | Include Google songs by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-F, --exclude-filter         | Exclude Google songs by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-a, --all-includes           | Songs must match all include filter criteria
-A, --all-excludes           | Songs must match all exclude filter criteria
-y, --yes                    | Display results without asking for confirmation


## gmdelete

```
gmdelete (-h | --help)
gmdelete [options] [-f FILTER]... [-F FILTER]...
```

Options                      | Description
-----------------------------|--------------
-h, --help                   | Show help message
-u USERNAME, --user USERNAME | Your Google username or e-mail address
-p PASSWORD, --pass PASSWORD | Your Google or app-specific password
-I ID --android-id ID        | An Android device id.
-l, --log                    | Enable gmusicapi logging
-d, --dry-run                | Output list of songs that would be uploaded and excluded
-q, --quiet                  | Don't output status messages<br>With -l,--log will display gmusicapi warnings
-f, --include-filter         | Include Google songs by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-F, --exclude-filter         | Exclude Google songs by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-a, --all-includes           | Songs must match all include filter criteria
-A, --all-excludes           | Songs must match all exclude filter criteria
-y, --yes                    | Display results without asking for confirmation


## gmsync

```
gmsync (-h | --help)
gmsync up [-e PATTERN]... [-f FILTER]... [-F FILTER]... [options] [<input>]...
gmsync down [-e PATTERN]... [-f FILTER]... [-F FILTER]... [options] [<output>]
gmsync [-e PATTERN]... [-f FILTER]... [-F FILTER]... [options] [<input>]...
```

Supports **.mp3**, **.flac**, **.m4a**, **.ogg**
_Non-MP3 files are transcoded with ffmpeg/avconv to 320kbps MP3 for uploading_

Options                | Description
-----------------------|--------------
-h, --help             | Show help message
-c, --cred             | Specify oauth credential file name to use/create<br>(Default: "oauth")
-U ID --uploader-id ID | A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').<br>This should only be provided when the default does not work.
-l, --log              | Enable gmusicapi logging
-m, --match            | Enable scan and match
-d, --dry-run          | Output list of songs that would be uploaded and excluded
-q, --quiet            | Don't output status messages<br>With -l,--log will display gmusicapi warnings<br>With -d,--dry-run will display song list
--delete-on-success    | Delete successfully uploaded local files.
-R, --no-recursion     | Disable recursion when scanning for local files.<br>This is equivalent to setting --max-depth to 0.
--max-depth DEPTH      | Set maximum depth of recursion when scanning for local files.<br>Default is infinite recursion.<br>Has no effect when -R, --no-recursion set.
-e, -exclude           | Exclude file paths matching a Python regex pattern<br>This option can be set multiple times
-f, --include-filter   | Include Google songs (download) or local songs (upload) by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-F, --exclude-filter   | Exclude Google songs (download) or local songs (upload) by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-a, --all-includes     | Songs must match all include filter criteria
-A, --all-excludes     | Songs must match all exclude filter criteria
input                  | Files, directories, or glob patterns to upload<br>Defaults to current directory if omitted
output                 | Output file or directory name which can include template patterns<br>Defaults to name suggested by Google Music in your current directory

\* *Filter fields can be any of artist, title, album, or albumartist/album_artist*

Commands | Description
---------|-------------
up       | Sync local songs to Google Music. This is the default behavior.
down     | Sync Google Music songs to local computer.

**Examples:**

```
gmsync -m "/path/to/music" "/other/path/to/music.mp3" "/another/path/to/*.flac"
gmsync up -e 'MyFolderName' "/path/to/music"
gmsync up -f 'artist:Muse' "/path/to/music"
gmsync down -a -f 'artist:Muse' -f 'album:Black Holes' "/path/to/%artist%/%album%/%title%"
gmsync down -f 'artist:Muse|Modest Mouse' "/path/to/%artist%/%album%/%title%"
```


## gmupload

```
gmupload (-h | --help)
gmupload [-e PATTERN]... [-f FILTER]... [-F FILTER]... [options] [<input>]...
```

Supports **.mp3**, **.flac**, **.m4a**, **.ogg**
_Non-MP3 files are transcoded with ffmpeg/avconv to 320kbps MP3 for uploading_

Options                | Description
-----------------------|--------------
-h, --help             | Show help message
-c, --cred             | Specify oauth credential file name to use/create<br>(Default: "oauth")
-U ID --uploader-id ID | A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').<br>This should only be provided when the default does not work.
-l, --log              | Enable gmusicapi logging
-m, --match            | Enable scan and match
-d, --dry-run          | Output list of songs that would be uploaded and excluded
-q, --quiet            | Don't output status messages<br>With -l,--log will display gmusicapi warnings<br>With -d,--dry-run will display song list
--delete-on-success    | Delete successfully uploaded local files.
-R, --no-recursion     | Disable recursion when scanning for local files.<br>This is equivalent to setting --max-depth to 0.
--max-depth DEPTH      | Set maximum depth of recursion when scanning for local files.<br>Default is infinite recursion.<br>Has no effect when -R, --no-recursion set.
-e, -exclude           | Exclude file paths matching a Python regex pattern<br>This option can be set multiple times
-f, --include-filter   | Include local songs by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-F, --exclude-filter   | Exclude local songs by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-a, --all-includes     | Songs must match all include filter criteria
-A, --all-excludes     | Songs must match all exclude filter criteria
input                  | Files, directories, or glob patterns to upload<br>Defaults to current directory if omitted

\* *Filter fields can be any of artist, title, album, or albumartist/album_artist*

**Examples:**

```
gmupload "/path/to/music" "/other/path/to/music.mp3" "/another/path/to/*.flac"
gmupload -e 'MyFolderName' "/path/to/music"
gmupload -f 'artist:Muse' "/path/to/music"
```


## gmdownload

```
gmdownload (-h | --help)
gmdownload [-f FILTER]... [-F FILTER]... [options] [<output>
```

Options                | Description
-----------------------|--------------
-h, --help             | Show help message
-c, --cred             | Specify oauth credential file name to use/create<br>(Default: "oauth")
-U ID --uploader-id ID | A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').<br>This should only be provided when the default does not work.
-l, --log              | Enable gmusicapi logging
-d, --dry-run          | Output list of songs that would be uploaded and excluded
-q, --quiet            | Don't output status messages<br>With -l,--log will display gmusicapi warnings<br>With -d,--dry-run will display song list
-f, --include-filter   | Include Google songs by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-F, --exclude-filter   | Exclude Google songs by field:pattern filter (e.g. "artist:Muse").*<br>Values can be any valid [Python regex pattern](http://docs.python.org/2/library/re.html)<br>This option can be set multiple times
-a, --all-includes     | Songs must match all include filter criteria
-A, --all-excludes     | Songs must match all exclude filter criteria
output                 | Output file or directory name which can include template patterns<br>Defaults to name suggested by Google Music in your current directory

\* *Filter fields can be any of artist, title, album, or albumartist/album_artist*

**Examples:**

```
gmdownload -a -f 'artist:Muse' -f 'album:Black Holes' "/path/to/%artist%/%album%/%title%"
gmdownload -f 'artist:Muse|Modest Mouse' "/path/to/%artist%/%album%/%title%"
```

