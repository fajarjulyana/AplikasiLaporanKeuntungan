import sqlite3
import os
import pandas as pd
from flask import g

DATABASE = 'kasir.db'

def get_db():
    """Connect to the database if not already connected."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db(app):
    """Initialize database connection."""
    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

def query_db(query, args=(), one=False):
    """Query the database and return results."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_table_names():
    """Get all table names from the database."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]

def get_table_structure(table_name):
    """Get the structure of a specific table."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    return cursor.fetchall()

def get_transactions(start_date=None, end_date=None):
    """Get transactions with optional date filtering."""
    query = "SELECT * FROM transaksi_log"
    params = []
    
    # Add date filtering if provided
    if start_date and end_date:
        query += " WHERE tanggal >= ? AND tanggal <= ?"
        params.extend([start_date, end_date])
    elif start_date:
        query += " WHERE tanggal >= ?"
        params.append(start_date)
    elif end_date:
        query += " WHERE tanggal <= ?"
        params.append(end_date)
    
    query += " ORDER BY tanggal DESC"
    
    return query_db(query, params)

def get_transaction_details(transaction_id):
    """Get details of a specific transaction."""
    return query_db("SELECT * FROM detail_transaksi WHERE transaksi_id = ?", [transaction_id])

def get_products():
    """Get all products from the database."""
    return query_db("SELECT * FROM barang")

def get_product_stock():
    """Get product stock information."""
    return query_db("SELECT id, nama as nama_produk, jumlah FROM barang ORDER BY jumlah DESC")

def get_daily_revenue(start_date=None, end_date=None):
    """Get daily revenue data for charting."""
    query = """
    SELECT tanggal, SUM(total) as daily_revenue
    FROM transaksi_log
    """
    params = []
    
    # Add date filtering if provided
    if start_date and end_date:
        query += " WHERE tanggal >= ? AND tanggal <= ?"
        params.extend([start_date, end_date])
    elif start_date:
        query += " WHERE tanggal >= ?"
        params.append(start_date)
    elif end_date:
        query += " WHERE tanggal <= ?"
        params.append(end_date)
    
    query += " GROUP BY tanggal ORDER BY tanggal"
    
    return query_db(query, params)

def get_product_sales():
    """Get product sales for product performance analysis."""
    query = """
    SELECT b.nama as nama_produk,
           SUM(dt.jumlah) as total_quantity,
           SUM(dt.jumlah * dt.harga) as total_revenue
    FROM detail_transaksi dt
    JOIN barang b ON dt.id_barang = b.id
    GROUP BY b.id, b.nama
    ORDER BY total_revenue DESC
    LIMIT 5
    """
    try:
        result = query_db(query)
        if not result:
            return [{'nama_produk': 'N/A', 'total_quantity': 0, 'total_revenue': 0.0} for _ in range(5)]
        # Ensure we always return 5 items
        while len(result) < 5:
            result.append({'nama_produk': 'N/A', 'total_quantity': 0, 'total_revenue': 0.0})
        return result
    except Exception as e:
        print(f"Error getting product sales: {e}")
        return []
    except Exception as e:
        print(f"Error getting product sales: {e}")
        # Return dummy data for debugging
        return []

def get_monthly_revenue():
    """Get monthly revenue for trend analysis."""
    query = """
    SELECT strftime('%Y-%m', tanggal) as month, SUM(total) as monthly_revenue
    FROM transaksi_log
    GROUP BY month
    ORDER BY month
    """
    return query_db(query)

def get_revenue_by_category():
    """Get revenue by product category."""
    # Return empty list since categories are not used
    return []

def get_profit_data(start_date=None, end_date=None):
    """Calculate profit data from sales and product cost."""
    query = """
    SELECT 
        t.id, 
        t.tanggal, 
        t.total as revenue,
        COALESCE(p.cost, 0) as cost,
        COALESCE(t.total - p.cost, 0) as profit,
        CASE 
            WHEN t.total > 0 THEN ((t.total - COALESCE(p.cost, 0)) / t.total * 100)
            ELSE 0 
        END as profit_margin
    FROM transaksi_log t
    LEFT JOIN (
        SELECT 
            dt.transaksi_id,
            SUM(dt.jumlah * b.harga_beli) as cost
        FROM detail_transaksi dt
        JOIN barang b ON dt.id_barang = b.id
        GROUP BY dt.transaksi_id
    ) p ON t.id = p.transaksi_id
    """
    params = []
    
    # Add date filtering if provided
    if start_date and end_date:
        query += " WHERE t.tanggal >= ? AND t.tanggal <= ?"
        params.extend([start_date, end_date])
    elif start_date:
        query += " WHERE t.tanggal >= ?"
        params.append(start_date)
    elif end_date:
        query += " WHERE t.tanggal <= ?"
        params.append(end_date)
    
    query += " GROUP BY t.id ORDER BY t.tanggal DESC"
    
    return query_db(query, params)

def get_summary_stats(start_date=None, end_date=None):
    """Get summary statistics for the dashboard."""
    profit_data = get_profit_data(start_date, end_date)
    
    if not profit_data:
        return {
            'total_revenue': 0,
            'total_cost': 0,
            'total_profit': 0,
            'average_profit_margin': 0,
            'transaction_count': 0
        }
    
    # Convert to pandas DataFrame for easier calculations
    df = pd.DataFrame([dict(row) for row in profit_data])
    
    return {
        'total_revenue': df['revenue'].sum(),
        'total_cost': df['cost'].sum(),
        'total_profit': df['profit'].sum(),
        'average_profit_margin': df['profit_margin'].mean(),
        'transaction_count': len(df)
    }
