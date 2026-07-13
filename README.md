🏭 RMG Supply Chain ETL & Analysis Pipeline
An end-to-end ETL pipeline and financial analysis project for a fast-fashion RMG (Ready-Made Garments) supply chain — processing 82,000+ order records across 5 factories, 40 products, and multiple warehouse routes to derive operational KPIs and business insights.


Built to mirror real-world MIS and supply chain reporting in the RMG/apparel industry.
📌 Project Highlights

MetricValueTotal Records Processed82,463 ordersTotal Revenue Analysed$2.73 BillionGross Profit Margin43%Date RangeApr 2023 – Jan 2024Source Tables4 relational CSVsOutput Tables4 clean summary tablesCharts Generated5 business insight visuals


🗂️ Project Structure

rmg-supply-chain-etl/
│
├── data/
│   ├── raw/                    # Source CSV files (4 tables)
│   │   ├── Log_Data.csv
│   │   ├── Production_Costs.csv
│   │   ├── Products.csv
│   │   └── Warehouse_Shipping_Costs.csv
│   └── processed/              # ETL output (auto-generated)
│       ├── master_fact_table.csv
│       ├── monthly_summary.csv
│       ├── product_summary.csv
│       └── factory_summary.csv
│
├── etl/
│   └── pipeline.py             # ETL pipeline script
│
├── analysis/
│   └── analysis.ipynb          # EDA & business insights notebook
│
└── outputs/                    # Generated charts (5 visuals)


🔄 ETL Pipeline Architecture

RAW DATA (4 CSVs)
│
├── Log_Data.csv        → 82,463 order records (shipments, sales, returns)
├── Production_Costs.csv → Factory × Product manufacturing cost
├── Products.csv         → Product master (name, price, weight)
└── Warehouse_Shipping   → Shipping cost per factory-warehouse route
│
▼
[EXTRACT]  Load all 4 source tables with validation logging
│
▼
[TRANSFORM]
  ├── Clean & standardise column names
  ├── Parse and extract date dimensions (Month, Year)
  ├── Rename keys for consistent joining
  ├── Derive Delay_Days & Is_Delayed flag
  ├── Calculate Return_Rate per order
  ├── JOIN all 4 tables → star schema (82,463 × 30 cols)
  └── Calculate financials:
       Revenue = Units Sold × Selling Price
       Prod Cost = Units × Manufacturing Cost
       Ship Cost = Units × Shipping Cost Per Unit
       Gross Profit = Revenue − Total Cost
       Profit Margin % = Gross Profit / Revenue
│
▼
[LOAD]  Save master fact table + 3 pre-aggregated summary tables

Pipeline runtime: < 2 seconds for 82,463 records


▶️ How to Run

1. Install dependencies

bashpip install pandas numpy matplotlib seaborn

2. Place raw CSVs in data/raw/

3. Run the ETL pipeline

bashcd etl
python pipeline.py

Expected output:

[14:38:23] === RMG Supply Chain ETL Pipeline Started ===
[14:38:23] EXTRACT: Loading raw CSV files...
[14:38:23]   Log_Data:    (82463, 12)
[14:38:23]   Prod_Costs:  (159, 3)
[14:38:23]   Products:    (40, 5)
[14:38:23]   Shipping:    (386, 4)
[14:38:23] TRANSFORM: Cleaning and enriching data...
[14:38:23]   Master table shape: (82463, 30)
[14:38:23]   Nulls in key cols: {'Total_Revenue': 0, 'Gross_Profit': 0, 'Profit_Margin_%': 0}
[14:38:23] LOAD: Saving processed data...
[14:38:25]   Saved: master_fact_table.csv (82,463 rows)
[14:38:25]   Saved: monthly_summary.csv, product_summary.csv, factory_summary.csv
[14:38:25] === Pipeline Complete ✓ ===

4. Run the analysis notebook

Open analysis/analysis.ipynb in VS Code or Jupyter and run all cells.

🛠️ Technical Skills Demonstrated

SkillImplementationETL Pipeline DesignExtract → Transform → Load with timestamped loggingData ModellingStar schema join across 4 relational tablesFinancial KPI DerivationRevenue, COGS, Gross Profit, Margin calculated from raw dataSupply Chain AnalyticsDelay rate, return rate, factory performance scoringPython / Pandas82K row dataset — merges, aggregations, derived columnsData Visualisation5 publication-quality charts with Matplotlib & SeabornBusiness StorytellingInsights framed as actionable findings, not just numbers


💼 Industry Relevance

This project directly mirrors operational MIS and reporting workflows in the RMG/apparel industry:


Log_Data → equivalent to WFX shipment/order transaction log
Production_Costs → equivalent to SAP FICO cost centre data
Products → equivalent to product master in ERP
Star schema join → equivalent to consolidated MIS reporting across multiple ERP sources



👤 Author

Asif Mahmud Chowdhury
Senior Finance Executive — MIS & Business Analysis | Indochine International
