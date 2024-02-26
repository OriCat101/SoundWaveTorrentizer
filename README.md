# The Idea

## Description:

A script that can analyse the files and generates a media info table and optionally uploads the spectrogram.

It outputs bbcode table into your clipboard for use on various forums.

### Example output:

![example](/doc/images/exampleoutput.png)

## Usage guide

### Create your config

use [example.json](conf/example.json) as a template and work from there.

> [!NOTE]
> not all of the arguments are required/implemented yet, the ones that aten't are marked as such.
> All comments have to be removed from the file. 

### Using the Script

There are two main ways how this script can be run and used.

you can eiter just run the script without any arguments, then you'll have a somewhat *"guided"* experience.

### CLI arguments

*big thanks to: [@GalaxyBalaxy](https://github.com/GalaxyBalaxy) for implementing these <3*

The following CLI arguments are available to the User:

- `-p`, `--paths`: A list of paths to the album folder or files to be processed. This argument is required, and at least one path must be provided. The paths can be separated by spaces.
- `-s`, `--spectrogram`: A boolean flag indicating whether to upload spectrogram images along with the audio files.
  Default value: `False`.
- `-t`, `--save-torrent`: The path where the generated torrent file should be saved. If not specified, the default behavior is to save the torrent file in the same directory as the audio files.
- `-c`, `--config`: The name of the tracker configuration to use for generating the torrent file. If not specified, no torrent can be generated
- `-f`, `--format`: The format of the table to display the album information. Valid values are `bbcode` and `markdown`.
  Default value: `bbcode`.

## Smol bits:

- [x] analyse quality of the album (avg. Bitrate etc.)
- [x] Generate a spectrograph
- [x] upload spectrograph
- [x] output bbCode
- [x] generate .torrent
- [x] add support for Markdown
- [x] add support for multi dis albums/collections
- [ ] Display which album is currently being analyzed
- [x] write arguments doc
- [ ] Basic console UI
- [ ] Write usage guide
- [ ] (advanced) upload using UNIT3D api

## Contribution

Missing features? Want to Implement a new API? Want to support other file Types?
Heck yeh! go for it, Contribution is encuraged and welcome

## Disclaimer:

~~The code runs and does it is job but it isn't what id call good code, at least rn~~

Now I'd say it is at least decent code :)
