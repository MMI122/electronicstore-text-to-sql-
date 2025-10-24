# Gadgets Store - Natural Language to SQL

A comprehensive electronics store management system with AI-powered natural language to SQL query capabilities. Built with Flask (backend) and React (frontend), featuring banking integration and advanced analytics.

## 🌟 Features

### Core Functionality
- **Natural Language to SQL**: Convert plain English queries to SQL using free AI services
- **Product Management**: Complete CRUD operations for electronics inventory
- **Order Processing**: Full order lifecycle management with status tracking
- **Banking Integration**: Customer accounts, transactions, and payment processing
- **Advanced Analytics**: Sales trends, customer insights, and performance metrics

### AI-Powered Queries
- Complex SQL generation with joins, subqueries, and aggregations
- Support for all SQL operations (SELECT, INSERT, UPDATE, DELETE)
- Advanced features like window functions, CTEs, and stored procedures
- Real-time query execution with result visualization

### Database Features
- **Comprehensive Schema**: 12+ interconnected tables
- **Views & Procedures**: Pre-built analytics views and stored procedures
- **Triggers**: Automated business logic enforcement
- **Advanced Queries**: Complex reporting with multiple joins and aggregations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd gadgets-store
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup
```bash
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE gadgets_store;
USE gadgets_store;

# Import schema and seed data
SOURCE db/schema.sql;
SOURCE db/seed.sql;
```

### 4. Frontend Setup
```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Start Backend Server
```bash
# In backend directory
python app.py
```

## 🔧 Configuration

### Environment Variables (.env)
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=gadgets_store
HUGGINGFACE_API_TOKEN=your_free_hf_token
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

### Getting Free Hugging Face Token
1. Visit [https://huggingface.co/](https://huggingface.co/)
2. Create a free account
3. Go to Settings → Access Tokens
4. Create new token with read permissions
5. Add token to `.env` file

## 📊 Database Schema

### Core Tables
- **products**: Electronics inventory with specifications
- **categories**: Product categorization hierarchy  
- **customers**: Customer information and loyalty data
- **orders**: Order management with status tracking
- **order_items**: Individual items within orders
- **suppliers**: Supplier information and ratings
- **employees**: Staff management
- **stores**: Multi-location support

### Banking Tables
- **banking_accounts**: Customer financial accounts
- **banking_transactions**: Transaction history and processing
- **product_reviews**: Customer feedback system
- **inventory_logs**: Stock movement tracking

### Advanced Features
- **Views**: `customer_summary`, `product_performance`
- **Stored Procedures**: Complex analytics and reporting
- **Triggers**: Automated business logic
- **Functions**: Custom calculations and utilities

## 🤖 Natural Language Queries

### Supported Query Types

#### Sales Analysis
```
- "Show me total sales for last 30 days"
- "What are the top selling products by revenue?"
- "Sales by category this month"
- "Daily sales trend for the last week"
```

#### Customer Insights
```
- "Who are my top 10 customers by spending?"
- "Show new customers this month"
- "Customer loyalty points analysis" 
- "Average order value by customer segment"
```

#### Inventory Management
```
- "Which products are low on stock?"
- "Show me out of stock items"
- "Inventory value by category"
- "Recent stock movements"
```

#### Financial Reporting
```
- "Show banking transactions for last month"
- "Payment method usage statistics"
- "Account balances summary"
- "Revenue by payment type"
```

#### Advanced Analytics
```
- "Show me products with rating above 4 stars"
- "Employee performance by sales"
- "Store performance comparison"
- "Seasonal sales patterns"
```

## 🏗️ Architecture

### Backend (Flask)
- **Routes**: Modular API endpoints
- **Database**: MySQL with connection pooling
- **AI Service**: Hugging Face integration
- **Error Handling**: Comprehensive error management

### Frontend (React)
- **Components**: Reusable UI components
- **State Management**: React Query for server state
- **Styling**: Tailwind CSS
- **Charts**: Chart.js for data visualization

## 📈 Advanced SQL Features

### Complex Joins
```sql
-- Multi-table joins with performance metrics
SELECT 
    p.product_name,
    c.category_name,
    s.company_name as supplier,
    SUM(oi.total_price) as revenue,
    RANK() OVER (ORDER BY SUM(oi.total_price) DESC) as revenue_rank
FROM products p
INNER JOIN categories c ON p.category_id = c.category_id
INNER JOIN suppliers s ON p.supplier_id = s.supplier_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'DELIVERED'
GROUP BY p.product_id
HAVING revenue > 1000;
```

### Window Functions & CTEs
```sql
-- Advanced analytics with window functions
WITH monthly_sales AS (
    SELECT 
        DATE_FORMAT(order_date, '%Y-%m') as month,
        SUM(total_amount) as revenue,
        LAG(SUM(total_amount)) OVER (ORDER BY DATE_FORMAT(order_date, '%Y-%m')) as prev_month_revenue
    FROM orders 
    WHERE order_status = 'DELIVERED'
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
)
SELECT 
    month,
    revenue,
    prev_month_revenue,
    ROUND(((revenue - prev_month_revenue) / prev_month_revenue * 100), 2) as growth_rate
FROM monthly_sales;
```

### Stored Procedures
```sql
-- Advanced sales analysis procedure
CALL get_sales_analysis('2024-01-01', '2024-12-31', 1);
```

## 🔍 API Endpoints

### Products
- `GET /api/products` - List products with filters
- `GET /api/products/{id}` - Get product details
- `GET /api/products/categories` - List categories
- `GET /api/products/analytics` - Product analytics

### Orders
- `GET /api/orders` - List orders
- `POST /api/orders` - Create new order
- `PUT /api/orders/{id}/status` - Update order status
- `GET /api/orders/analytics` - Order analytics

### AI Queries
- `POST /api/ai/query` - Execute natural language query
- `GET /api/ai/suggestions` - Get query suggestions
- `GET /api/ai/schema` - Get database schema info

### Banking
- `GET /api/orders/banking/accounts/{customer_id}` - Customer accounts
- `GET /api/orders/banking/transactions/{account_id}` - Account transactions

## 🧪 Sample Queries

### Complex Business Intelligence Queries
```sql
-- Customer Lifetime Value Analysis
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) as customer_name,
    get_customer_lifetime_value(c.customer_id) as lifetime_value,
    COUNT(DISTINCT o.order_id) as total_orders,
    AVG(DATEDIFF(LEAD(o.order_date) OVER (PARTITION BY c.customer_id ORDER BY o.order_date), o.order_date)) as avg_days_between_orders
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id;

-- Product Performance with Cohort Analysis
SELECT 
    p.product_name,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    COUNT(DISTINCT CASE WHEN o.order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) THEN o.customer_id END) as recent_customers,
    ROUND(COUNT(DISTINCT CASE WHEN o.order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) THEN o.customer_id END) / COUNT(DISTINCT o.customer_id) * 100, 2) as retention_rate
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'DELIVERED'
GROUP BY p.product_id;
```

## 🎯 Use Cases

### Retail Management
- Inventory optimization
- Sales performance tracking
- Customer behavior analysis
- Supplier management

### Financial Services
- Transaction monitoring
- Account management
- Payment processing
- Risk assessment

### Business Intelligence
- KPI dashboards
- Trend analysis
- Predictive insights
- Performance metrics

## 🚦 Deployment

### Production Setup
```bash
# Backend
gunicorn --bind 0.0.0.0:5000 app:app

# Frontend
npm run build
# Serve dist/ folder with nginx or similar
```

### Docker Deployment
```dockerfile
# Dockerfile example for backend
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♀️ Support

- 📧 Email: support@gadgetsstore.com
- 💬 Issues: GitHub Issues
- 📖 Documentation: [Wiki](wiki-url)

## 🎉 Acknowledgments

- Hugging Face for free AI inference
- TailwindCSS for styling
- Chart.js for visualizations
- React Query for state management

---

