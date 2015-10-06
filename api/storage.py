# -*- coding: utf-8 -*-


class BasicContainer(object):
    """
    Most basic container class
    """
    COLUMN_HEADERS = ['warehouse1', 'warehouse']

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
                if column1 not in self.COLUMN_HEADERS:
                    self.add_item(column1, column2, int(column3))

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
        Adds both the vertex edge and the reverse edge
        """
        super(Graph, self).add_item(index, item_id, value)
        super(Graph, self).add_item(item_id, index, value)

    def error(self, message):
        """
        Returns an error into our json response
        """
        return {'error': message}

    def exclude_visited_vertices(self, dict):
        """
        Excludes visited vertices from the neighbour dictionary
        """
        if dict:
            return {key: value for key, value in dict.items() if key not in self.visited_vertices.keys()}
        else:
            return {}

    def get_minimum_from_nested_dict(self, dict):
        """
        Returns the minimum value from a nested dictionary in a form of tuple of tuples
        """
        s = [(k, min(d.iteritems(), key=lambda a:a[1])) for k, d in dict.iteritems()]
        return min(s, key=lambda a:a[1][1])

    def strip_dict(self, dict):
        """
        Returns the value from a specific dictionary (for a singular vertex)
        """
        return [x for x in dict.itervalues()][0]

    def get_closest_next_vertex(self):
        """
        Calculates the next closest vertex from the yet not visited in the graph
        """
        nearest = {}
        for key, value in self.visited_vertices.items():
            neighbours = self.exclude_visited_vertices(self.items.get(key))
            if neighbours:
                closest = min(neighbours, key=neighbours.get)
                if nearest.get(closest, None):
                    if self.strip_dict(nearest.get(closest)) > neighbours[closest] + value:
                        nearest[closest] = {key: neighbours[closest] + value}
                else:
                    nearest[closest] = {key: neighbours[closest] + value}
        if nearest:
            closest_next = self.get_minimum_from_nested_dict(nearest)
            closest_next_vertex = closest_next[0]
        else:
            return None, None

        return closest_next_vertex, self.items[closest_next[1][0]][closest_next_vertex] +\
               self.visited_vertices[closest_next[1][0]]

    def process_vertex(self, vertex, distance=0):
        """
        Recurrent function which runs through vertices in the graph
        """
        self.visited_vertices.update({vertex: distance})
        next_vertex, new_distance = self.get_closest_next_vertex()
        if next_vertex:
            self.process_vertex(next_vertex, new_distance)
        else:
            return None

    def process(self, vertex):
        """
        Go through the graph vertices
        """
        self.visited_vertices = {}
        start = self.items.get(vertex, None)
        if start:
            self.process_vertex(vertex)
            return self.visited_vertices
        else:
            return self.error('Start vertex does not exist.')
