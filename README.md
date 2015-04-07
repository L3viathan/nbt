# nbt
Parser and Serializer for Minecraft's binary format

## Usage

    $ python3
    >>> import nbt
    >>> f = nbt.read("level.dat")
    >>> f["Data"]["Player"]["Score"]
    TAG_Int("Score"): 292
    >>> f["Data"]["Player"]["Score"] = 300
    >>> f["Data"]["Player"]["Score"]
    TAG_Int("Score"): 300
    >>> nbt.write("level.dat", f)
    >>>

Alternatively, you can use the lazynbt approach, inspired by [lazyjson](https://github.com/fenhl/lazyjson): Instead of explicitly reading and writing, you just keep a reference to the file, which is read every time when it changed and written back to disk when the user makes changes.

    $ python3
    >>> import lazynbt
    >>> f = lazynbt.File("level.dat")
    >>> f["Data"]["Player"]["Score"]
    lazynbt.File("level.dat", ["Data", "Player", "Score"])
    >>> f["Data"]["Player"]["Score"].value()
    TAG_Int("Score"): 292
    >>> f["Data"]["Player"]["Score"] = 300
    >>>

## License
WTFPL, but attribution would be nice, and if you use it, please tell me.
