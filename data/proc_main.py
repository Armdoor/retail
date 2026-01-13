import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def read_data(file_path):
    df = pd.read_excel(file_path, engine="calamine")
    return df


def clean(df):
    df = df.dropna(subset=['Customer ID'])
    df = df[df['Quantity'] > 0]
    df['Description'] = df['Description'].fillna('Unknown')
    df['Date'] = df['InvoiceDate'].dt.date
    df['Time'] = df['InvoiceDate'].dt.time
    return df

def analysis_clean(df, input):
    Q1 = df[input].quantile(0.25)
    Q3 = df[input].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    return lower_bound, upper_bound

def data_segmentation(df):
    df['line_revenue'] = df["Quantity"] * df["Price"]
    df = df.rename(columns={"Invoice": "order_id"})

    segmented_data = (df.groupby("order_id")
                       .agg(
                           order_datetime=("InvoiceDate", "min"),
                            customer_id=("Customer ID", "first"),
                            country=("Country", "first"),
                            order_revenue=("line_revenue", "sum"),
                            item_count=("Quantity", "sum"),
                            unique_products=("StockCode", "nunique")
                            ).reset_index()
                            .sort_values(["customer_id", "order_datetime"])
                    )

    segmented_data["order_number"] = (
        segmented_data
        .groupby("customer_id")
        .cumcount() + 1
    )

    dim_customers = (
        segmented_data.groupby("customer_id").agg(
            first_order_date=("order_datetime", "min"),
            total_orders=("order_id", "count"),
            total_revenue=("order_revenue", "sum")
           ).reset_index()
        )
    return segmented_data, dim_customers

def main():
    file_path = "/Users/akshitsanoria/Desktop/retail/data/raw.xlsx"
    df = read_data(file_path)
    df = clean(df)
    lb_price,ub_price = analysis_clean(df, "Price")
    lb_quant,ub_quant = analysis_clean(df, "Quantity")

    df_core = df[(df["Price"] <= ub_price) & (df["Quantity"] <= ub_quant)].copy()
    df_prem = df[df["Price"] > ub_price].copy()

    df_main_segmented, df_main_dim_customers  = data_segmentation(df)
    df_core_segmented, df_core_dim_customers  = data_segmentation(df_core)
    df_prem_segmented, df_prem_dim_customers  = data_segmentation(df_prem)
    return df_main_segmented, df_core_segmented, df_prem_segmented, df, df_core, df_prem, df_main_dim_customers, df_core_dim_customers,df_prem_dim_customers

if __name__ == "__main__":
    main_seg, core_seg, prem_seg, df_all, df_c, df_p,df_main_dim_customers, df_core_dim_customers,df_prem_dim_customers  = main()
    
    main_seg.to_csv('/Users/akshitsanoria/Desktop/retail/data/analysis/main_seg.csv')
    core_seg.to_csv('/Users/akshitsanoria/Desktop/retail/data/analysis/core_seg.csv')
    prem_seg.to_csv('/Users/akshitsanoria/Desktop/retail/data/analysis/prem_seg.csv')
    df_all.to_csv('/Users/akshitsanoria/Desktop/retail/data/analysis/df_all.csv')
    df_c.to_csv('/Users/akshitsanoria/Desktop/retail/data/analysis/df_c.csv')
    df_p.to_csv('/Users/akshitsanoria/Desktop/retail/data/analysis/df_p.csv')
    df_main_dim_customers.to_csv('/Users/akshitsanoria/Desktop/retail/data/analysis/df_main_dim_customers.csv')
    df_core_dim_customers.to_csv('/Users/akshitsanoria/Desktop/retail/data/analysis/df_core_dim_customers.csv')
    df_prem_dim_customers.to_csv('/Users/akshitsanoria/Desktop/retail/data/analysis/df_prem_dim_customers.csv')