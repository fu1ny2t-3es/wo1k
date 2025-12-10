#!/usr/bin/python3
#
# Copyright (c) 2025 secfurry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from PIL import Image
from os import makedirs
from struct import pack
from imagehash import dhash
from hashlib import md5, sha256
from io import BytesIO, StringIO
from sys import stderr, exit, argv
from argparse import ArgumentParser
from telethon.sync import TelegramClient
from telethon.tl.types import PeerUser, PeerChannel, PeerChat
from telethon.tl.types import Channel, MessageMediaDocument, MessageMediaPhoto, MessageMediaWebPage, MessageMediaPoll
from os.path import join, exists, isdir, expanduser, expandvars
from datetime import datetime
import time
import random


def _main():
    p = ArgumentParser()
    p.add_argument(
        "-s",
        "--state",
        type=str,
        dest="state",
        action="store",
        default="deduper",
        required=False,
    )
    p.add_argument(
        "-i",
        "--app-id",
        type=int,
        dest="app_id",
        action="store",
        required=True,
    )
    p.add_argument(
        "-n",
        "--app-hash",
        type=str,
        dest="app_hash",
        action="store",
        required=True,
    )
    p.add_argument(
        type=str,
        dest="name",
        nargs=1,
        action="store",
    )
    a = p.parse_args()
    del p
    if len(a.name) != 1:
        raise ValueError("name cannot be empty")
    n = a.name[0]
    if not isinstance(n, str) or len(n) == 0:
        raise ValueError("name cannot be empty")
    if not isinstance(a.app_hash, str) or len(a.app_hash) == 0:
        raise ValueError("app_hash cannot be empty")
    d = None
    s = a.state
    with TelegramClient(s, a.app_id, a.app_hash) as x:
        c = _find_channel(x, n)
        if c is None:
            raise ValueError(f'no Channel or Group with name "{n}" found')
        print(
            f'Found {'Channel' if c.is_channel else 'Group'} "{c.name}" with ID {c.id}..'
        )
        print(datetime.now())
        _remove_dupes(x, c)
        print(datetime.now())
        del c
    del s, d, n


def _usage(*_):
    print(USAGE.format(bin=argv[0]))
    exit(2)


def _get_user(m):
    if isinstance(m.from_id, PeerChat):
        return m.from_id.chat_id
    elif isinstance(m.from_id, PeerUser):
        return m.from_id.user_id
    elif isinstance(m.from_id, PeerChannel):
        return m.from_id.channel_id
    return None


def _find_channel(client, name):
    for i in client.get_dialogs():
        if not i.is_channel and not i.is_group:
            continue
        if i.name != name:
            continue
        return i
    return None


def _remove_dupes(client, channel):
    t_doc, t_photo, t_webpage = set(), set(), set()
    o = 1

    for i in client.iter_messages(channel.id, reverse=False):
        time.sleep(random.uniform(0.001, 0.01))
        o += 1
        if o % 100 == 0:
            print(o, flush=True)

        if not i.media:
            continue

        if type(i.media) is MessageMediaDocument:
            new_id = int(i.media.document.id)

            if new_id not in t_doc:
                t_doc.add(new_id)
            else:
                print('dupe doc ' + str(i.id))
                i.delete()

        elif type(i.media) is MessageMediaPhoto:
            new_id = int(i.media.photo.id)

            if new_id not in t_photo:
                t_photo.add(new_id)
            else:
                print('dupe photo ' + str(i.id))
                i.delete()

        elif type(i.media) is MessageMediaWebPage:
            new_id = int(i.media.webpage.id)

            if new_id not in t_webpage:
                t_webpage.add(new_id)
            else:
                print('dupe webpage ' + str(i.id))
                i.delete()

        elif type(i.media) is MessageMediaPoll:
            i.delete()

        else:
            print(i.media)


    with open('document.txt', 'w') as myfile:
        for line in t_doc:
            print(line, file=myfile)  # Python 3.x

    with open('photo.txt', 'w') as myfile:
        for line in t_photo:
            print(line, file=myfile)  # Python 3.x

    with open('webpage.txt', 'w') as myfile:
        for line in t_webpage:
            print(line, file=myfile)  # Python 3.x



if __name__ == "__main__":
    try:
        _main()
    except Exception as err:
        print(f"Error during runtime: {err}!", file=stderr)
        exit(1)
