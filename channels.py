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
from telethon.tl.types import Channel, MessageMediaDocument, MessageMediaPhoto, MessageMediaWebPage
from os.path import join, exists, isdir, expanduser, expandvars
from datetime import datetime


USAGE = """Telegram Chat Text/File/Image/Video De-Duplicator

Usage: {bin} -i <app_id> -n <app_hash>

Required Arguments:
    -i           <app_id>   Telegram API "app_id" value.
    --app-id
    -n           <app_hash> Telegram API "app_hash" value.
    --app-hash

The app_id and app_hash values can be gerenerated via the Telegram API page at
https://my.telegram.org

On first run or when no state file is used, you will be asked for Telegram login
credentials. You may use the credentials of any account that has delete permission
for media in the target Telegram channel.

NOTE: YOU CANNOT USE BOT TOKENS FOR THIS!! Bots do NOT have the ability to list
channels.
"""


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
    a = p.parse_args()
    del p
    if not isinstance(a.app_hash, str) or len(a.app_hash) == 0:
        raise ValueError("app_hash cannot be empty")
    s = a.state
    print(datetime.now())
    with TelegramClient(s, a.app_id, a.app_hash) as x:
        with open('channels-0.txt', 'w', encoding='utf-8') as myfile:
            for i in x.get_dialogs():
                if not i.is_channel and not i.is_group:
                    continue

                if hasattr(i.message.peer_id, 'channel_id'):
                    print(str(i.message.peer_id.channel_id) + '\t' + i.name)
                    print(str(i.message.peer_id.channel_id) + '\t' + i.name, file=myfile)

                elif hasattr(i.message.peer_id, 'chat_id'):
                    print(str(i.message.peer_id.chat_id) + '\t' + i.name)
                    print(str(i.message.peer_id.chat_id) + '\t' + i.name, file=myfile)
    print(datetime.now())


if __name__ == "__main__":
    try:
        _main()
    except Exception as err:
        print(f"Error during runtime: {err}!", file=stderr)
        exit(1)
