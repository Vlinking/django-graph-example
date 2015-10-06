
import heapq

from django.http import JsonResponse
from django.views.generic import View
from django.views.generic.base import ContextMixin


COLUMN_HEADERS = ['warehouse1', 'warehouse']


class BasicContainer(object):
    def __init__(self):
        self.items = {}

    def add_item(self, index, item_id, value):
        """
        add a new item to the storage object
        """
        if self.items.get(index):
            self.items[index].update({item_id: value})
        else:
            self.items[index] = {item_id: value}

    def import_from_file(self, filename):
        with open(filename, "r") as f:
            text = f.readlines()
            for line in text:
                column1, column2, column3 = [x.strip() for x in line.split(",")]
                if column1 not in COLUMN_HEADERS:
                    self.add_item(column1, column2, column3)

    def __str__(self):
        return str(self.items)


class Storage(BasicContainer):
    """
    Class which implements a collection of warehouses with products via a Facade
    """
    def get_product_quantity(self, warehouse, product):
        warehouse_storage = self.items.get(warehouse, None)
        return warehouse_storage.get(product, 0)


class Graph(BasicContainer):
    """
    Class which implements weighted Graphs via a Facade design pattern
    """
    def __init__(self, storage, products):
        super(Graph, self).__init__()
        self.products = products
        self.gathered_products = {key: 0 for (key, _) in products}
        self.storage = storage

    def add_item(self, index, item_id, value):
        """
        Add both the vertex edge and the reverse
        """
        super(Graph, self).add_item(index, item_id, value)
        super(Graph, self).add_item(item_id, index, value)

    def error(self, message):
        return {'error': message}

    def exclude_visited_vertices(self, dict):
        if dict:
            return {key: value for key, value in dict.items() if key not in self.visited_vertices.keys()}
        else:
            return {}

    def NestedDictMin(self, dict):
        s = [(k, min(d.iteritems(), key=lambda a:a[1])) for k, d in dict.iteritems()]
        return min(s, key=lambda a:a[1][1])

    def strip_dict(self, dict):
        return [x for x in dict.itervalues()]

    def get_closest_next_vertex(self, vertex, distance):
        nearest = {}
        for key, value in self.visited_vertices.items():
            neighbours = self.exclude_visited_vertices(self.items.get(key))
            if neighbours:
                closest = min(neighbours, key=neighbours.get)
                if nearest.get(closest, None):
                    if self.strip_dict(nearest.get(closest))[0] > neighbours[closest] + value:
                        nearest[closest] = {key: neighbours[closest] + value}
                else:
                    nearest[closest] = {key: neighbours[closest] + value}
        if nearest:
            print nearest
            closest_next = self.NestedDictMin(nearest)
            closest_next_vertex = closest_next[0]
        else:
            return None, None

        return closest_next_vertex, self.items[closest_next[1][0]][closest_next_vertex] + self.visited_vertices[closest_next[1][0]]

    def process_vertex(self, vertex, distance=0):
        # print vertex
        self.visited_vertices.update({vertex: distance})
        next_vertex, new_distance = self.get_closest_next_vertex(vertex, distance)
        if next_vertex:
            self.process_vertex(next_vertex, new_distance)
        else:
            return None

    def calculate_gathering_time(self, warehouse):
        """
        Go through each node, get stuff,
        """
        self.visited_vertices = {}
        start = self.items.get(warehouse, None)
        if start:
            self.visited_vertices.update({warehouse: 0})
            self.process_vertex(warehouse)
            return self.visited_vertices
        else:
            return self.error('Start warehouse does not exist.')


class AjaxRequiredMixin(object):
    """
    A mixin that blocks the view when not using ajax
    """
    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            return super(AjaxRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return JsonResponse({'error': 'not an ajax request'})


class JsonView(ContextMixin, View):
    """
    A view that renders a template.  This view will also pass into the context
    any keyword arguments passed by the url conf.
    """
    def process_data(self, context):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        data = self.process_data(context)
        return JsonResponse(data)


class ProductsSetView(JsonView):
    """
    Returns the product assembly time for a given warehouse and a set of products
    """
    def process_data(self, context):
        warehouses = Storage()
        warehouses.import_from_file("api/stocks.csv")
        products = self.request.GET.getlist('products[]')
        quantities = self.request.GET.getlist('quantities[]')

        products_dict = {x: y for x in products for y in quantities}

        connections = Graph(
            warehouses,
            products_dict
        )
        connections.import_from_file("api/connections.csv")
        connections.items = {
            'A': {'E': 1, 'B': 3},
            'B': {'A': 3, 'C': 4, 'D': 2},
            'C': {'B': 4, 'D': 8, 'E': 2},
            'D': {'B': 2, 'C': 8},
            'E': {'A': 1, 'C': 2},
        }
        return connections.calculate_gathering_time(context.get('warehouse'))