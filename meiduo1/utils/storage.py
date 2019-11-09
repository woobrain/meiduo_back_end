from django.core.files.storage import Storage


class FastDFSStorage(Storage):
    # def __init__(self):

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        pass

    def url(self,name):

        return 'http://192.168.179.130:8888/' + name

