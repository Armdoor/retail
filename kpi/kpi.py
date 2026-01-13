import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def read_data(file_path):
    df = pd.read_csv(file_path)
    return df

def kpi(df):
    total_revenue = df["order_revenue"].sum()
    aov = (
        df["order_revenue"].sum() /
        df["order_id"].nunique()
    )
    orders_per_customer = (
    df["order_id"].nunique() /
    df["customer_id"].nunique()
)
    revenue_per_customer = (
    df["order_revenue"].sum() /
    df["customer_id"].nunique()
)
    df["customer_type"] = np.where(
    df["order_number"] == 1,
    "New",
    "Returning"
)

    revenue_by_type = (
        df
        .groupby("customer_type")["order_revenue"]
        .sum()
    )
    df["order_month"] = (
    df["order_datetime"].dt.to_period("M")
)

    monthly_revenue = (
        df.groupby("order_month")["order_revenue"]
                .sum()
                .reset_index()
    )
    
    customer_revenue = (
    df.groupby("customer_id")["order_revenue"]
               .sum()
               .sort_values(ascending=False)
)

    top_10pct_revenue_share = (
        customer_revenue.head(int(0.1 * len(customer_revenue))).sum() /
        customer_revenue.sum()
    )

    df["order_month"] = (
    df["order_datetime"].dt.to_period("M")
)

    monthly_active_customers = (
        df
        .groupby("order_month")["customer_id"]
        .nunique()
        .reset_index(name="active_customers")
    )
    customer_orders = (
        df.groupby("customer_id")["order_id"]
                .nunique()
    )

    repeat_purchase_rate = (
        (customer_orders > 1).sum() / customer_orders.count()
    )

    df["cohort_month"] = (
        df.groupby("customer_id")["order_month"]
                .transform("min")
    )
    cohort_data = (
        df
        .groupby(["cohort_month", "order_month"])["customer_id"]
        .nunique()
        .reset_index()
    )
    cohort_data["cohort_index"] = (
        cohort_data["order_month"] - cohort_data["cohort_month"]
    ).apply(lambda x: x.n)

    cohort_pivot = cohort_data.pivot_table(
        index="cohort_month",
        columns="cohort_index",
        values="customer_id"
    )

    cohort_retention = cohort_pivot.divide(cohort_pivot.iloc[:, 0], axis=0)
    last_purchase = (
    df.groupby("customer_id")["order_datetime"]
               .max()
)

    analysis_date = df["order_datetime"].max()
    churn_threshold = analysis_date - pd.Timedelta(days=90)

    churned_customers = last_purchase[last_purchase < churn_threshold]

    churn_rate = (
        churned_customers.count() / last_purchase.count()
    )
    customer_ltv = (
    df.groupby("customer_id")["order_revenue"]
               .sum()
)

    average_ltv = customer_ltv.mean()
    kpi_dict = {
        "total_revenue": total_revenue,
        "aov": aov,
        "orders_per_customer": orders_per_customer,
        "revenue_per_customer": revenue_per_customer,
        "revenue_by_type": revenue_by_type,
        "monthly_revenue": monthly_revenue,
        "top_10pct_revenue_share": top_10pct_revenue_share,
        "monthly_active_customers": monthly_active_customers,
        "repeat_purchase_rate": repeat_purchase_rate,
        "cohort_retention": cohort_retention,
        "churn_rate": churn_rate,
        "average_ltv": average_ltv
    }
    return kpi_dict

def main():
    file_path = "/Users/akshitsanoria/Desktop/retail/data/analysis/core_seg.csv"
    df = read_data(file_path)
    kpi_dict = kpi(df)
    print(kpi_dict)
    return kpi_dict

if __name__ == "__main__":
    kpi_dict =main()
    kpi_dict["monthly_revenue"].to_csv('/Users/akshitsanoria/Desktop/retail/kpi/analysis/monthly_revenue.csv')
    kpi_dict["monthly_active_customers"].to_csv('/Users/akshitsanoria/Desktop/retail/kpi/analysis/monthly_active_customers.csv')
    kpi_dict["cohort_retention"].to_csv('/Users/akshitsanoria/Desktop/retail/kpi/analysis/cohort_retention.csv')