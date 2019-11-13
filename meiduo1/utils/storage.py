from django.core.files.storage import Storage


class FastDFSStorage(Storage):
    # def __init__(self):

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        pass

    def url(self,name):

        return 'http://image.meiduo.site:8888/' + name

