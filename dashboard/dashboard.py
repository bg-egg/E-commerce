import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import urllib

sns.set(style='dark')

####Functions###

#Daily Orders Function
def create_daily_orders(df):
    daily_orders_df = df.resample (rule = 'D', on= 'order_purchase_timestamp').agg(order_count=('order_id', 'nunique'),
                                                                                   revenue=('payment_value','sum'))
    daily_orders_df= daily_orders_df.reset_index()
    return daily_orders_df
#Sum Order Function
def create_sum_orders(df):
    sum_orders_df = df.groupby(by='product_category_name_english').order_item_id.sum().sort_values(ascending=False).reset_index()
    return sum_orders_df
#By Payment Type Function
def create_payment_type(df):
    payment_type_df = df.groupby(by='payment_type').customer_unique_id.nunique().sort_values(ascending=False).reset_index()
    return payment_type_df
#By State Function
def create_customer_state(df):
    customer_state_df = df.groupby(by='customer_state').customer_unique_id.nunique().sort_values(ascending=False).reset_index()
    return customer_state_df
#RFM Function
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg(
        max_order_timestamp=("order_purchase_timestamp","max"), #mengambil tanggal order terakhir
        frequency=("order_id","nunique"),
        monetary= ("payment_value", "sum"))
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df
#Deploy Brazil Map


###INSERT MASTER DATA####

all_df = pd.read_csv('all_df.csv')
#Change "order_purchase_timestamp" datatype to DateTime
all_df["order_purchase_timestamp"]= pd.to_datetime(all_df["order_purchase_timestamp"])

###Code Slider for Sidebar###

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
#Data container for slider
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# Declare DataFrames
daily_orders_df = create_daily_orders(main_df)
sum_order_items_df = create_sum_orders(main_df)
payment_type_df = create_payment_type(main_df)
customer_state_df = create_customer_state(main_df)
mapping_df = main_df.drop_duplicates('customer_unique_id')
rfm_df = create_rfm_df(main_df)


###FRONT-END####
st.header('E-Commerce Dashboard :sparkles:')

# Sub Header 1#
st.subheader('Daily Orders')
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "USD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


# Sub Header 2#
st.subheader("Customer Informations")
#Customer by Payment Type Plot:
fig, ax = plt.subplots(figsize=(20, 15)) 
colors = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
        y="customer_unique_id", 
        x="payment_type",
        data=payment_type_df.sort_values(by="customer_unique_id", ascending=False),
        palette=colors,
        ax=ax
    )
ax.set_title("Number of Customer by Payment Type", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

 #Customer By State Plot:
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_unique_id", 
    y="customer_state",
    data=customer_state_df.sort_values(by="customer_state", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#Customer State by Map


#Sub Header 3#
st.subheader("RFM Analysis")
#RFM Figures:
fig,ax = plt.subplots(ncols=1 , nrows=3, figsize= (12,13))

sns.barplot(y='customer_unique_id',x='frequency',data= rfm_df.sort_values(by='frequency',ascending=False).head(5),ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title('Order Frequency', loc='center', fontsize = 15)

sns.barplot(y = 'customer_unique_id',x = 'recency',data =rfm_df.sort_values(by='customer_unique_id',ascending=True).head(5),ax = ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title('Order Recency (Days)', loc='center', fontsize = 15)

sns.barplot(y ='customer_unique_id',x ='monetary',data=rfm_df.sort_values(by='monetary',ascending=False).head(5),ax = ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title('Order Revenues', loc='center', fontsize =15)

plt.suptitle('RFM Analysis on E-Commerce Customers',fontsize =25)
st.pyplot(fig)
