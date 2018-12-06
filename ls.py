#!/usr/bin/env python3
import re
import sys
try:
    import ipfsapi
except ModuleNotFoundError:
    import ipfsApi


api = ipfsapi.connect('127.0.0.1', 5001)


indexed_hashes = set()
checkpoint = []
logger = False


def handle_refs(f, file_hash: str, level: int = 0) -> None:
    global logger
    refs = api.refs(file_hash)
    refs = filter(lambda x: x['Err'] == '', refs)
    refs = map(lambda x: x['Ref'], refs)
    for ref in refs:
        assert ref.startswith('Qm') or ref.startswith('zb2rh')
        if level >= len(checkpoint):
            logger = True
        if logger:
            handle_hash(f, ref, level)
            handle_refs(f, ref, level + 1)
        elif ref == checkpoint[level]:
            if level == len(checkpoint) - 1:
                logger = True
            handle_refs(f, ref, level + 1)


def handle_hash(f, file_hash: str, level: int = 0) -> None:
    if file_hash in indexed_hashes:
        return
    line = level * " " + file_hash
    print(line)
    f.write(line + "\n")
    indexed_hashes.add(file_hash)


def load_file(file_name: str):
    global checkpoint
    with open(file_name, "r") as f:
        while True:
            line = f.readline()
            if line == '':
                print(checkpoint)
                return checkpoint
            level = len(line) - len(line.lstrip())
            line = line.strip()
            if level < len(checkpoint):
                checkpoint = checkpoint[:level]
            checkpoint.append(line)
            indexed_hashes.add(line)


def main(root_hash, file_name):
    load_file(file_name)
    with open(file_name, "a+") as f:
        handle_refs(f, root_hash)


if __name__ == '__main__':
    # USAGE: python3 ls.py <file_name> <root_hash>
    # all arguments optional
    root_hash = 'QmT5NvUtoM5nWFfrQdVrFtvGfKFmG7AHE8P34isapyhCxX'
    file_name = 'wikipedia_results.txt'
    if len(sys.argv) >= 2:
        file_name = sys.argv[1]
    if len(sys.argv) >= 3:
        root_hash = sys.argv[2]
    main(root_hash, file_name)
