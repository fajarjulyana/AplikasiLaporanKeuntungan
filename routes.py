from flask import render_template, request, jsonify, redirect, url_for, flash, send_file, make_response
import sqlite3
from app import app
from database import (
    get_transactions, get_daily_revenue, get_product_sales,
    get_monthly_revenue, get_revenue_by_category, get_profit_data,
    get_summary_stats, get_table_names, get_table_structure,
    get_product_stock
)
import datetime
import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm

@app.route('/')
def index():
    """Render the dashboard page with summary statistics."""
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get summary statistics
    summary = get_summary_stats(start_date, end_date)

    # Get daily revenue data for the chart
    daily_revenue = get_daily_revenue(start_date, end_date)

    # Get product sales data
    product_sales = get_product_sales()

    # Get product stock information
    product_stock = get_product_stock()

    # Prepare data for charts
    chart_labels = [row['tanggal'] for row in daily_revenue] if daily_revenue else []
    chart_data = [float(row['daily_revenue']) for row in daily_revenue] if daily_revenue else []

    # Prepare stock data for pie chart (replacing category data)
    stock_labels = [row['nama_produk'] for row in product_stock[:10]] if product_stock else []
    stock_data = [int(row['jumlah']) for row in product_stock[:10]] if product_stock else []

    # Get the top 5 selling products
    top_products = product_sales[:5] if product_sales else []

    return render_template(
        'index.html',
        summary=summary,
        chart_labels=chart_labels,
        chart_data=chart_data,
        category_labels=stock_labels,  # renamed but used for stock data
        category_data=stock_data,      # renamed but used for stock data
        top_products=top_products,
        product_stock=product_stock,
        start_date=start_date,
        end_date=end_date
    )

@app.route('/transactions')
def transactions():
    """Render the transactions page with transaction data."""
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get transaction data
    transaction_data = get_transactions(start_date, end_date)

    # Get profit data
    profit_data = get_profit_data(start_date, end_date)

    # Convert profit data to a dictionary for easy lookup
    profit_dict = {row['id']: row for row in profit_data}

    return render_template(
        'transactions.html',
        transactions=transaction_data,
        profit_dict=profit_dict,
        start_date=start_date,
        end_date=end_date
    )

@app.route('/analytics')
def analytics():
    """Render the analytics page with detailed data analysis."""
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get monthly revenue for trend analysis
    monthly_revenue = get_monthly_revenue()

    # Get product sales data
    product_sales = get_product_sales()

    # Get revenue by category
    category_revenue = get_revenue_by_category()

    # Prepare monthly data for charts
    monthly_labels = [row['month'] for row in monthly_revenue]
    monthly_data = [float(row['monthly_revenue']) for row in monthly_revenue]

    # Calculate growth rates
    growth_rates = []
    for i in range(1, len(monthly_data)):
        if monthly_data[i-1] > 0:
            growth_rate = (monthly_data[i] - monthly_data[i-1]) / monthly_data[i-1] * 100
            growth_rates.append((monthly_labels[i], round(growth_rate, 2)))
        else:
            growth_rates.append((monthly_labels[i], 100))  # If previous month was 0, show 100% growth

    return render_template(
        'analytics.html',
        product_sales=product_sales,
        category_revenue=category_revenue,
        monthly_labels=monthly_labels,
        monthly_data=monthly_data,
        growth_rates=growth_rates,
        start_date=start_date,
        end_date=end_date
    )

@app.route('/api/daily-revenue')
def api_daily_revenue():
    """API endpoint for daily revenue data."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    daily_revenue = get_daily_revenue(start_date, end_date)

    return jsonify({
        'labels': [row['tanggal'] for row in daily_revenue],
        'data': [float(row['daily_revenue']) for row in daily_revenue]
    })

@app.route('/api/monthly-revenue')
def api_monthly_revenue():
    """API endpoint for monthly revenue data."""
    monthly_revenue = get_monthly_revenue()

    return jsonify({
        'labels': [row['month'] for row in monthly_revenue],
        'data': [float(row['monthly_revenue']) for row in monthly_revenue]
    })

@app.route('/api/category-revenue')
def api_category_revenue():
    """API endpoint for category revenue data."""
    category_revenue = get_revenue_by_category()

    return jsonify({
        'labels': [row['kategori'] for row in category_revenue],
        'data': [float(row['category_revenue']) for row in category_revenue]
    })

@app.route('/db-info')
def db_info():
    """Display database information for debugging."""
    tables = get_table_names()
    table_structures = {table: get_table_structure(table) for table in tables}

    return render_template(
        'error.html',
        tables=tables,
        table_structures=table_structures
    )

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', error='Page not found.'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('error.html', error='An internal server error occurred.'), 500

@app.route('/export/pdf')
def export_pdf():
    """Generate a PDF report of revenue analysis."""
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get all necessary data
    summary = get_summary_stats(start_date, end_date)
    transaction_data = get_transactions(start_date, end_date)
    product_sales = get_product_sales()
    category_revenue = get_revenue_by_category()
    top_products = []
    if product_sales:
        for product in product_sales:
            if isinstance(product, sqlite3.Row):
                top_products.append({
                    'nama_produk': product['nama_produk'],
                    'total_quantity': product['total_quantity'],
                    'total_revenue': float(product['total_revenue'])
                })
            else:
                top_products.append(product)
        top_products = top_products[:5]
    # Get profit data with proper handling
    profit_data = get_profit_data(start_date, end_date)
    profit_dict = {}
    if profit_data:
        for row in profit_data:
            if isinstance(row, sqlite3.Row):
                profit_dict[row['id']] = {
                    'cost': float(row['cost']) if row['cost'] is not None else 0,
                    'profit': float(row['profit']) if row['profit'] is not None else 0,
                    'profit_margin': float(row['profit_margin']) if row['profit_margin'] is not None else 0
                }
            else:
                profit_dict[row['id']] = row

    # Create PDF document
    buffer = io.BytesIO()

    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Laporan Pendapatan Fajar Mandiri Store")

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading1']
    normal_style = styles['Normal']

    # Add custom style for Indonesian text
    indo_style = ParagraphStyle(
        'Indonesian',
        parent=normal_style,
        fontSize=10,
        leading=14,
    )

    # Create document content
    elements = []

    # Add title
    elements.append(Paragraph("Laporan Analisis Pendapatan Fajar Mandiri Store", title_style))
    elements.append(Spacer(1, 0.5*cm))

    # Add date range
    period_text = f"Periode: {start_date or 'Semua waktu'} sampai {end_date or 'Sekarang'}"
    elements.append(Paragraph(period_text, indo_style))
    elements.append(Spacer(1, 1*cm))

    # Add summary section
    elements.append(Paragraph("Ringkasan", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    # Summary data
    if summary:
        summary_data = [
            ["Metrik", "Nilai"],
            ["Total Pendapatan", f"Rp {summary['total_revenue']:,.2f}"],
            ["Total Keuntungan", f"Rp {summary['total_profit']:,.2f}"],
            ["Margin Keuntungan", f"{summary['average_profit_margin']:.2f}%"]
        ]

        summary_table = Table(summary_data, colWidths=[8*cm, 8*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(summary_table)
    else:
        elements.append(Paragraph("Tidak ada data ringkasan tersedia", indo_style))

    elements.append(Spacer(1, 1*cm))

    # Add top products section
    elements.append(Paragraph("Produk Terlaris", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    if top_products:
        # Create data for top products table
        product_data = [["Produk", "Jumlah Terjual", "Pendapatan"]]

        for product in top_products:
            product_data.append([
                product['nama_produk'] if 'nama_produk' in product else 'N/A',
                str(product['total_quantity'] if 'total_quantity' in product else 0),
                f"Rp {float(product['total_revenue'] if 'total_revenue' in product else 0):,.2f}"
            ])

        product_table = Table(product_data, colWidths=[8*cm, 4*cm, 4*cm])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(product_table)
    else:
        elements.append(Paragraph("Tidak ada data produk tersedia", indo_style))

    elements.append(Spacer(1, 1*cm))

    # Add recent transactions
    elements.append(Paragraph("Transaksi Terbaru", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    if transaction_data:
        # Get only first 10 transactions
        recent_transactions = transaction_data[:10]

        # Create data for transactions table
        transaction_table_data = [["ID", "Tanggal", "Pendapatan", "Keuntungan"]]

        for transaction in recent_transactions:
            profit_info = profit_dict.get(transaction['id'], {})
            if isinstance(profit_info, dict):
                profit_value = profit_info.get('profit', 0)
            else:
                profit_value = profit_info['profit'] if 'profit' in profit_info else 0
            profit_value = 0 if profit_value is None else profit_value

            transaction_table_data.append([
                str(transaction['id']),
                transaction['tanggal'],
                f"Rp {transaction['total']:,.2f}",
                f"Rp {profit_value:,.2f}"
            ])

        transaction_table = Table(transaction_table_data, colWidths=[2*cm, 5*cm, 4*cm, 4*cm])
        transaction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(transaction_table)
    else:
        elements.append(Paragraph("Tidak ada data transaksi tersedia", indo_style))

    elements.append(Spacer(1, 1*cm))

    # Add category revenue
    if category_revenue:
        elements.append(Paragraph("Pendapatan per Kategori", heading_style))
        elements.append(Spacer(1, 0.3*cm))

        category_data = [["Kategori", "Pendapatan"]]

        for category in category_revenue:
            category_data.append([
                category['kategori'] if 'kategori' in category else 'Tidak terkategori',
                f"Rp {float(category['category_revenue'] if 'category_revenue' in category else 0):,.2f}"
            ])

        category_table = Table(category_data, colWidths=[8*cm, 8*cm])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(category_table)

    elements.append(Spacer(1, 2*cm))

    # Add footer with current time
    now = datetime.datetime.now()
    footer_text = f"Laporan ini dibuat secara otomatis pada {now.strftime('%d %B %Y, %H:%M')}"
    elements.append(Paragraph(footer_text, indo_style))
    elements.append(Paragraph("Aplikasi Fajar Julyana Analisis © 2025", indo_style))

    # Build PDF
    doc.build(elements)

    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()

    # Create response
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=laporan-pendapatan.pdf'

    return response
