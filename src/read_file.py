import sys

class Video(object):
    """docstring for Video."""
    def __init__(self, identifier, size):
        super(Video, self).__init__()
        self.identifier = identifier
        self.size = size
        self.requests = {}

    def addRequest(self, request):
        self.requests[request.identifier] = request

class Endpoint(object):
    """docstring for Endpoint."""
    def __init__(self, identifier, latency, ncaches):
        super(Endpoint, self).__init__()
        self.identifier = identifier
        # latency to datacenter
        self.latency = latency
        self.ncaches = ncaches
        self.caches = {}
        self.requests = {}

    def addCache(self, cache):
        self.caches[cache.identifier] = cache

    def addRequest(self, request):
        self.requests[request.identifier] = request

class Cache(object):
    """docstring for Cache."""
    def __init__(self, identifier):
        super(Cache, self).__init__()
        self.identifier = identifier
        self.endpoints = {}

    def addEndpoint(self, endpoint, latency):
        # latency to endpoint
        self.endpoints[endpoint.identifier] = {"obj": endpoint, "latency": latency}
        endpoint.addCache(self)


class Request(object):
    """docstring for Request."""
    def __init__(self, identifier, video, endpoint, amount):
        super(Request, self).__init__()
        self.identifier = identifier
        self.video = video
        self.endpoint = endpoint
        self.amount = amount

        video.addRequest(self)
        endpoint.addRequest(self)


def print_infos(nvideos, nendpoints, nrequests, ncache, ncachecap):
    print(
"""Video number: %d
Endpoints number: %d
Requests number: %d
Cache servers number: %d
Cache server capacity: %d""" % (
    nvideos, nendpoints, nrequests, ncache, ncachecap
    )
)

def main(args):
    with open(args[1], 'rb') as f:
        lines = f.readlines()
        nvideos, nendpoints, nrequests, ncache, ncachecap = map(
            int, lines[0].split()
        )
    print_infos(nvideos, nendpoints, nrequests, ncache, ncachecap)

    videos = {}
    i = 0
    for size in lines[1].split():
        videos[i] = Video(i, int(size))
        i += 1

    print("\nRetrieval")
    print("Videos number retrieved %d" % (len(videos.values())))

    endpoints = {}
    caches = {}
    i = 0
    index = 2
    while i < nendpoints:
        latency_datacenter, ncaches = map(int, lines[index].split())
        endpoint = Endpoint(i, latency_datacenter, ncaches)
        endpoints[i] = endpoint
        index += 1
        j = 0
        while j < ncaches:
            identifier, latency_endpoint = map(int, lines[index].split())
            if identifier not in caches.keys():
                caches[identifier] = Cache(identifier)
            caches[identifier].addEndpoint(endpoint, latency_endpoint)
            index += 1
            j += 1
        i += 1

    print("Number of endpoints: %d" % (len(endpoints.values())))
    print("Number of caches: %d" % (len(caches.values())))

    requests = {}
    i = 0
    while i < nrequests:
        video_id, endpoint_id, amount = map(int, lines[index].split())
        requests[i] = Request(
            i, videos[video_id], endpoints[endpoint_id], amount
        )
        index += 1
        i += 1

    print("Number of requests: %d" % len(requests))


if __name__ == "__main__":
    main(sys.argv)
