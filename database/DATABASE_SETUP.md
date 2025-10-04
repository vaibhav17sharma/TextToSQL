# Database Setup Guide

This guide explains how to set up and test the PostgreSQL database service for the Text-to-SQL application.

## PostgreSQL Service
- **Container**: `postgres-container`
- **Port**: `5432`
- **Database**: `testdb`
- **Username**: `postgres`
- **Password**: `postgres`

## Quick Start

### Start Services
```bash
# Start all services (backend + database)
docker-compose up -d
```

## PostgreSQL Sample Database

The PostgreSQL service includes a comprehensive e-commerce sample database with:

### Tables
- **customers** - Customer information with types (regular/premium)
- **categories** - Product categories with hierarchical structure
- **products** - Product catalog with inventory tracking
- **orders** - Order management with status tracking
- **order_items** - Order line items
- **suppliers** - Supplier information
- **product_suppliers** - Product-supplier relationships

### Sample Data
- 10 customers (mix of regular and premium)
- 8 product categories
- 10 products across different categories
- 8 orders with various statuses
- 5 suppliers with ratings
- Pre-built views for common queries

### Views
- **customer_summary** - Customer overview with totals
- **product_inventory** - Product stock status
- **order_details** - Order summary with customer info

## Testing Natural Language Queries

Once your services are running, you can test these natural language queries through your API:

### Customer Queries
- "Show me all premium customers"
- "How many customers do we have?"
- "Find customers who have spent more than $1000"
- "List customers from California"

### Product Queries
- "What are the top 5 most expensive products?"
- "Show me all Apple products"
- "Which products are out of stock?"
- "List all products with low stock"

### Order Queries
- "How many orders have been delivered?"
- "Show me all pending orders"
- "Find orders from this year"
- "What is our total revenue?"

### Inventory Queries
- "Show me products that need restocking"
- "List all products in the Electronics category"
- "Find products with more than 50 units in stock"

## Manual Database Access

### PostgreSQL
```bash
# Connect to PostgreSQL container
docker exec -it postgres-container psql -U postgres -d testdb

# Or connect from host (if you have psql installed)
psql -h localhost -p 5432 -U postgres -d testdb
```

## Troubleshooting

### PostgreSQL Connection Issues
1. Check if the container is running:
   ```bash
   docker ps | grep postgres
   ```

2. Check container logs:
   ```bash
   docker logs postgres-container
   ```

3. Restart the service:
   ```bash
   docker-compose restart postgres
   ```

### Port Conflicts
If you get port binding errors:
- PostgreSQL: Change port from `5432` to another port in docker-compose.yml

### Data Persistence
- PostgreSQL data is stored in Docker volume: `postgres_data`

To reset the database:
```bash
docker-compose down -v  # This will remove volumes and all data
docker-compose up -d    # This will recreate with fresh data
```

## Development Tips

1. **Test different query types** - Try aggregations, joins, filters, and sorting

2. **Monitor query performance** - Check execution times in the API responses

3. **Validate SQL output** - Always verify the generated SQL makes sense

4. **Test edge cases** - Try ambiguous queries to see how the model handles them