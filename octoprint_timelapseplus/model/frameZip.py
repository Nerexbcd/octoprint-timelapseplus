import hashlib
import os
import zipfile
from contextlib import closing
from zipfile import ZipFile

from ..helpers.fileHelper import FileHelper


class FrameZip:
    def __init__(self, path, parent):
        self.PARENT = parent
        self.CACHE_CONTROLLER = parent.CACHE_CONTROLLER

        self.FILE = os.path.splitext(os.path.basename(path))[0]
        self.PATH = path
        self.TIMESTAMP = os.path.getmtime(path)
        self.SIZE = os.path.getsize(path)
        self.MIMETYPE = 'application/zip'
        self.ID = self.getId()
        self.FRAMES = self.countFrames()

    def delete(self):
        os.remove(self.PATH)

    def getThumbnail(self):
        zip = zipfile.ZipFile(self.PATH, 'r')
        nl = zip.namelist()
        img = zip.read(nl[-1])
        return img

    def getId(self):
        c = self.PATH + str(self.TIMESTAMP) + str(self.SIZE)
        return hashlib.md5(c.encode('utf-8')).hexdigest()

    def getJSON(self):
        import flask
        data = flask.request.get_json()
        return dict(
            id=self.ID,
            file=self.FILE,
            frames=self.FRAMES,
            size=self.SIZE,
            timestamp=self.TIMESTAMP,
            thumbnail=data["webcamUrlPath"] + '/plugin/timelapseplus/thumbnail?type=frameZip&id=' + self.ID,
            url=data["webcamUrlPath"] + '/plugin/timelapseplus/download?type=frameZip&id=' + self.ID
        )

    def countFrames(self):
        cacheId = ['frameZip', 'countFrames', self.ID]
        if self.CACHE_CONTROLLER.isCached(cacheId):
            cv = self.CACHE_CONTROLLER.getString(cacheId)
            return int(cv)

        try:
            count = 0
            with closing(ZipFile(self.PATH)) as archive:
                for aFile in archive.namelist():
                    if os.path.basename(aFile) != FileHelper.METADATA_FILE_NAME:
                        count += 1

            self.CACHE_CONTROLLER.storeString(cacheId, str(count))

            return count

        except Exception as e:
            return 0
