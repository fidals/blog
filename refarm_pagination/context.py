from refarm_pagination.pagination import Paginator, NeighborPages


# @todo #255:30m  Improve `PaginationContext` interface.
#  It's not clear now.
#  For example client should know the class context details
#  to fetch objects iterable.
#  See `catalog.context.products.PaginatedProducts#qs`.
class PaginationContext:

    def __init__(self, url, number, per_page, objects):
        self.url = url
        self.number = number
        self.objects = objects
        self.paginator = Paginator(objects, per_page)

    def context(self):
        page = self.paginator.page(self.number)
        showed_count = (self.number - 1) * self.paginator.per_page + len(page)
        neighbours = NeighborPages(page)

        prev_pairs = [
            (prev.number, prev.url(self.url))
            for prev in neighbours.prev_neighbors()
        ]
        next_pairs = [
            (next.number, next.url(self.url))
            for next in neighbours.next_neighbors()
        ]

        return {
            'page': page,
            'prev_pairs': prev_pairs,
            'next_pairs': next_pairs,
            'showed_count': showed_count,
            'total_products': self.objects.count(),
        }
