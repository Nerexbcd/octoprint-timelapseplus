import hashlib
import os
import subprocess


class Video:
    def __init__(self, path, parent, settings):
        self.PARENT = parent
        self.CACHE_CONTROLLER = parent.CACHE_CONTROLLER
        self._settings = settings

        self.FILE = os.path.splitext(os.path.basename(path))[0]
        self.THUMBNAIL = path + '.thumb.jpg'
        self.PATH = path
        self.TIMESTAMP = os.path.getmtime(path)
        self.SIZE = os.path.getsize(path)
        self.MIMETYPE = 'video/mp4'
        self.ID = self.getId()
        self.LENGTH = self.getVideoLength()
        self.EXTENSION = os.path.splitext(path)[1][1:].lower()

    def getVideoLength(self):
        cacheId = ['video', 'length', self.ID]
        if self.CACHE_CONTROLLER.isCached(cacheId):
            cv = self.CACHE_CONTROLLER.getString(cacheId)
            return int(cv)

        try:
            ffprobePath = self._settings.get(["ffprobePath"])
            cmd = [ffprobePath, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', self.PATH]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            if result.returncode != 0:
                raise Exception('FFPROBE Return Code != 0')

            output = result.stdout.strip()
            s = float(output)
            ms = int(s * 1000)

            self.CACHE_CONTROLLER.storeString(cacheId, str(ms))

            return ms

        except Exception as e:
            return 0

    def delete(self):
        os.remove(self.PATH)
        if os.path.exists(self.THUMBNAIL):
            os.remove(self.THUMBNAIL)

    def getJSON(self):
        import flask
        data = flask.request.get_json()
        return dict(
            id=self.ID,
            file=self.FILE,
            size=self.SIZE,
            length=self.LENGTH,
            timestamp=self.TIMESTAMP,
            extension=self.EXTENSION,
            thumbnail=data["webcamUrlPath"] + '/plugin/timelapseplus/thumbnail?type=video&id=' + self.ID,
            url=data["webcamUrlPath"] + '/plugin/timelapseplus/download?type=video&id=' + self.ID
        )

    def getId(self):
        c = self.PATH + str(self.TIMESTAMP) + str(self.SIZE)
        return hashlib.md5(c.encode('utf-8')).hexdigest()
