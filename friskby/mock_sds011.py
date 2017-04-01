class MockSDS011(object):

    def __init__(self, device_url):
        self.device_url = device_url

    def read(self):
        return (10.0, 2.5)
