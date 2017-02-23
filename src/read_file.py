import sys

class Video(object):
    """docstring for Video."""
    def __init__(self, identifier, size):
        super(Video, self).__init__()
        self.identifier = identifier
        self.size = size
        self.requests = {}
        self.best_score = -1.0

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


def lolbigsort(videos, endpoints, caches, requests, ncachecap):
    result = {}

    for endpoint_id, endpoint in endpoints.items():
        total = 0.0
        for cache_id, cache in endpoint.caches.items():
            try:
                total += cache.endpoints[endpoint_id]["latency"]
            except:
                print(cache.endpoints.keys())

        total = float(total) / float(len(endpoint.caches.values()))

        for cache_id, cache in endpoint.caches.items():
            if cache_id not in result.keys():
                result[cache_id] = {}

            temptotal = total - float(
                cache.endpoints[endpoint.identifier]["latency"]
            )

            for request_id, request in endpoint.requests.items():
                if request.video.identifier not in result[cache_id].keys():
                    result[cache_id][request.video.identifier] = 0.0
                result[cache_id][request.video.identifier] += temptotal * request.amount
                videos[request.video.identifier].best_score = temptotal * request.amount
    return result


# def lolbigsort2(weird_stuff, videos, caches):
#     for video in sorted(videos.values(), key=lambda item: item.best_score, reverse=True):
#         cache_max = -1.0
#         best_cache_id = -1
#
#         for cache_id, weird_stuff2 in weird_stuff.items():
#             try:
#                 if weird_stuff2[video.identifier] > cache_max:
#                     cache_max = weird_stuff2[video.identifier]
#                     best_cache_id = cache_id
#             except IndexError:
#                 # didn't find video id
#                 pass
#
#         best_cache = caches[best_cache_id]
#         best_cache_endpoints = map(
#             lambda item: item["obj"], best_cache.endpoints
#         )
#
#         for cache_id, cache in caches.items():
#             if cache_id == best_cache_id:
#                 continue
#             weird_stuff[cache_id][video.identifier] = 0.0
#             endpoints_exclusives = set(map(
#                 lambda item: item["obj"], cache.endpoints
#             )) - set(best_cache_endpoints)
#
#             for endpoint in endpoints_exclusives:
#                 if len(filter(lambda item: item.video.identifier == video.identifier, endpoint.requests)) > 0:
#                     total = 0.0
#                     for cache_id, cache in endpoint.caches.items():
#                         total += cache.endpoints[endpoint_id]["latency"]
#
#                     total = float(total) / float(len(endpoint.caches.values()))
#
#                     for cache_id2, cache2 in endpoint.caches.items():
#                         temptotal = total - float(
#                             cache2.endpoints[endpoint.identifier]["latency"]
#                         )
#
#
#
#                         for request_id, request in endpoint.requests.items():
#                             weird_stuff[cache_id][request.video.identifier] += temptotal * request.amount
#
#


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
        size = int(size)
        if size <= ncachecap:
            videos[i] = Video(i, size)
        i += 1

    print("\nRetrieval")
    print("Videos number retrieved %d" % (len(videos.values())))

    endpoints = {}
    caches = {}
    i = 0
    index = 2
    caches[-1] = Cache(-1)
    while i < nendpoints:
        latency_datacenter, ncaches = map(int, lines[index].split())
        endpoint = Endpoint(i, latency_datacenter, ncaches)
        caches[-1].addEndpoint(endpoint, latency_datacenter)
        endpoints[i] = endpoint
        index += 1
        j = 0
        while j < ncaches:
            identifier, latency_endpoint = map(int, lines[index].split())
            if identifier not in caches.keys():
                caches[identifier] = Cache(identifier)
            caches[identifier].addEndpoint(endpoint, latency_endpoint)
            caches[-1].addEndpoint(endpoint, latency_datacenter)
            index += 1
            j += 1
        i += 1

    print("Number of endpoints: %d" % (len(endpoints.values())))
    print("Number of caches: %d" % (len(caches.values())))

    requests = {}
    i = 0
    while i < nrequests:
        video_id, endpoint_id, amount = map(int, lines[index].split())
        try:
            requests[i] = Request(
                i, videos[video_id], endpoints[endpoint_id], amount
            )
        except IndexError:
            # Can only be triggered if video_id is referring a video which size
            # is too big
            pass
        index += 1
        i += 1

    print("Number of requests: %d" % len(requests))

    result = lolbigsort(videos, endpoints, caches, requests, ncachecap)
    print(result)

if __name__ == "__main__":
    main(sys.argv)
