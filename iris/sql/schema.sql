-- schema.sql
-- Schema for Customer Support Agent demo
-- All tables under schema Agent_Data

------------------------------------------------------------
-- Create schema
------------------------------------------------------------
CREATE SCHEMA Agent_Data;

------------------------------------------------------------
-- Customers
------------------------------------------------------------
CREATE TABLE Agent_Data.Customers (
    CustomerID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(150) UNIQUE NOT NULL
);

------------------------------------------------------------
-- Products
------------------------------------------------------------
CREATE TABLE Agent_Data.Products (
    ProductID INT PRIMARY KEY,
    Name VARCHAR(200) NOT NULL,
    Category VARCHAR(50),
    Price DECIMAL(10,2),
    WarrantyMonths INT,
    Description VARCHAR(1000)
);

------------------------------------------------------------
-- Orders
------------------------------------------------------------
CREATE TABLE Agent_Data.Orders (
    OrderID INT PRIMARY KEY,
    CustomerID INT NOT NULL,
    ProductID INT NOT NULL,
    OrderDate DATE NOT NULL,
    Status VARCHAR(20),
    FOREIGN KEY (CustomerID) REFERENCES Agent_Data.Customers(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES Agent_Data.Products(ProductID)
);

------------------------------------------------------------
-- Shipments
------------------------------------------------------------
CREATE TABLE Agent_Data.Shipments (
    OrderID INT PRIMARY KEY,
    Carrier VARCHAR(50),
    TrackingCode VARCHAR(100),
    LastUpdate TIMESTAMP,
    FOREIGN KEY (OrderID) REFERENCES Agent_Data.Orders(OrderID)
);

------------------------------------------------------------
-- Product Vectors for semantic search
------------------------------------------------------------
CREATE TABLE Agent_Data.ProductVectors (
    ProductID INT PRIMARY KEY,
    Embedding VECTOR(FLOAT, 1536),
    FOREIGN KEY (ProductID) REFERENCES Agent_Data.Products(ProductID)
);

------------------------------------------------------------
-- Document Vectors for RAG
------------------------------------------------------------
CREATE TABLE Agent_Data.DocVectors (
    DocID VARCHAR(64) PRIMARY KEY,
    Title VARCHAR(200),
    Embedding VECTOR(FLOAT, 1536)
);

------------------------------------------------------------
-- Optional: Docs metadata table
------------------------------------------------------------
CREATE TABLE Agent_Data.Docs (
    DocID VARCHAR(64) PRIMARY KEY,
    Title VARCHAR(200),
    BodyText VARCHAR(4000),
    DocType VARCHAR(50)
);
