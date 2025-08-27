-- truncate.sql
-- Truncate all demo tables in Agent_Data schema
-- Run this before reseeding data

------------------------------------------------------------
-- Order matters because of FK dependencies
-- First truncate children, then parents
------------------------------------------------------------

-- Child tables
TRUNCATE TABLE Agent_Data.Shipments;
TRUNCATE TABLE Agent_Data.Orders;

-- Vector + docs (no FKs into other tables)
TRUNCATE TABLE Agent_Data.ProductVectors;
TRUNCATE TABLE Agent_Data.DocVectors;
TRUNCATE TABLE Agent_Data.Docs;

-- Parent tables
TRUNCATE TABLE Agent_Data.Products;
TRUNCATE TABLE Agent_Data.Customers;

DROP TABLE Agent_Data.Shipments;
DROP TABLE Agent_Data.Orders;
DROP TABLE Agent_Data.ProductVectors;
DROP TABLE Agent_Data.DocVectors;
DROP TABLE Agent_Data.Docs;
DROP TABLE Agent_Data.Products;
DROP TABLE Agent_Data.Customers;
DROP SCHEMA Agent_Data;
