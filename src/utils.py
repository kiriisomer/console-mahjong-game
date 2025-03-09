

def DEBUG(*args):
    with open("debug.txt", "a") as f:
        f.write(" ".join(map(str, args)) + "\n")

