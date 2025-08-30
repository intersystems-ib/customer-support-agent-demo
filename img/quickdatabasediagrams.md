https://app.quickdatabasediagrams.com/#/

```
Customers
--
CustomerID 
Name
Email

Products
--
ProductID
Name
Category
Price
WarrantyMonths
Description
Embedding

Orders
--
OrderID
CustomerID FK >- Customers.CustomerID
ProductID FK >- Products.ProductID
OrderDate
Status

Shipments
--
OrderID FK >- Orders.OrderID
Carrier
TrackingCode
LastUpdate

DocChunks
--
ChunkID
DocID
ChunkIndex
StartPos
EndPos
Title
Heading
ChunkText
Embedding
```