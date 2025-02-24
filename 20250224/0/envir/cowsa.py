import cowsay
import sys

with open("./max-payne.cow") as f:
    m = f.read()
    print(cowsay.cowsay(sys.argv[1], cowfile=m))
