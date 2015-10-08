# django-graph-example
A service for suuplying information about gathering resources from warehouses, using weighted graphs, Django and REST API framework

# Philosophy

Based on two files, connections.csv and stocks.csv, the application creates a REST api service to ascertain how many time would it take to gather wanted products.

## connections.csv

warehouse1, warehouse2, time - contains vertices for the warehouse connection graph

## stocks.csv

warehouse, product, quantity - contains storage info of products in warehouses net

# The service

Is available from the url api/get_products_set/(warehouse)/, where warehouse is the warehouse we want to store the order.

Additionally, the GET request should supply products name array and wanted quantity array.

