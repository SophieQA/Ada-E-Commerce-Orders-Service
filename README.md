# Order Service
## Description

The Order Service is one of 3 microservices for the Ada Developers Academy Cloud Curriculum e-commerce application. It handles the creation and management of customer orders in  e-commerce system. Each order belongs to a user and contains one or more order items, where each item references a product (by ID, name, and price) along with a quantity.

### Data Models

- **Order** — represents a customer order, associated with a `user_id`
- **OrderItem** — represents a line item within an order, containing `product_id`, `product_name`, `product_price`, and `quantity`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/orders/` | Create a new order |
| GET | `/orders/` | Get all orders (supports query filters) |
| GET | `/orders/<id>` | Get a single order by ID |
| PUT | `/orders/<id>` | Update an order by ID |
| DELETE | `/orders/<id>` | Delete an order by ID |

## Prerequisites

- Python 3.13+
- PostgreSQL

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd order-service
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:postgres@localhost:5432/order_service_db
SQLALCHEMY_TEST_DATABASE_URI=postgresql+psycopg2://postgres:postgres@localhost:5432/order_service_test_db
```

### 5. Create the database

```bash
psql -U postgres

# Inside psql CLI 
CREATE DATABASE order_service_db;
CREATE DATABASE order_service_test_db;
```

### 6. Run database migrations

```bash
flask db upgrade
```

### 7. (Optional) Seed the database

```bash
python seed.py
```

## Running the App

```bash
flask run --debug
```

## Running Tests

```bash
pytest
```
