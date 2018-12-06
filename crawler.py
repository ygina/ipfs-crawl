#!/usr/bin/env python3
import json
import re
import subprocess
import time
import magic
from tempfile import NamedTemporaryFile
from enum import Enum
from typing import Optional, Tuple


SUBDIR_LIMIT = 20


indexed_hashes = set()
wiki_hashes = set()


class IPFSCatError(Enum):
    DIRECTORY = 'Error: this dag node is a directory'
    WIRETYPE = 'Error: proto:'
    NONASCII = 'NotAscii'


def get_file_type(line: bytes) -> str:
    if b'mediawiki' in line:
        return 'Wikipedia?'
    f = NamedTemporaryFile()
    f.write(line)
    f.seek(0)
    return magic.from_file(f.name);


class FileHash:
    def __init__(self, file_hash: str):
        self.file_hash = file_hash
        self.count = 0

    def write(self, text: str) -> bool:
        with open("index_results.txt", "a+") as f:
            f.write(text + "\n")
        print(text)
        self.count += 1
        return self.count >= SUBDIR_LIMIT


    def readline(self, file_hash: str) -> Tuple[Optional[bytes], Optional[str]]:
        try:
            process = subprocess.Popen(['ipfs', 'cat', file_hash, '--length', '1000'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            line = process.stdout.read()
            if line == b'':
                line = process.stderr.readline()
                return (None, line.decode('ascii').strip())
            return (line, None)
        finally:
            process.kill()


    def handle_directory(self, dir_hash: str, indent: int = 0) -> bool:
        try:
            process = subprocess.Popen(['ipfs', 'refs', dir_hash], stdout=subprocess.PIPE)
            while True:
                line = process.stdout.readline()
                if line == b'':
                    return
                line = line.decode('ascii').strip()
                assert line.startswith('Qm') or line.startswith('zb2rh')
                if self.handle_hash(line, indent):
                    return True
            return False
        finally:
            process.kill()


    def handle_hash(self, file_hash: str, indent: int = 0) -> bool:
        # Check that the hash is not a repeaded and is not Wikipedia
        if file_hash in indexed_hashes:
            return
        if file_hash in wiki_hashes:
            return self.write(indent * " " + "(Wikipedia) {}".format(file_hash))
            return

        # Read a line and mark it as handled
        indexed_hashes.add(file_hash)
        line, err = self.readline(file_hash)

        # Handle directory and read errors
        if err is not None:
            if IPFSCatError.DIRECTORY.value in err:
                if self.write(indent * " " + "(DIR) {}".format(file_hash)):
                    return True
                return self.handle_directory(file_hash, indent + 2)
            elif IPFSCatError.WIRETYPE.value in err:
                return self.write(indent * " " + "(WireType) {}".format(file_hash))

        # Handle a regular file (might be Wikipedia still)
        if line is not None:
            file_type = get_file_type(line)
            return self.write(indent * " " + "({}) {}".format(file_type, file_hash))


    def handle(self):
        if self.handle_hash(self.file_hash):
            self.write('and more...')


def sniff_hashes(process: subprocess.Popen) -> None:
    """Sniff the DHT logs for requested file hashes"""
    while True:
        line = process.stderr.readline()
        if line == b'':
            return
        regex = r'.*received provider <.*> for (.*) \(addrs'
        match = re.match(regex, str(line))
        if match:
            file_hash = match.groups()[0]
            FileHash(file_hash).handle()


def load_index_hashes() -> None:
    global indexed_hashes
    with open("index_results.txt", "r") as f:
        for line in f.read().split('\n'):
            if line == '':
                return
            file_hash = line.split()[-1]
            indexed_hashes.add(file_hash)


def load_wiki_hashes() -> None:
    with open("ls_results.txt", "r") as f:
        for wiki_hash in f.read().split():
            wiki_hashes.add(wiki_hash)


def initialize_log() -> None:
    """Initialize log levels to gather relevant data"""
    subprocess.call(['ipfs', 'log', 'level', 'dht', 'info'])


if __name__ == '__main__':
    try:
        dhtlog = subprocess.Popen(['ipfs', 'daemon'], stderr=subprocess.PIPE)
        time.sleep(5)
        load_index_hashes()
        load_wiki_hashes()
        initialize_log()
        sniff_hashes(dhtlog)
    finally:
        # dhtlog.kill()
        pass
