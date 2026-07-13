import pandas as pd
import numpy as np
import os
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────
RAW_PATH = r"D:\OneDrive - Indochine Textiles BD Ltd\ETL\rmg-supply-chain-etl\data\raw/"
OUT_PATH = r"D:\OneDrive - Indochine Textiles BD Ltd\ETL\rmg-supply-chain-etl\data\processed/"
os.makedirs(OUT_PATH, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ── EXTRACT ─────────────────────────────────────────────
def extract():
    log("EXTRACT: Loading raw CSV files...")
    log_df       = pd.read_csv(RAW_PATH + "Log_Data.csv")
    prod_cost    = pd.read_csv(RAW_PATH + "Production_Costs.csv")
    products     = pd.read_csv(RAW_PATH + "Products.csv")
    shipping     = pd.read_csv(RAW_PATH + "Warehouse_Shipping_Costs.csv")
    log(f"  Log_Data:    {log_df.shape}")
    log(f"  Prod_Costs:  {prod_cost.shape}")
    log(f"  Products:    {products.shape}")
    log(f"  Shipping:    {shipping.shape}")
    return log_df, prod_cost, products, shipping

# ── TRANSFORM ────────────────────────────────────────────
def transform(log_df, prod_cost, products, shipping):
    log("TRANSFORM: Cleaning and enriching data...")

    # 1. Clean column names
    log_df.columns    = log_df.columns.str.strip().str.replace(' ', '_')
    shipping.columns  = shipping.columns.str.strip().str.replace(' ', '_')

    # 2. Parse dates
    log_df['Date'] = pd.to_datetime(log_df['Date'])
    log_df['Month'] = log_df['Date'].dt.to_period('M').astype(str)
    log_df['Year']  = log_df['Date'].dt.year

    # 3. Rename for clean joining
    log_df.rename(columns={'Source_Factory': 'Factory_ID',
                            'Dest._Warehouse': 'Warehouse_ID'}, inplace=True)
    shipping.rename(columns={'Source_Factory_ID': 'Factory_ID'}, inplace=True)

    # 4. Derive delay flag
    log_df['Delay_Days'] = log_df['Shipping_Time_(Actual)'] - log_df['Shipping_Time_(Expected)']
    log_df['Is_Delayed'] = (log_df['Delay_Days'] > 0).astype(int)

    # 5. Return rate
    log_df['Return_Rate'] = (
        log_df['No._of_Pieces_Returned'] / log_df['Total_No._of_Pieces']
    ).round(4)

    # 6. Join all tables → master fact table
    df = log_df.merge(products, on='Product_ID', how='left')
    df = df.merge(prod_cost, on=['Factory_ID', 'Product_ID'], how='left')
    df = df.merge(
        shipping[['Warehouse_ID','Factory_ID','Product_ID','Shipping_Cost_(per_1000_pieces)']],
        on=['Warehouse_ID','Factory_ID','Product_ID'], how='left'
    )

    # 7. Calculate financials
    df['Shipping_Cost_Per_Unit'] = df['Shipping_Cost_(per_1000_pieces)'] / 1000
    df['Total_Revenue']   = df['No._of_pieces_sold'] * df['Selling_Price']
    df['Total_Prod_Cost'] = df['Total_No._of_Pieces'] * df['Manufac_Cost']
    df['Total_Ship_Cost'] = df['Total_No._of_Pieces'] * df['Shipping_Cost_Per_Unit']
    df['Total_Cost']      = df['Total_Prod_Cost'] + df['Total_Ship_Cost']
    df['Gross_Profit']    = df['Total_Revenue'] - df['Total_Cost']
    df['Profit_Margin_%'] = (df['Gross_Profit'] / df['Total_Revenue']).round(4)

    log(f"  Master table shape: {df.shape}")
    log(f"  Nulls in key cols: {df[['Total_Revenue','Gross_Profit','Profit_Margin_%']].isnull().sum().to_dict()}")
    return df

# ── LOAD ─────────────────────────────────────────────────
def load(df):
    log("LOAD: Saving processed data...")

    # Full master table
    df.to_csv(OUT_PATH + "master_fact_table.csv", index=False)

    # Summary tables
    monthly = df.groupby('Month').agg(
        Revenue=('Total_Revenue','sum'),
        Profit=('Gross_Profit','sum'),
        Orders=('Order_ID','count'),
        Avg_Delay=('Delay_Days','mean'),
        Return_Rate=('Return_Rate','mean')
    ).reset_index()
    monthly.to_csv(OUT_PATH + "monthly_summary.csv", index=False)

    product = df.groupby(['Product_ID','Name']).agg(
        Revenue=('Total_Revenue','sum'),
        Profit=('Gross_Profit','sum'),
        Units_Sold=('No._of_pieces_sold','sum'),
        Avg_Margin=('Profit_Margin_%','mean')
    ).reset_index()
    product.to_csv(OUT_PATH + "product_summary.csv", index=False)

    factory = df.groupby('Factory_ID').agg(
        Orders=('Order_ID','count'),
        Avg_Prod_Cost=('Manufac_Cost','mean'),
        Delay_Rate=('Is_Delayed','mean'),
        Avg_Rating=('Avg._Batch_Rating','mean')
    ).reset_index()
    factory.to_csv(OUT_PATH + "factory_summary.csv", index=False)

    log(f"  Saved: master_fact_table.csv ({len(df):,} rows)")
    log(f"  Saved: monthly_summary.csv, product_summary.csv, factory_summary.csv")

# ── RUN ──────────────────────────────────────────────────
if __name__ == "__main__":
    log("=== RMG Supply Chain ETL Pipeline Started ===")
    log_df, prod_cost, products, shipping = extract()
    master_df = transform(log_df, prod_cost, products, shipping)
    load(master_df)
    log("=== Pipeline Complete ✓ ===")