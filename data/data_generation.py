# Install Faker if not already installed
import subprocess
try:
    import faker
except ImportError:
    print("Installing Faker...")
    subprocess.check_call(["pip", "install", "Faker"])
    import faker

import pandas as pd
import numpy as np
import random
import string
import itertools
from faker import Faker
import datetime
import os

fake = Faker('sv_SE')
np.random.seed(42)
random.seed(42)

# --- SETTINGS ---
DATE_FORMAT = "%Y-%m-%d"
WAREHOUSE_DIR = '/content/Files' # Ensure this directory exists and contains reference CSVs, or adjust path.

# --- TIME FRAME ---
start_date = pd.to_datetime('2025-07-07').normalize()
end_date = pd.to_datetime('2025-10-24').normalize()

all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
all_dates = [d for d in all_dates if d.weekday() < 5]  # Mon–Fri only

# --- SWEDISH CITIES/REGIONS ---
# Placeholder for `swedish_cities` if it's not defined in your base data files:
swedish_cities = [
    ('Stockholm', 'Stockholm', 59.3293, 18.0686),
    ('Gothenburg', 'Västra Götaland', 57.7089, 11.9746),
    ('Malmö', 'Skåne', 55.60498, 13.00382),
    ('Uppsala', 'Uppsala', 59.8586, 17.6389),
    ('Linköping', 'Östergötland', 58.4108, 15.6214),
    ('Västerås', 'Västmanland', 59.6163, 16.5528),
    ('Örebro', 'Örebro', 59.2745, 15.2066),
    ('Helsingborg', 'Skåne', 56.0465, 12.6946),
    ('Jönköping', 'Jönköping', 57.7816, 14.1618),
    ('Norrköping', 'Östergötland', 58.5943, 16.1826)
]

def random_city():
    return random.choice(swedish_cities)
def fake_phone():
    return fake.phone_number()

# --- Load Existing Data ---
# Ensure these CSV files exist in WAREHOUSE_DIR before running, or adapt for initial generation
building_customers_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Building_Customers.csv'))
grocery_customers_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Customers.csv'))
suppliers_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Suppliers.csv'))
building_items_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Building_Items.csv'))
grocery_items_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Items.csv'))
building_aisles_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Building_Aisles.csv'))
grocery_aisles_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Aisles.csv'))
drivers_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'TruckDrivers.csv'))
routes_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'DeliveryRoutes.csv'))
employees_df = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Employees.csv'))

# Extract picker IDs from existing employees_df
grocery_frozen_pickers = employees_df[(employees_df['Department'] == 'Grocery') & (employees_df['AssignedSection'] == 'Frozen')]['EmployeeID'].tolist()
grocery_drycold_pickers = employees_df[(employees_df['Department'] == 'Grocery') & (employees_df['AssignedSection'] == 'Dry/Cold')]['EmployeeID'].tolist()
perm_frozen_pickers = grocery_frozen_pickers # Assuming permanent frozen pickers are all frozen pickers in the loaded data

# --- Helper Functions for Order/Line IDs ---
def generate_order_id(prefix, date, seq):
    return f"{prefix}{date.strftime('%y%m%d')}{str(seq).zfill(4)}"
def generate_orderline_id(order_id, line_seq):
    return f"{order_id}_L{str(line_seq).zfill(3)}"

def random_priority():
    return random.choices(['Normal', 'Rush', 'Backorder'], weights=[0.80, 0.12, 0.08])[0]
def random_picking_status():
    return random.choices(['On Time', 'Delayed'], weights=[0.96, 0.04])[0]

order_statuses = ['Cancelled', 'Delayed Delivery', 'Delivered', 'Pending']
# Adjusted probabilities based on user feedback and to reduce 'Pending' significantly
order_status_probabilities = [0.01, 0.19, 0.79, 0.01]

pick_statuses = ['Picked', 'Error', 'Short']

# --- Robust Order Generation for All Departments/Sections ---
summary_rows = []

sections = {
    "Building": {
        "orders_dict": {},
        "orderlines_dict": {},
        "order_seq": 1,
        "min_orders_per_day": 5
    },
    "Grocery_DryCold": {
        "orders_dict": {},
        "orderlines_dict": {},
        "order_seq": 1,
        "min_orders_per_day": 10
    },
    "Grocery_Frozen": {
        "orders_dict": {},
        "orderlines_dict": {},
        "order_seq": 1,
        "min_orders_per_day": 3
    }
}

for date in all_dates:
    weekday = date.weekday() # Monday is 0, Friday is 4

    # --- Section Parameters ---
    # Adjust order/line counts based on weekday (Monday busiest, decreasing to Friday)
    if weekday == 0: # Monday
        building_orders_target = random.randint(40, 65)
        building_lines_target = random.randint(1600, 2800)
        drycold_orders_target = random.randint(90, 120)
        drycold_lines_target = random.randint(3500, 5500)
        frozen_orders_target = random.randint(15, 30)
        frozen_lines_target = random.randint(120, 220)
    elif weekday == 1: # Tuesday
        building_orders_target = random.randint(32, 55)
        building_lines_target = random.randint(1200, 2200)
        drycold_orders_target = random.randint(70, 95)
        drycold_lines_target = random.randint(2500, 4200)
        frozen_orders_target = random.randint(12, 25)
        frozen_lines_target = random.randint(90, 170)
    elif weekday == 2: # Wednesday
        building_orders_target = random.randint(28, 50)
        building_lines_target = random.randint(850, 1700)
        drycold_orders_target = random.randint(60, 80)
        drycold_lines_target = random.randint(1700, 3000)
        frozen_orders_target = random.randint(10, 18)
        frozen_lines_target = random.randint(75, 140)
    elif weekday == 3: # Thursday
        building_orders_target = random.randint(22, 40)
        building_lines_target = random.randint(600, 1200)
        drycold_orders_target = random.randint(50, 65)
        drycold_lines_target = random.randint(1000, 2000)
        frozen_orders_target = random.randint(8, 16)
        frozen_lines_target = random.randint(50, 100)
    else: # Friday (weekday == 4)
        building_orders_target = random.randint(15, 28)
        building_lines_target = random.randint(350, 700)
        drycold_orders_target = random.randint(40, 55)
        drycold_lines_target = random.randint(800, 1200)
        frozen_orders_target = random.randint(7, 12)
        frozen_lines_target = random.randint(35, 70)

    section_params = [
        ("Building", "Dry/Cold", building_orders_target, building_lines_target, "Building", "BO", building_items_df, list(employees_df[employees_df['Department'] == 'Building']['EmployeeID'])),
        ("Grocery", "Dry/Cold", drycold_orders_target, drycold_lines_target, "Grocery_DryCold", "GO", grocery_items_df[grocery_items_df['SubCategory'].isin(['Dry', 'Cold', 'Drinks', 'Pantry & Dry Goods', 'Dairy & Chilled', 'Beverages', 'Grains & Cereals', 'Snacks & Sweets', 'Hot Beverages', 'Other Dry', 'Dairy', 'Deli & Proteins', 'Chilled Juice', 'Other Chilled', 'Juice', 'Soft Drinks', 'Bottled Water', 'Energy Drinks', 'Other Drinks'])], grocery_drycold_pickers),
        ("Grocery", "Frozen", frozen_orders_target, frozen_lines_target, "Grocery_Frozen", "GF", grocery_items_df[grocery_items_df['SubCategory'].isin(['Frozen', 'Frozen Foods', 'Frozen Proteins', 'Frozen Veg', 'Ice Cream', 'Frozen Snacks', 'Other Frozen'])], perm_frozen_pickers),
    ]

    for dept, section, orders_target, lines_target, key, prefix, items_df, picker_pool in section_params:
        sec = sections[key]
        current_day_orders = []

        num_new_orders_to_generate = random.randint(orders_target - 5, orders_target + 5)
        num_new_orders_to_generate = max(sec['min_orders_per_day'], num_new_orders_to_generate)

        avg_lines_per_new_order = max(1, int(lines_target / max(1, num_new_orders_to_generate))) if num_new_orders_to_generate else 1


        for _ in range(num_new_orders_to_generate):
            cust = (grocery_customers_df if dept == 'Grocery' else building_customers_df).sample(1).iloc[0]
            status = np.random.choice(order_statuses, p=order_status_probabilities)
            lines_in_order = max(1, int(np.random.normal(avg_lines_per_new_order, 4)))
            picker = random.choice(picker_pool) if picker_pool else ''
            driver = drivers_df.sample(1).iloc[0]
            route = routes_df.sample(1).iloc[0]
            order_id = generate_order_id(prefix, date, sec['order_seq'])
            sec['order_seq'] += 1
            planned_delivery = date + pd.Timedelta(days=random.randint(1, 3))
            actual_delivery = planned_delivery + pd.Timedelta(days=random.choices([0, 0, 1], [0.7, 0.2, 0.1])[0]) if status in ['Delivered', 'On Time Delivery', 'Delayed Delivery'] else pd.NaT

            pick_start = datetime.datetime.combine(date, datetime.time(6 if dept=='Grocery' else 7, random.randint(0, 59)))
            pick_end = pick_start + datetime.timedelta(minutes=int(np.random.normal(lines_in_order * 2, 4)))

            order = {
                'OrderID': order_id,
                'CustomerID': cust['CustomerID'],
                'OrderDate': date,
                'OrderType': random_priority(),
                'OrderPriority': random_priority(),
                'OrderStatus': status,
                'PickingStatus': random_picking_status(),
                'PlannedDeliveryDate': planned_delivery,
                'ActualDeliveryDate': actual_delivery,
                'PickStartTime': pick_start,
                'PickEndTime': pick_end,
                'TruckDriverID': driver['TruckDriverID'],
                'RouteID': route['RouteID'],
                'TotalOrderValue': round(np.random.uniform(500, 30000), 2),
                'PickedByEmployeeID': picker,
                'Section': section,
                'Department': dept,
                'OrderLines': []
            }
            for l in range(lines_in_order):
                item = items_df.sample(1).iloc[0]
                pick_status = random.choices(pick_statuses, weights=[0.97, 0.02, 0.01])[0]
                qty = int(np.random.uniform(1, 15))
                line_id = generate_orderline_id(order_id, l + 1)
                line = {
                    'OrderLineID': line_id,
                    'OrderID': order_id,
                    'OrderDate': date,
                    'ItemID': item['ItemID'],
                    'Quantity': qty,
                    'UnitOfMeasure': item['UnitOfMeasure'],
                    'WarehouseAisleID': item['AisleID'],
                    'PickStatus': pick_status,
                    'PickedByEmployeeID': picker,
                    'Weight': item['Weight'],
                    'LineWeight': qty * item['Weight']
                }
                sec['orderlines_dict'][line_id] = line
                order['OrderLines'].append(line)
            current_day_orders.append(order)

        for order in current_day_orders:
             if order['OrderDate'] == date:
                 sec['orders_dict'][order['OrderID']] = order


        summary_rows.append({
            'Date': date.strftime(DATE_FORMAT),
            'Department': dept,
            'Section': section,
            'OrdersForTheDay': len([o for o in sec['orders_dict'].values() if o['OrderDate'] == date]),
            'ArrearsFromPrevDay': 0,
            'TotalItemsToPick': sum(len(order['OrderLines']) for order in sec['orders_dict'].values() if order['OrderDate'] == date),
            'Notes': "Arrears logic removed."
        })


# --- DataFrames & Export ---
building_orders_df_new = pd.DataFrame([dict(order, OrderLines=None) for order in sections['Building']['orders_dict'].values()])
building_orderlines_df_new = pd.DataFrame(list(sections['Building']['orderlines_dict'].values()))
grocery_drycold_orders_df_new = pd.DataFrame([dict(order, OrderLines=None) for order in sections['Grocery_DryCold']['orders_dict'].values()])
grocery_drycold_orderlines_df_new = pd.DataFrame(list(sections['Grocery_DryCold']['orderlines_dict'].values()))
grocery_frozen_orders_df_new = pd.DataFrame([dict(order, OrderLines=None) for order in sections['Grocery_Frozen']['orders_dict'].values()])
grocery_frozen_orderlines_df_new = pd.DataFrame(list(sections['Grocery_Frozen']['orderlines_dict'].values()))
summary_df_new = pd.DataFrame(summary_rows)

# Convert date columns to datetime and then format back to date strings, removing time component
date_cols = ['OrderDate', 'PlannedDeliveryDate', 'ActualDeliveryDate']
for df in [building_orders_df_new, grocery_drycold_orders_df_new, grocery_frozen_orders_df_new]:
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime(DATE_FORMAT)

# Convert OrderDate in orderlines dataframes to date objects
for df in [building_orderlines_df_new, grocery_drycold_orderlines_df_new, grocery_frozen_orderlines_df_new]:
    if 'OrderDate' in df.columns:
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce').dt.date


# Load existing data and append new data, then remove duplicates based on OrderID and OrderLineID
try:
    building_orders_df_existing = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Building_Orders.csv'))
    building_orders_df = pd.concat([building_orders_df_existing, building_orders_df_new], ignore_index=True)
    building_orders_df = building_orders_df.drop_duplicates(subset=['OrderID'], keep='first')
except FileNotFoundError:
    building_orders_df = building_orders_df_new

try:
    building_orderlines_df_existing = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Building_OrderLines.csv'))
    building_orderlines_df = pd.concat([building_orderlines_df_existing, building_orderlines_df_new], ignore_index=True)
    building_orderlines_df = building_orderlines_df.drop_duplicates(subset=['OrderLineID'], keep='first')
except FileNotFoundError:
    building_orderlines_df = building_orderlines_df_new

try:
    grocery_drycold_orders_df_existing = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_DryCold_Orders.csv'))
    grocery_drycold_orders_df = pd.concat([grocery_drycold_orders_df_existing, grocery_drycold_orders_df_new], ignore_index=True)
    grocery_drycold_orders_df = grocery_drycold_orders_df.drop_duplicates(subset=['OrderID'], keep='first')
except FileNotFoundError:
    grocery_drycold_orders_df = grocery_drycold_orders_df_new

try:
    grocery_drycold_orderlines_df_existing = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_DryCold_OrderLines.csv'))
    grocery_drycold_orderlines_df = pd.concat([grocery_drycold_orderlines_df_existing, grocery_drycold_orderlines_df_new], ignore_index=True)
    grocery_drycold_orderlines_df = grocery_drycold_orderlines_df.drop_duplicates(subset=['OrderLineID'], keep='first')
except FileNotFoundError:
    grocery_drycold_orderlines_df = grocery_drycold_orderlines_df_new

try:
    grocery_frozen_orders_df_existing = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Frozen_Orders.csv'))
    grocery_frozen_orders_df = pd.concat([grocery_frozen_orders_df_existing, grocery_frozen_orders_df_new], ignore_index=True)
    grocery_frozen_orders_df = grocery_frozen_orders_df.drop_duplicates(subset=['OrderID'], keep='first')
except FileNotFoundError:
    grocery_frozen_orders_df = grocery_frozen_orders_df_new

try:
    grocery_frozen_orderlines_df_existing = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Frozen_OrderLines.csv'))
    grocery_frozen_orderlines_df = pd.concat([grocery_frozen_orderlines_df_existing, grocery_frozen_orderlines_df_new], ignore_index=True)
    grocery_frozen_orderlines_df = grocery_frozen_orderlines_df.drop_duplicates(subset=['OrderLineID'], keep='first')
except FileNotFoundError:
    grocery_frozen_orderlines_df = grocery_frozen_orderlines_df_new

try:
    summary_df_existing = pd.read_csv(os.path.join(WAREHOUSE_DIR, 'Daily_Summary.csv'))
    summary_df = pd.concat([summary_df_existing, summary_df_new], ignore_index=True)
except FileNotFoundError:
    summary_df = summary_df_new


os.makedirs(WAREHOUSE_DIR, exist_ok=True)
building_customers_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Building_Customers.csv'), index=False)
grocery_customers_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Customers.csv'), index=False)
suppliers_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Suppliers.csv'), index=False)
building_items_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Building_Items.csv'), index=False)
grocery_items_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Items.csv'), index=False)
building_aisles_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Building_Aisles.csv'), index=False)
grocery_aisles_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Aisles.csv'), index=False)
drivers_df.to_csv(os.path.join(WAREHOUSE_DIR, 'TruckDrivers.csv'), index=False)
routes_df.to_csv(os.path.join(WAREHOUSE_DIR, 'DeliveryRoutes.csv'), index=False)
employees_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Employees.csv'), index=False)
building_orders_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Building_Orders.csv'), index=False)
building_orderlines_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Building_OrderLines.csv'), index=False)
grocery_drycold_orders_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_DryCold_Orders.csv'), index=False)
grocery_drycold_orderlines_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_DryCold_OrderLines.csv'), index=False)
grocery_frozen_orders_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Frozen_Orders.csv'), index=False)
grocery_frozen_orderlines_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Grocery_Frozen_OrderLines.csv'), index=False)
summary_df.to_csv(os.path.join(WAREHOUSE_DIR, 'Daily_Summary.csv'), index=False)


print(f"All generated/updated files saved to {WAREHOUSE_DIR}.")

# --- Fix dates in Building_Orders.csv ---
print("Fixing dates in Building_Orders.csv...")
df = pd.read_csv(os.path.join(WAREHOUSE_DIR, "Building_Orders.csv"), parse_dates=['OrderDate','PlannedDeliveryDate','ActualDeliveryDate'])

mask_planned = df['PlannedDeliveryDate'] < df['OrderDate']
mask_actual = df['ActualDeliveryDate'] < df['OrderDate']

df.loc[mask_planned, 'PlannedDeliveryDate'] = df.loc[mask_planned, 'OrderDate'] + pd.to_timedelta(np.random.randint(1, 4, size=mask_planned.sum()), unit='D')
df.loc[mask_actual, 'ActualDeliveryDate'] = df.loc[mask_actual, 'PlannedDeliveryDate'] + pd.to_timedelta(np.random.randint(0, 2, size=mask_actual.sum()), unit='D')

df.to_csv(os.path.join(WAREHOUSE_DIR, "Building_Orders.csv"), index=False)
print("Building_Orders.csv dates fixed.")

# --- Fix dates in Grocery_DryCold_Orders.csv ---
print("Fixing dates in Grocery_DryCold_Orders.csv...")
df = pd.read_csv(os.path.join(WAREHOUSE_DIR, "Grocery_DryCold_Orders.csv"), parse_dates=['OrderDate','PlannedDeliveryDate','ActualDeliveryDate'])

mask_planned = df['PlannedDeliveryDate'] < df['OrderDate']
mask_actual = df['ActualDeliveryDate'] < df['OrderDate']

df.loc[mask_planned, 'PlannedDeliveryDate'] = df.loc[mask_planned, 'OrderDate'] + pd.to_timedelta(np.random.randint(1, 4, size=mask_planned.sum()), unit='D')
df.loc[mask_actual, 'ActualDeliveryDate'] = df.loc[mask_actual, 'PlannedDeliveryDate'] + pd.to_timedelta(np.random.randint(0, 2, size=mask_actual.sum()), unit='D')

df.to_csv(os.path.join(WAREHOUSE_DIR, "Grocery_DryCold_Orders.csv"), index=False)
print("Grocery_DryCold_Orders.csv dates fixed.")

# --- Fix dates in Grocery_Frozen_Orders.csv ---
print("Fixing dates in Grocery_Frozen_Orders.csv...")
df = pd.read_csv(os.path.join(WAREHOUSE_DIR, "Grocery_Frozen_Orders.csv"), parse_dates=['OrderDate','PlannedDeliveryDate','ActualDeliveryDate'])

mask_planned = df['PlannedDeliveryDate'] < df['OrderDate']
mask_actual = df['ActualDeliveryDate'] < df['OrderDate']

df.loc[mask_planned, 'PlannedDeliveryDate'] = df.loc[mask_planned, 'OrderDate'] + pd.to_timedelta(np.random.randint(1, 4, size=mask_planned.sum()), unit='D')
df.loc[mask_actual, 'ActualDeliveryDate'] = df.loc[mask_actual, 'PlannedDeliveryDate'] + pd.to_timedelta(np.random.randint(0, 2, size=mask_actual.sum()), unit='D')

df.to_csv(os.path.join(WAREHOUSE_DIR, "Grocery_Frozen_Orders.csv"), index=False)
print("Grocery_Frozen_Orders.csv dates fixed.")

# --- Fix cancelled orders in Grocery_Frozen_Orders.csv ---
print("Fixing cancelled orders in Grocery_Frozen_Orders.csv...")
df = pd.read_csv(os.path.join(WAREHOUSE_DIR, "Grocery_Frozen_Orders.csv"), parse_dates=['OrderDate','PlannedDeliveryDate','ActualDeliveryDate'])

mask_cancelled = df['OrderStatus'].str.lower() == 'cancelled'
df.loc[mask_cancelled, 'PlannedDeliveryDate'] = df.loc[mask_cancelled, 'OrderDate']
df.loc[mask_cancelled, 'ActualDeliveryDate'] = df.loc[mask_cancelled, 'OrderDate']
df['DeliveredFlag'] = (~mask_cancelled).astype(int)
df.to_csv(os.path.join(WAREHOUSE_DIR, "Grocery_Frozen_Orders.csv"), index=False)
print("Grocery_Frozen_Orders.csv cancelled orders fixed.")

# --- Fix cancelled orders in Grocery_DryCold_Orders.csv ---
print("Fixing cancelled orders in Grocery_DryCold_Orders.csv...")
df = pd.read_csv(os.path.join(WAREHOUSE_DIR, "Grocery_DryCold_Orders.csv"), parse_dates=['OrderDate','PlannedDeliveryDate','ActualDeliveryDate'])

mask_cancelled = df['OrderStatus'].str.lower() == 'cancelled'
df.loc[mask_cancelled, 'PlannedDeliveryDate'] = df.loc[mask_cancelled, 'OrderDate']
df.loc[mask_cancelled, 'ActualDeliveryDate'] = df.loc[mask_cancelled, 'OrderDate']
df['DeliveredFlag'] = (~mask_cancelled).astype(int)
df.to_csv(os.path.join(WAREHOUSE_DIR, "Grocery_DryCold_Orders.csv"), index=False)
print("Grocery_DryCold_Orders.csv cancelled orders fixed.")

# --- Fix cancelled orders in Building_Orders.csv ---
print("Fixing cancelled orders in Building_Orders.csv...")
df = pd.read_csv(os.path.join(WAREHOUSE_DIR, "Building_Orders.csv"), parse_dates=['OrderDate','PlannedDeliveryDate','ActualDeliveryDate'])

mask_cancelled = df['OrderStatus'].str.lower() == 'cancelled'
df.loc[mask_cancelled, 'PlannedDeliveryDate'] = df.loc[mask_cancelled, 'OrderDate']
df.loc[mask_cancelled, 'ActualDeliveryDate'] = df.loc[mask_cancelled, 'OrderDate']
df['DeliveredFlag'] = (~mask_cancelled).astype(int)
df.to_csv(os.path.join(WAREHOUSE_DIR, "Building_Orders.csv"), index=False)
print("Building_Orders.csv cancelled orders fixed.")

# --- Fix delivery status for all order files ---
print("Fixing delivery status for all order files...")
order_files = [
    os.path.join(WAREHOUSE_DIR, "Building_Orders.csv"),
    os.path.join(WAREHOUSE_DIR, "Grocery_DryCold_Orders.csv"),
    os.path.join(WAREHOUSE_DIR, "Grocery_Frozen_Orders.csv")
]

for file in order_files:
    df = pd.read_csv(file, parse_dates=['ActualDeliveryDate', 'PlannedDeliveryDate'])

    lastDate = pd.Timestamp("2025-07-04").normalize()

    mask_non_cancelled = df['OrderStatus'] != "Cancelled"

    mask_delayed = mask_non_cancelled & (df['ActualDeliveryDate'] > df['PlannedDeliveryDate'])
    df.loc[mask_delayed, 'OrderStatus'] = "Delayed Delivery"

    mask_on_time = mask_non_cancelled & (df['ActualDeliveryDate'] == df['PlannedDeliveryDate'])
    df.loc[mask_on_time, 'OrderStatus'] = "On Time Delivery"

    mask_pending = mask_non_cancelled & (df['PlannedDeliveryDate'] > lastDate) & (df['ActualDeliveryDate'] > lastDate)
    df.loc[mask_pending, 'OrderStatus'] = "Pending"

    mask_pending_status = df['OrderStatus'] == "Pending"
    df.loc[mask_pending_status, 'ActualDeliveryDate'] = df.loc[mask_pending_status, 'PlannedDeliveryDate']

    mask_cancelled = (df['OrderStatus'] == "Cancelled")
    df.loc[mask_cancelled, 'ActualDeliveryDate'] = pd.NaT

    df['DeliveredFlag'] = 0
    mask_delivered_or_ontime = (df['OrderStatus'] == 'Delivered') | (df['OrderStatus'] == 'On Time Delivery') | (df['OrderStatus'] == 'Delayed Delivery')
    df.loc[mask_delivered_or_ontime, 'DeliveredFlag'] = 1

    df.to_csv(file, index=False)
    print(f"Processed {file}")

print("All Orders tables have been corrected.")
