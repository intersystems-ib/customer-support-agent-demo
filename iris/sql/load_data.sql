-- load_data.sql
-- Bulk load demo CSVs into Agent_Data.* using IRIS LOAD DATA.

------------------------------------------------------------
-- Customers
------------------------------------------------------------
LOAD DATA FROM FILE '/app/iris/data/customers.csv'
INTO Agent_Data.Customers
USING {"from":{"file":{"header":true}}};

------------------------------------------------------------
-- Products
------------------------------------------------------------
LOAD DATA FROM FILE '/app/iris/data/products.csv'
INTO Agent_Data.Products
USING {"from":{"file":{"header":true}}};

------------------------------------------------------------
-- Orders
------------------------------------------------------------
LOAD DATA FROM FILE '/app/iris/data/orders.csv'
INTO Agent_Data.Orders
USING {"from":{"file":{"header":true}}};

------------------------------------------------------------
-- Shipments
------------------------------------------------------------
LOAD DATA FROM FILE '/app/iris/data/shipments.csv'
INTO Agent_Data.Shipments
USING {"from":{"file":{"header":true}}};
