from django.http import JsonResponse
from django.views.generic import View
from django.views.generic.base import ContextMixin
from api.storage import Storage, WarehouseGraph


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

        products_dict = {x: y for x, y in zip(products, quantities)}

        connections = WarehouseGraph(
            warehouses,
            products_dict
        )
        connections.import_from_file("api/connections.csv")

        return connections.process(context.get('warehouse'))