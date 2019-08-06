from volapi import Room
import argparse
import requests
from tqdm import tqdm
import os
import string
import random
import config
from datetime import datetime, timedelta
import time

kill = False


class VolaDL(object):
    def __init__(self, args):
        """Initialize Object"""
        self.headers = config.HEADERS
        self.cookies = config.COOKIES
        self.room = args[0]
        self.password = args[1]
        if args[2] is None:
            self.downloader = config.DOWNLOADER
        else:
            self.downloader = args[2]
        if args[3] is None:
            self.logger = config.LOGGER
        else:
            self.logger = args[3]

        self.alive = True

        self.download_all = config.DOWNLOAD_ALL_ON_ROOM_ENTER
        self.duplicate = not config.ALLOW_DUPLICATES
        self.continue_running = config.CONTINUE_RUNNING
        self.max_file_size = config.MAXIMUM_FILE_SIZE

        self.download_path = config.DOWNLOAD_PATH + self.room
        self.log_path = config.LOG_PATH + self.room
        self.refresh_time = datetime.now() + timedelta(days=1)
        self.counter = 1
        self.user_whitelist = []
        self.user_blacklist = []
        self.filename_whitelist = []
        self.filename_blacklist = []
        self.filetype_whitelist = []
        self.filetype_blacklist = []

        if self.config_check():
            self.alive = False
            global kill
            kill = True
            print('### YOU CAN NOT USE A BLACKLIST AND A WHITELIST FOR THE SAME FILTER.')
        else:
            self.listen = self.create_room()

    def dl(self):
        """Main method that gets called at the start"""

        def onfile(f):
            """Listener on new files in the room"""
            url = f.url
            uploader = f.uploader
            file_size = '{0:.4f}'.format(f.size / 1048576)
            print('### NEW FILE - URL : {} - UPLOADER: {} - FILESIZE: {} MB'.format(url, uploader, file_size))
            if not self.max_file_size == -1 and f.size / 1048576 >= self.max_file_size:
                print('File is too big to download.')
            elif self.file_check(f):
                self.single_file_download(url, uploader)
            else:
                print('File got filtered out.')

        def ontime(t):
            """React to time events emitted by volafile socket connection, used for maintenance"""
            if datetime.now() > self.refresh_time:
                # if the refresh_time is now -> close the bot
                self.close()
                return t
            # check for connections
            if self.listen:
                if not self.listen.connected:
                    self.close()
            return t

        def onmessage(m):
            """React to and log chat messages"""
            self.log_room(m)

        if self.alive:
            global kill

            if self.download_all and self.downloader:
                print("Downloading room on enter")
                duplicate_temp = self.duplicate
                self.duplicate = True
                self.download_room()
                self.duplicate = duplicate_temp
            if self.continue_running:
                if self.downloader:
                    self.listen.add_listener("file", onfile)
                if self.logger:
                    self.listen.add_listener("chat", onmessage)
                if self.downloader or self.logger:
                    self.listen.add_listener("time", ontime)
                    self.listen.listen()
                else:
                    print('### You need to activate either LOGGER or DOWNLOADER for the bot to continue running')
                    kill = True
            else:
                kill = True

    def log_room(self, msg):
        if msg.nick == 'News' and msg.system:
            return False
        time_now = datetime.now()
        prefix = VolaDL.prefix(msg)
        if os.path.exists(self.log_path):
            temp_path = self.log_path + '/'
        else:
            temp_path = VolaDL.create_folder(self.log_path)
        file_name = time_now.strftime("[%Y-%m-%d]") + "[" + self.room + "].txt"
        path = str(temp_path) + str(file_name)
        if not os.path.isfile(path):
            fl = open(path, "w+")
        else:
            fl = open(path, "a")

        log_msg = '[{}][{}][{}][{}]\n'.format(str(time_now.strftime("%Y-%m-%d--%H:%M:%S")), prefix, msg.nick, str(msg))
        print("### Writing to log: " + log_msg[0:-1])
        fl.write(log_msg)
        fl.close

    def download_room(self):
        """Download the whole room on enter"""
        time.sleep(2)
        file_list = self.listen.files
        for f in file_list:
            url = f.url
            uploader = f.uploader
            file_size = '{0:.4f}'.format(f.size / 1048576)
            print('### NEXT FILE:')
            print('URL : {} - UPLOADER: {} - FILESIZE: {} MB'.format(url, uploader, file_size))
            if not self.max_file_size == -1 and f.size / 1048576 >= self.max_file_size:
                print('File is too big to download.')
            elif self.file_check(f):
                self.single_file_download(url, uploader)
            else:
                print('File got filtered out.')
        print('### ### ###')
        print('Downloading the room has been finished, leave this running to download new files/log or quit.')
        print('### ### ###')

    def download_file(self, url, file_name=None):
        """ Downloads a file from volafile and shows a progress bar """
        chunk_size = 1024
        try:
            r = requests.get(url, stream=True, headers=self.headers, cookies=self.cookies)
            r.raise_for_status()
            if not r:
                return False
            total_size = int(r.headers.get("content-length", 0))
            with open(file_name + ".part", "wb") as fl:
                for data in tqdm(iterable=r.iter_content(chunk_size=chunk_size), total=total_size / chunk_size,
                                 unit="KB", unit_scale=True):
                    fl.write(data)
            os.rename(file_name + ".part", file_name)
            return True
        except Exception as ex:
            print("[-] Error: " + str(ex))
            return False

    def single_file_download(self, url, upl):
        """Prepares a single file from vola for download"""
        if os.path.exists(self.download_path + '/' + upl):
            temp_path = self.download_path + '/' + upl + '/'
        else:
            temp_path = VolaDL.create_folder(self.download_path + '/' + upl)

        url_split = url.split('/')
        file_split = str(url_split[-1]).split('.')
        file_split_length = len(file_split[-1]) + 1
        download_path = temp_path + str(url_split[-1][0:-file_split_length]) + '.' + str(file_split[-1])

        if self.duplicate and os.path.isfile(download_path):
            print("File exists already!")
            return False
        elif os.path.isfile(download_path):
            download_path = temp_path + str(file_split[0]) + "-" + VolaDL.id_generator() + '.' + str(file_split[-1])
        print('[{}] Downloading to: {}'.format(self.counter, download_path))
        self.counter += 1
        return self.download_file(url, download_path)

    def config_check(self):
        """Checks filter configs for validity and prepares them for filtering"""
        if (config.USE_USER_BLACKLIST and config.USE_USER_WHITELIST) or (
                config.USE_FILENAME_BLACKLIST and config.USE_FILENAME_WHITELIST) or (
                config.USE_FILETYPE_BLACKLIST and config.USE_FILETYPE_WHITELIST):
            return (config.USE_USER_BLACKLIST and config.USE_USER_WHITELIST) or (
                    config.USE_FILENAME_BLACKLIST and config.USE_FILENAME_WHITELIST) or (
                           config.USE_FILETYPE_BLACKLIST and config.USE_FILETYPE_WHITELIST)
        else:
            if config.USE_USER_BLACKLIST:
                self.user_blacklist = config.USER_BLACKLIST
                self.config_list_prepare(self.user_blacklist)
            if config.USE_USER_WHITELIST:
                self.user_whitelist = config.USER_WHITELIST
                self.config_list_prepare(self.user_whitelist)
            if config.USE_FILETYPE_BLACKLIST:
                self.filetype_blacklist = config.FILETYPE_BLACKLIST
                self.config_list_prepare(self.filetype_blacklist)
            if config.USE_FILETYPE_WHITELIST:
                self.filetype_whitelist = config.FILETYPE_WHITELIST
                self.config_list_prepare(self.filetype_whitelist)
            if config.USE_FILENAME_BLACKLIST:
                self.filename_blacklist = config.FILENAME_BLACKLIST
                self.config_list_prepare(self.filename_blacklist)
            if config.USE_FILENAME_WHITELIST:
                self.filename_whitelist = config.FILENAME_WHITELIST
                self.config_list_prepare(self.filename_whitelist)
            return False

    def config_list_prepare(self, config_list):
        """Add #roomname to filters if needed"""
        for idx, item in enumerate(config_list):
            if '#' not in str(item):
                item = item + '#{}'.format(self.room)
                config_list[idx] = item

    def file_check(self, file):
        """Check file against filters"""
        if config.USE_USER_BLACKLIST:
            user_bool = True
            if str(file.uploader) + '#{}'.format(self.room) in self.user_blacklist:
                user_bool = False
        elif config.USE_USER_WHITELIST:
            user_bool = False
            if str(file.uploader) + '#{}'.format(self.room) in self.user_whitelist:
                user_bool = True
        else:
            user_bool = True

        if config.USE_FILENAME_BLACKLIST:
            filename_bool = True
            for item in self.filename_blacklist:
                if item.lower().split('#')[0] in str(file.name).lower() and '#{}'.format(self.room) in item:
                    filename_bool = False
        elif config.USE_FILENAME_WHITELIST:
            filename_bool = False
            for item in self.filename_whitelist:
                if item.lower().split('#')[0] in str(file.name).lower() and '#{}'.format(self.room) in item:
                    filename_bool = True
        else:
            filename_bool = True

        if config.USE_FILETYPE_BLACKLIST:
            filetype_bool = True
            if str(file.filetype) + '#{}'.format(self.room) in self.filetype_blacklist:
                filetype_bool = False
        elif config.USE_FILETYPE_WHITELIST:
            filetype_bool = False
            if str(file.filetype) + '#{}'.format(self.room) in self.filetype_whitelist:
                filetype_bool = True
        else:
            filetype_bool = True

        return user_bool and filename_bool and filetype_bool

    def create_room(self):
        """return a volapi room"""
        if config.VOLAFILE_USER == '':
            vola_user = 'downloader'
        else:
            vola_user = config.VOLAFILE_USER
        if self.password == '*':
            r = Room(name=self.room, user=vola_user)
        elif self.password[0:4] == '#key':
            r = Room(name=self.room, user=vola_user, key=self.password[4:])
        else:
            r = Room(name=self.room, user=vola_user, password=self.password)
        if config.VOLAFILE_USER_PASSWORD == '':
            return r
        else:
            vola_pass = config.VOLAFILE_USER_PASSWORD
            time.sleep(1)
            try:
                r.user.login(vola_pass)
                time.sleep(1)
            except RuntimeError:
                print('### LOGIN FAILED, PLEASE CHECK YOUR CONFIG BEFORE USING THE BOT')
                self.alive = False
                global kill
                kill = True
                return r
            print('### USER LOGGED IN')
            cookie_jar = r.conn.cookies
            cookies_dict = {}
            for cookie in cookie_jar:
                if "volafile" in cookie.domain:
                    cookies_dict[cookie.name] = cookie.value
            self.cookies = {**self.cookies, **cookies_dict}
            return r

    def close(self):
        """only closes the current session, afterwards the downloader reconnects"""
        print("Closing current instance")
        self.alive = False
        self.listen.close()
        del self.listen
        return ""

    @staticmethod
    def create_folder(new_folder):
        """creates a new folder"""
        new_path = new_folder
        try:
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                print('Created directory: ' + new_path)
                return str(new_path + '/')
        except OSError:
            print('Error: Creating directory. ' + new_path)
            return 'Error'

    @staticmethod
    def id_generator(size=7, chars=string.ascii_uppercase + string.digits):
        """returns an id"""
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def prefix(msg):
        prefix = ''
        if msg.purple:
            prefix += "@"
        if msg.owner:
            prefix += "$"
        if msg.janitor:
            prefix += "~"
        if msg.green:
            prefix += "+"
        if msg.system:
            prefix += "%"
        return prefix


def parse_args():
    """Parses user arguments"""
    parser = argparse.ArgumentParser(
        description="volafile downloader",
        epilog="Pretty meh"
    )
    parser.add_argument('--room', '-r', dest='room', type=str, required=True,
                        help='Room name, as in https://volafile.org/r/ROOMNAME')
    parser.add_argument('--passwd', '-p', dest='passwd', type=str,
                        default="*",
                        help='Room password to enter the room.')
    parser.add_argument('--downloader', '-d', dest='downloader', type=str,
                        default="None",
                        help='Do you want to download files -> [True/False]')
    parser.add_argument('--logger', '-l', dest='logger', type=str,
                        default="None",
                        help='Do you want to log the room -> [True/False]')
    return parser.parse_args()


def main():
    """Main method"""
    global kill
    args = parse_args()
    if args.downloader == "True":
        downloader = True
    elif args.downloader == "False":
        downloader = False
    else:
        downloader = None
    if args.logger == "True":
        logger = True
    elif args.logger == "False":
        logger = False
    else:
        logger = None

    lister = [args.room, args.passwd, downloader, logger]
    while not kill:
        v = VolaDL(lister)
        v.dl()


def main_callable(room, passwd='*', downloader=None, logger=None):
    """Callable main method with arguments"""
    global kill
    lister = [room, passwd, downloader, logger]
    while not kill:
        v = VolaDL(lister)
        v.dl()


if __name__ == "__main__":
    main()
