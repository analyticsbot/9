class ProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta['proxy'] = "http://189.219.102.253:10000"
