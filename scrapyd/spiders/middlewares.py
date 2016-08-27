class ProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta['proxy'] = "http://45.32.131.88:8080"