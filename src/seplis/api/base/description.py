class Description(object):

    def __init__(self, text, title=None, url=None):
        '''

        :param text: str
        :param title: str
        :param url: str
        '''
        self.text = text
        self.title = title
        self.url = url

    def to_dict(self):
        return self.__dict__