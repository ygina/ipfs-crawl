#!/usr/bin/env python3
import json
import re
import subprocess
import time
import magic
from typing import Optional, Tuple


indexed_hashes = set()


def write(text: str):
    with open("ipfs_dht_results.txt", "a+") as f:
        f.write(text + "\n")
    print(text)


def sniff_hashes(process: subprocess.Popen) -> None:
    """Sniff the DHT logs for requested file hashes"""
    while True:
        line = process.stderr.readline()
        if line == b'':
            return
        regex = r'.*received provider <.*> for (.*) \(addrs'
        match = re.match(regex, str(line))
        if not match:
            continue
        file_hash = match.groups()[0]
        if file_hash in indexed_hashes:
            continue
        indexed_hashes.add(file_hash)
        write(file_hash)


def load_index_hashes() -> None:
    global indexed_hashes
    with open("ipfs_dht_results.txt", "r") as f:
        for line in f.read().split('\n'):
            if line == '':
                return
            file_hash = line.strip()
            indexed_hashes.add(file_hash)


def initialize_log() -> None:
    """Initialize log levels to gather relevant data"""
    subprocess.call(['ipfs', 'log', 'level', 'dht', 'info'])


if __name__ == '__main__':
    try:
        dhtlog = subprocess.Popen(['ipfs', 'daemon'], stderr=subprocess.PIPE)
        time.sleep(5)
        load_index_hashes()
        initialize_log()
        sniff_hashes(dhtlog)
    finally:
        # dhtlog.kill()
        pass
