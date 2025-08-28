-- truncate.sql
-- Truncate all demo tables in Agent_Data schema

TRUNCATE TABLE Agent_Data.Shipments;
TRUNCATE TABLE Agent_Data.Orders;

TRUNCATE TABLE Agent_Data.DocChunks;

TRUNCATE TABLE Agent_Data.Products;
TRUNCATE TABLE Agent_Data.Customers;

DROP TABLE Agent_Data.Shipments;
DROP TABLE Agent_Data.Orders;
DROP TABLE Agent_Data.DocChunks;
DROP TABLE Agent_Data.Products;
DROP TABLE Agent_Data.Customers;

DROP SCHEMA Agent_Data;
