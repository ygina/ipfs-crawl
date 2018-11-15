#!/usr/bin/env python3
import json
import re
import subprocess
import time
from enum import Enum
from typing import Optional


indexed_hashes = set()


class IPFSCatError(Enum):
    DIRECTORY = 'Error: this dag node is a directory'
    WIRETYPE = 'Error: proto:'


def is_ascii(file_hash: str) -> Optional[str]:
    """Reads a line from the file, returning the line if and only if it's ascii"""
    try:
        process = subprocess.Popen(['ipfs', 'cat', file_hash, '--length', '1000'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        line = process.stdout.readline()
        if line == b'':
            line = process.stderr.readline()
        line.decode('ascii')
        return str(line)
    except UnicodeDecodeError:
        # not ascii
        return None
    finally:
        process.kill()


def handle_hash(file_hash: str) -> None:
    """Only handle hashes that:
    (1) have not been seen before
    (2) contain human-readable plain text
    """
    if file_hash in indexed_hashes:
        return
    indexed_hashes.add(file_hash)
    line: Optional[str] = is_ascii(file_hash)
    if line is None:
        return
    if IPFSCatError.DIRECTORY.value in line:
        print("Directory: {}".format(file_hash))
    elif IPFSCatError.WIRETYPE.value in line:
        print("WireType error: {}".format(file_hash))
    else:
        print("Straight ASCII: {}".format(file_hash))


def sniff_hashes(process: subprocess.Popen) -> None:
    """Sniff the DHT logs for requested file hashes"""
    while True:
        line = process.stderr.readline()
        if line == '':
            return
        regex = r'.*received provider <.*> for (.*) \(addrs'
        match = re.match(regex, str(line))
        if match:
            file_hash = match.groups()[0]
            handle_hash(file_hash)


def initialize_log() -> None:
    """Initialize log levels to gather relevant data"""
    subprocess.call(['ipfs', 'log', 'level', 'dht', 'info'])


if __name__ == '__main__':
    try:
        dhtlog = subprocess.Popen(['ipfs', 'daemon'], stderr=subprocess.PIPE)
        time.sleep(5)
        initialize_log()
        sniff_hashes(dhtlog)
    finally:
        dhtlog.kill()
