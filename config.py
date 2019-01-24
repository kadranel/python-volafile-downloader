# #### CONFIG VARIABLES
# Configure a path on your system to put the downloaded files. The files will get sorted by room and uploader.
# Make sure this path exists beforehand
DOWNLOAD_PATH = './'

# When starting the script the whole room gets downloaded -> True/False
DOWNLOAD_ALL_ON_ROOM_ENTER = True

# After entering the room downloader remains running and downloads new files when they get uploaded -> True/False
CONTINUE_DOWNLOADING_NEW_FILES = True

# When this is True files from the same user with the same filename get downloaded with an altered
# filename -> True/False
# Does not apply to the room entering downloads, there no duplicates will be stored
ALLOW_DUPLICATES = True

# Volafile user for downloading. Useful if you have volafile pro for a higher speed.
VOLAFILE_USER = ''
VOLAFILE_USER_PASSWORD = ''

# Maximum allowed size to download in MB -> unlimited if -1
MAXIMUM_FILE_SIZE = -1

# #### FILTERING OPTIONS
# All filters get stored as strings in lists. You can only use either a white- or a blacklist from each filter.
# If you want to specify filters for a certain room put #ROOMNAME behind the filter. (This works for all filters)
# ## USER FILTERING
# Example for this filtertype: USER_WHITELIST = ['zipbot', 'kad#gentoomen']
# This example allows all files of the user zipbot to be downloaded in all rooms and all files of the user kad to
# to be downloaded only in the room 'gentoomen' (https://volafile.org/r/gentoomen)
USE_USER_WHITELIST = False
USER_WHITELIST = []
USE_USER_BLACKLIST = False
USER_BLACKLIST = []

# ## FILENAME FILTERING
# Example for this filtertype: FILENAME_WHITELIST = ['hello', 'girl#gentoomen']
# This example will download all files with 'hello' in their filenames in all rooms and all files with girl in
# their filename only in the room 'gentoomen' (https://volafile.org/r/gentoomen)
USE_FILENAME_WHITELIST = False
FILENAME_WHITELIST = []
USE_FILENAME_BLACKLIST = False
FILENAME_BLACKLIST = []

# ## FILETYPE FILTERING
# possible filter options: video, image, other, audio
# Example for this filtertype: FILETYPE_WHITELIST = ['video', 'other#gentoomen']
# This example will download videos in all rooms and archives/textdocuments/other in the room 'gentoomen' only
USE_FILETYPE_WHITELIST = False
FILETYPE_WHITELIST = []
USE_FILETYPE_BLACKLIST = False
FILETYPE_BLACKLIST = []

# #### REQUESTS CONFIG
# should not be changed unless errors occur when downloading
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1"
}
COOKIES = {
    "allow-download": "1"
}
