class SDS011(object):

    def __init__(self, usb):
        self.usb = usb

    def read(self):
        return (10, 25)

    @classmethod
    def is_mock(cls):
        return True
