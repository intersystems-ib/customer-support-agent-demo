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
    Description VARCHAR(1000),
    Embedding VECTOR(FLOAT, 1536)     -- vector for product search
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
-- Document storage for knowledge base
------------------------------------------------------------
CREATE TABLE Agent_Data.DocChunks (
    ChunkID     INT IDENTITY,
    DocID       VARCHAR(64)     NOT NULL,   -- logical doc grouping key (filename stem, etc.)
    ChunkIndex  INT             NOT NULL,   -- 0,1,2… within the DocID
    StartPos    INT,                        -- optional: char offset
    EndPos      INT,                        -- optional: char offset
    Title       VARCHAR(200),
    Heading     VARCHAR(200),
    ChunkText   VARCHAR(4000)   NOT NULL,  
    Embedding   VECTOR(FLOAT, 1536),        -- vector for semantic search
    CONSTRAINT DocChunksPK PRIMARY KEY (ChunkID),
    CONSTRAINT DocChunksDocIndexUQ UNIQUE (DocID, ChunkIndex)
);