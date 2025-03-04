from time import sleep


def f():
    print("Hello, World! I am f.")
    sleep(1)
    return g()


def g():
    print("Hello, World! I am g.")
    sleep(1)
    return f()


if __name__ == "__main__":
    g()
