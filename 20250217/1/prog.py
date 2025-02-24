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
    for head in Path(sys.argv[1]).glob(f".git/refs/heads/{sys.argv[2]}"):
        with open(head, "rb") as f:
            com = f.read().decode()
            print("ищем", com)
    for store in Path(sys.argv[1]).glob(".git/objects/??/*"):
        #print("store", store)
        Id = basename(dirname(store)) + basename(store)
        if Id + "\n" == com:
            with open(store, "rb") as f:
                obj = zlib.decompress(f.read())
                header, _, body = obj.partition(b'\x00')
                kind, size = header.split()
                out = body.decode()
                print(out)
        """continue
        print("Id", "kind.decode()", Id, kind.decode())
        if kind == b'tree':
            tail = body
            while tail:
                treeobj, _, tail = tail.partition(b'\x00')
                tmode, tname = treeobj.split()
                num, tail = tail[:20], tail[20:]
                print(f"{SHIFT}{tname.decode()} {tmode.decode()} {num.hex()}")
        elif kind == b'commit':
            out = body.decode().replace('\n', '\n' + SHIFT)
            print(f"{SHIFT}{out}")"""
