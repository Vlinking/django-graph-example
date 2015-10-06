from mock import mock

from django.test import TestCase

from api.views import ProductsSetView


# Of course, it would be perfect to test the functionality by a 100% unit test code coverage...
# However this is beyond the scope of this exercise at the moment

# functional tests
# I'm presuming here the data files are constant, since they're part of the exercise
class ProductsSetViewTest(TestCase):
    def setUp(self):
        """
        Set up initial data
        """
        self.obj = ProductsSetView()
        self.products = ['570E77', 'E1D9F2']
        self.quantities = [120, 500]

    def getlist(self, arg):
        """
        "Mocked" function
        """
        if arg == 'products[]':
            return self.products
        else:
            return self.quantities

    def test_process_data(self):
        """
        Test for a normal query that returns some time
        """
        self.obj.request = mock.MagicMock()
        self.obj.request.GET = mock.MagicMock()
        self.obj.request.GET.getlist = self.getlist
        self.assertEqual(self.obj.process_data({'warehouse': 'W1'}), {'delivery_time': 30})

    def test_process_data_insufficient(self):
        """
        Test for a query that is impossible to fulfill
        """
        self.quantities = [1000, 2000]
        self.obj.request = mock.MagicMock()
        self.obj.request.GET = mock.MagicMock()
        self.obj.request.GET.getlist = self.getlist
        self.assertEqual(self.obj.process_data({'warehouse': 'W1'}),
                         {'error': 'Delivery impossible for the current warehouse stocks.'})

