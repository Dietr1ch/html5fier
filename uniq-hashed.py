#!/usr/bin/python3

import sys

seen = set()
for url in sys.stdin:
    if url not in seen:
        seen.add(url)
        print(url.strip())
