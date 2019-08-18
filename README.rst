=====================
Python Volafile Downloader
=====================

Tool for downloading from volafile.org rooms via volapi_. (Currently the downloader is working on volapi 5.17.0)

.. _volapi: https://github.com/volafiled/python-volapi
This downloader does not use webdrivers and selenium like volafile-downloader_ and instead uses a websocket connection over the API, which makes this implementation a lot more light-weight.

The downloader allows for blacklists/whitelists for uploaders, filename-search and filetypes. Furthermore you can create your own chat logs.

.. _volafile-downloader: https://github.com/the-okn3/volafile-downloader

Installation
------------

0) What do you need?
  a) Python 3.7
  b) pip
1) How to install
  a) Download the newest release of the downloader at https://github.com/kadranel/python-volafile-downloader/archive/1.1.5.zip or git clone this repository.
  b) Unzip and enter the folder with you favourite shell, then type:
::

    pip3 install -r requirements.txt

2) Edit the config.py to your liking. Check the comments in there for more information on what to change.


Start the downloader
------------
::

    python3 downloader.py -r ROOMID -p PASSWORD[OPTIONAL] -d DOWNLOADER[OPTIONAL] -l LOGGER[OPTIONAL]

a) ROOMID: https://volafile.org/r/ROOMID
b) PASSWORD: The room password if it exists
c) DOWNLOADER: Overwrite for DOWNLOADER in config.py -> True/False
d) LOGGER: Overwrite for LOGGER in config.py -> True/False

Example: You want to download all files from https://volafile.org/r/n7yc3pgw
::

    python3 downloader.py -r n7yc3pgw -d True

Other
------------
If you have any issues/questions just post a new issue. Otherwise feel free to share, improve, use and make it your own.
