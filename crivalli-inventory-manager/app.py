import pandas as pd
import streamlit as st
from pathlib import Path
st.set_page_config(page_title="Crivalli | Inventory",layout="wide")
st.title("Crivalli | Inventory Planner")
st.info("This is a planning calculator, not a live inventory sync.")
up=st.file_uploader("Upload inventory CSV",type="csv")
df=pd.read_csv(up if up else Path(__file__).with_name("sample_inventory.csv"))
needed={"sku","product","stock_units","daily_sales_units","unit_cost"}
if not needed.issubset(df.columns):st.error("Required: "+", ".join(sorted(needed)));st.stop()
for c in ["stock_units","daily_sales_units","unit_cost"]:df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0).clip(lower=0)
lead=st.number_input("Supplier lead time (days)",1,180,14)
safety=st.number_input("Extra safety stock (days)",0,90,7)
df["reorder_point"]=(df.daily_sales_units*(lead+safety)).apply(lambda x:int(-(-x//1)))
df["suggested_order"]=(df.reorder_point-df.stock_units).clip(lower=0).astype(int)
df["days_of_stock"]=df.apply(lambda r:round(r.stock_units/r.daily_sales_units,1) if r.daily_sales_units>0 else None,axis=1)
df["stock_value"]=(df.stock_units*df.unit_cost).round(2)
st.metric("Inventory at cost",f"₹{df.stock_value.sum():,.0f}")
st.dataframe(df,use_container_width=True)
st.warning("Reorder flagged SKUs before stock reaches expected lead-time demand.")
st.download_button("Download reorder plan",df.to_csv(index=False).encode(),"crivalli_reorder_plan.csv","text/csv")
