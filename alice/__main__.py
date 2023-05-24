import uvloop
from alice.alice import Alice

if __name__ == "__main__":
    uvloop.install()
    Alice().run()
