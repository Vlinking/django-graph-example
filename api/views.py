from django.http import JsonResponse
from django.views.generic import View
from django.views.generic.base import ContextMixin
from api.storage import Storage, Graph


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
        # connections.items = {
        #     'A': {'E': 1, 'B': 3},
        #     'B': {'A': 3, 'C': 4, 'D': 2},
        #     'C': {'B': 4, 'D': 8, 'E': 2},
        #     'D': {'B': 2, 'C': 8},
        #     'E': {'A': 1, 'C': 2},
        # }
        return connections.process(context.get('warehouse'))