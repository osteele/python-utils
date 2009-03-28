__author__ = "Oliver Steele <steele@osteele.com>"
__copyright__ = "Copyright 2009 by Oliver Steele."
__license__ = "Python License"
__version__ = '0.1'

import os

class SegmentedFile:
    # A read-only file-like object that aggregates a series of file
    # chunks
    def __init__(self, files):
        self.files = [open(file) if type(file) is str else file
                      for file in files]
        self.closed = False
        self.mode = 'r'
        self.__setfile(0)

    def close(self):
        for file in self.files:
            file.close()
        self.closed = True

    def __setfile(self, i):
        self._index = i
        file = self.files[i] if i < len(self.files) else None
        self._file = file
        self.name = self._file and file.name
        if self._file:
            self._file.seek(0)
        return file

    def __nextfile(self):
        if self._index < len(self.files):
            self.__setfile(self._index + 1)

    def __read(self, size, methodname):
        chunks = []
        if size < 0: size = None
        while size is None or size > 0:
            if not self._file: break
            chunk = getattr(self._file, methodname)(size or -1)
            if chunk:
                if size: size -= len(chunk)
                chunks.append(chunk)
                if methodname == 'readline' and chunk and chunk[-1] == '\n':
                    break
            else:
                self.__nextfile()
        return ''.join(chunks)

    def read(self, size=None):
        return self.__read(size, 'read')

    def readline(self, size=None):
        return self.__read(size, 'readline')

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_CUR:
            offset += self.tell()
            whence = os.SEEK_SET
            # fall through
        if whence == os.SEEK_END:
            offset = self.__sizeuntil() - offset
            whence = os.SEEK_SET
            # fall through
        if whence == os.SEEK_SET:
            for i in range(len(self.files)):
                if offset < 0: break
                file = self.__setfile(i)
                file.seek(0, os.SEEK_END)
                n = file.tell()
                if offset < n:
                    return file.seek(offset)
                offset -= n
            raise IOError, 22, ("Invalid argument")

    def tell(self):
        return __sizeuntil(self._file)

    def __sizeuntil(self, stopfile=None):
        offset = 0
        for file in self.files:
            saved_offset = file.tell()
            if file is stopfile:
                return offset + saved_offset
            file.seek(0, os.SEEK_END)
            offset += file.tell()
            file.seek(saved_offset)
        return offset
        

