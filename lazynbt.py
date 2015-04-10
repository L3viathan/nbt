import nbt
import os

class File(object):
    def __init__(self, filename, pointer=None):
        self.filename = filename
        self.cache = None
        self.pointer = pointer if pointer else []
        self.mtime = 0
    def _read(self):
        mtime = os.path.getmtime(self.filename)
        if mtime > self.mtime:
            self.cache = nbt.read(self.filename)
            self.mtime = mtime
    def _write(self):
        nbt.write(self.filename, self.cache)
    def __repr__(self):
        return "lazynbt.File('" + self.filename + "', " + str(self.pointer) + ")"
    def prettyprint(self):
        self._read()
        ret = self.cache
        for thing in self.pointer:
            ret = ret[thing]
        ret.prettyprint()
    def __str__(self):
        self._read()
        ret = self.cache
        for thing in self.pointer:
            ret = ret[thing]
        return str(ret)
    def __getitem__(self, item):
        self._read()
        return File(self.filename, self.pointer + [item])
    def __setitem__(self, item, value):
        self._read()
        obj = self.cache
        for thing in self.pointer:
            obj = obj[thing]
        obj[item] = value
        self._write()
    def value(self):
        self._read()
        ret = self.cache
        for thing in self.pointer:
            ret = ret[thing]
        return ret
