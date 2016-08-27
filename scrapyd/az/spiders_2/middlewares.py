class ProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta['proxy'] = "http://69.147.248.50:3128"