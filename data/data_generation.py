# This cell contains the complete synthetic data generation logic.

!pip install Faker
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
WAREHOUSE_DIR = '/content/Files' # Use the correct path

# Number of entities to generate
NUM_BUILDING_CUSTOMERS = 35
NUM_GROCERY_CUSTOMERS = 65
NUM_SUPPLIERS = 40
NUM_BUILDING_ITEMS = 100
NUM_GROCERY_ITEMS = 200
NUM_BUILDING_AISLES = 15
NUM_GROCERY_AISLES_DRYCOLD = 25
NUM_GROCERY_AISLES_FROZEN = 10
NUM_DRIVERS = 30
NUM_EMPLOYEES = 80
NUM_ROUTES = 10 # Corrected from 12 to 10 to match len(swedish_cities)

# --- TIME FRAME ---
start_date = pd.to_datetime('2025-07-07').normalize() # Start from the last date in existing data
end_date = pd.to_datetime('2025-10-24').normalize() # End date as requested

all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
all_dates = [d for d in all_dates if d.weekday() < 5]  # Mon–Fri only

# --- SWEDISH CITIES/REGIONS ---
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

# --- Generate Master Data ---

# Customers
building_customers = []
for i in range(NUM_BUILDING_CUSTOMERS):
    city, _, _, _ = random_city()
    building_customers.append({
        'CustomerID': f'BC{i+1:03}',
        'CustomerName': fake.company(),
        'ContactPerson': fake.name(),
        'Address': fake.address(),
        'City': city,
        'Phone': fake_phone(),
        'Email': fake.email(),
        'CustomerType': 'Building'
    })
building_customers_df = pd.DataFrame(building_customers)

grocery_customers = []
for i in range(NUM_GROCERY_CUSTOMERS):
    city, _, _, _ = random_city()
    grocery_customers.append({
        'CustomerID': f'GC{i+1:03}',
        'CustomerName': fake.company(),
        'ContactPerson': fake.name(),
        'Address': fake.address(),
        'City': city,
        'Phone': fake_phone(),
        'Email': fake.email(),
        'CustomerType': 'Grocery'
    })
grocery_customers_df = pd.DataFrame(grocery_customers)

# Suppliers
suppliers = []
for i in range(NUM_SUPPLIERS):
    city, _, _, _ = random_city()
    suppliers.append({
        'SupplierID': f'S{i+1:03}',
        'SupplierName': fake.company(),
        'ContactPerson': fake.name(),
        'Address': fake.address(),
        'City': city,
        'Phone': fake_phone(),
        'Email': fake.email()
    })
suppliers_df = pd.DataFrame(suppliers)

# Aisles
building_aisles = []
for i in range(NUM_BUILDING_AISLES):
    building_aisles.append({'AisleID': f'BA{i+1:02}', 'AisleName': f'Building Aisle {i+1}', 'AisleType': random.choice(['Tools', 'Electrical', 'Plumbing', 'Paint', 'Hardware'])})
building_aisles_df = pd.DataFrame(building_aisles)

grocery_aisles = []
for i in range(NUM_GROCERY_AISLES_DRYCOLD):
    grocery_aisles.append({'AisleID': f'GD{i+1:02}', 'AisleName': f'Grocery Dry/Cold Aisle {i+1}', 'AisleType': random.choice(['Dry Goods', 'Beverages', 'Dairy', 'Chilled', 'Produce'])})
for i in range(NUM_GROCERY_AISLES_FROZEN):
    grocery_aisles.append({'AisleID': f'GF{i+1:02}', 'AisleName': f'Grocery Frozen Aisle {i+1}', 'AisleType': 'Frozen'})
grocery_aisles_df = pd.DataFrame(grocery_aisles)

# Items
building_item_categories = {'Tools': ['Hand Tools', 'Power Tools', 'Safety Gear'], 'Electrical': ['Cables', 'Outlets', 'Lighting'], 'Plumbing': ['Pipes', 'Faucets', 'Fittings']}
building_items = []
for i in range(NUM_BUILDING_ITEMS):
    category = random.choice(list(building_item_categories.keys()))
    subcategory = random.choice(building_item_categories[category])
    aisle_id = random.choice(building_aisles_df['AisleID'].tolist())
    building_items.append({
        'ItemID': f'BI{i+1:03}',
        'ItemName': fake.word().capitalize() + ' ' + subcategory.lower(),
        'Category': category,
        'SubCategory': subcategory,
        'UnitOfMeasure': random.choice(['pcs', 'box', 'set']),
        'Weight': round(np.random.uniform(0.1, 15.0), 2),
        'AisleID': aisle_id,
        'SupplierID': random.choice(suppliers_df['SupplierID'].tolist())
    })
building_items_df = pd.DataFrame(building_items)

grocery_item_categories = {
    'Dry/Cold': ['Pantry & Dry Goods', 'Beverages', 'Dairy & Chilled', 'Snacks & Sweets', 'Grains & Cereals'],
    'Frozen': ['Frozen Foods', 'Frozen Proteins', 'Ice Cream']
}
grocery_items = []
for i in range(NUM_GROCERY_ITEMS):
    category_type = random.choice(list(grocery_item_categories.keys()))
    subcategory = random.choice(grocery_item_categories[category_type])
    
    # Assign aisle based on category type
    if category_type == 'Dry/Cold':
        aisle_candidates = grocery_aisles_df[grocery_aisles_df['AisleType'] != 'Frozen']['AisleID'].tolist()
    else: # Frozen
        aisle_candidates = grocery_aisles_df[grocery_aisles_df['AisleType'] == 'Frozen']['AisleID'].tolist()

    aisle_id = random.choice(aisle_candidates) if aisle_candidates else ''

    grocery_items.append({
        'ItemID': f'GI{i+1:03}',
        'ItemName': fake.food_item().capitalize() if category_type == 'Grocery' else fake.word().capitalize(),
        'Category': 'Grocery',
        'SubCategory': subcategory,
        'UnitOfMeasure': random.choice(['pcs', 'pack', 'kg', 'g', 'L']),
        'Weight': round(np.random.uniform(0.05, 5.0), 2),
        'AisleID': aisle_id,
        'SupplierID': random.choice(suppliers_df['SupplierID'].tolist())
    })
grocery_items_df = pd.DataFrame(grocery_items)


# Employees
employment_types = ['Permanent', 'Temporary', 'Agency']
departments = ['Building', 'Grocery']
employees = []
grocery_frozen_pickers = []
grocery_drycold_pickers = []

for i in range(NUM_EMPLOYEES):
    dept = random.choice(departments)
    if dept == 'Grocery':
        assigned_section = random.choices(['Dry/Cold', 'Frozen'], weights=[0.7, 0.3])[0]
    else:
        assigned_section = '' # Building department employees don't have assigned sections in this context

    emp = {
        'EmployeeID': f'E{i+1:03}',
        'EmployeeName': fake.name(),
        'Address': fake.street_address(),
        'Phone': fake_phone(),
        'EmploymentDate': fake.date_between(start_date='-4y', end_date='-2w'),
        'EmploymentType': random.choice(employment_types),
        'Department': dept,
        'AssignedSection': assigned_section
    }
    employees.append(emp)
    if dept == 'Grocery':
        if assigned_section == 'Frozen':
            grocery_frozen_pickers.append(emp['EmployeeID'])
        elif assigned_section == 'Dry/Cold':
            grocery_drycold_pickers.append(emp['EmployeeID'])
employees_df = pd.DataFrame(employees)

perm_frozen_pickers = grocery_frozen_pickers # All frozen pickers are considered permanent for this simulation

# Truck Drivers & Routes
routes = []
route_cities_sample = random.sample(swedish_cities, k=NUM_ROUTES)
for i in range(NUM_ROUTES):
    start_city = route_cities_sample[i][0]
    end_city = random.choice([c[0] for c in swedish_cities if c[0] != start_city]) # Ensure different end city
    routes.append({
        'RouteID': f'R{i+1:03}',
        'RouteName': f"{start_city}-{end_city}",
        'StartLocation': start_city,
        'EndLocation': end_city,
        'DistanceKM': int(np.random.uniform(50, 800)),
        'TypicalDurationMins': int(np.random.uniform(60, 720))
    })
routes_df = pd.DataFrame(routes)

drivers = []
for i in range(NUM_DRIVERS):
    drivers.append({
        'TruckDriverID': f'TD{i+1:03}',
        'DriverName': fake.name(),
        'TruckPlate': fake.license_plate(),
        'AssignedRouteID': random.choice(routes_df['RouteID'].tolist())
    })
drivers_df = pd.DataFrame(drivers)


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
order_status_probabilities = [0.01, 0.19, 0.79, 0.01] # Reduced Pending probability significantly, adjusted others

pick_statuses = ['Picked', 'Error', 'Short']

# --- Robust Order Generation for All Departments/Sections ---
summary_rows = []

sections = {
    "Building": {
        "orders_dict": {},
        "orderlines_dict": {},
        "order_seq": 1, # Reset sequence for new dates
        "min_orders_per_day": 5 # Minimum new orders per day for Building
    },
    "Grocery_DryCold": {
        "orders_dict": {},
        "orderlines_dict": {},
        "order_seq": 1, # Reset sequence for new dates
        "min_orders_per_day": 10 # Minimum new orders per day for Grocery Dry/Cold
    },
    "Grocery_Frozen": {
        "orders_dict": {},
        "orderlines_dict": {},
        "order_seq": 1, # Reset sequence for new dates
        "min_orders_per_day": 3 # Minimum new orders per day for Grocery Frozen
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
        ("Grocery", "Dry/Cold", drycold_orders_target, drycold_lines_target, "Grocery_DryCold", "GO", grocery_items_df[grocery_items_df['SubCategory'].isin(['Pantry & Dry Goods', 'Beverages', 'Dairy & Chilled', 'Snacks & Sweets', 'Grains & Cereals'])], grocery_drycold_pickers), # Updated subcategories
        ("Grocery", "Frozen", frozen_orders_target, frozen_lines_target, "Grocery_Frozen", "GF", grocery_items_df[grocery_items_df['SubCategory'].isin(['Frozen Foods', 'Frozen Proteins', 'Ice Cream'])], perm_frozen_pickers), # Updated subcategories
    ]

    for dept, section, orders_target, lines_target, key, prefix, items_df, picker_pool in section_params:
        sec = sections[key]
        current_day_orders = []

        # Generate number of *new* orders for the day based on target
        num_new_orders_to_generate = random.randint(orders_target - 5, orders_target + 5) # Generate around the target
        num_new_orders_to_generate = max(sec['min_orders_per_day'], num_new_orders_to_generate) # Ensure minimum new orders are generated


        # Calculate average lines per *new* order based on target lines and NEW orders
        avg_lines_per_new_order = max(1, int(lines_target / max(1, num_new_orders_to_generate))) if num_new_orders_to_generate else 1


        for _ in range(num_new_orders_to_generate):
            cust = (grocery_customers_df if dept == 'Grocery' else building_customers_df).sample(1).iloc[0]
            # Assign status based on probabilities
            status = np.random.choice(order_statuses, p=order_status_probabilities) # Adjusted probabilities for the 4 statuses
            lines_in_order = max(1, int(np.random.normal(avg_lines_per_new_order, 2)))
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


        # Add all orders generated for the current day to the main orders_dict
        # Ensure we are adding and counting only the orders generated for 'date'
        for order in current_day_orders:
             if order['OrderDate'] == date: # Explicitly check if the order is for the current date
                 sec['orders_dict'][order['OrderID']] = order


        summary_rows.append({
            'Date': date.strftime(DATE_FORMAT),
            'Department': dept,
            'Section': section,
            'OrdersForTheDay': len([o for o in sec['orders_dict'].values() if o['OrderDate'] == date]), # Report total orders generated on the current day
            'ArrearsFromPrevDay': 0, # No arrears are carried over in this logic
            'TotalItemsToPick': sum(len(order['OrderLines']) for order in sec['orders_dict'].values() if order['OrderDate'] == date), # Report total lines for the day
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
            # Convert to datetime, coerce errors to NaT, then format to date string
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime(DATE_FORMAT)

# Convert OrderDate in orderlines dataframes to date objects
for df in [building_orderlines_df_new, grocery_drycold_orderlines_df_new, grocery_frozen_orderlines_df_new]:
    if 'OrderDate' in df.columns:
        # Convert to datetime, coerce errors to NaT, then extract date
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce').dt.date


# Load existing data and append new data, then remove duplicates based on OrderID and OrderLineID
# This section is modified to handle cases where files might not exist initially (when generating from scratch)

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
    # No need to drop duplicates for summary data based on OrderID or OrderLineID
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


print(f"All files saved to {WAREHOUSE_DIR}.")
print(f"Permanent frozen pickers for the new period: {perm_frozen_pickers}")
