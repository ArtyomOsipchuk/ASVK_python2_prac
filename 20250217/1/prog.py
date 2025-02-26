#!/usr/bin/env python3
import zlib
from pathlib import Path
import glob
from os.path import basename, dirname
import sys

if len(sys.argv) == 2:
    for store in Path(sys.argv[1]).glob(".git/refs/heads/*"):
        Id = basename(store)
        print(Id)
elif len(sys.argv) == 3:
    for head in Path(sys.argv[1]).glob(f".git/logs/refs/heads/{sys.argv[2]}"):
        with open(head, "rb") as f:
            coms = f.read().decode().split("\n")[:-1]
        for commit in coms:
            com = commit.split()[1]
            print("TREE for commit", com)
            for store in Path(sys.argv[1]).glob(".git/objects/??/*"):
                Id = basename(dirname(store)) + basename(store)
                if Id == com:
                    with open(store, "rb") as f:
                        obj = zlib.decompress(f.read())
                        header, _, body = obj.partition(b'\x00')
                        kind, size = header.split()
                        tree = body.decode().split()[1]
                    break
            for store in Path(sys.argv[1]).glob(".git/objects/??/*"):
                Id = basename(dirname(store)) + basename(store)
                if Id == tree:
                    with open(store, "rb") as f:
                        obj = zlib.decompress(f.read())
                        header, _, body = obj.partition(b'\x00')
                        kind, size = header.split()
                        out = body
                    if kind == b'tree':
                        tail = body
                        while tail:
                            treeobj, _, tail = tail.partition(b'\x00')
                            tmode, tname = treeobj.split()
                            num, tail = tail[:20], tail[20:]
                            print(f"blob {num.hex()}\t{tname.decode()}")
                    print(f"tree {Id}\t{sys.argv[2]}")
