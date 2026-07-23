# FlowMotion-Logistix-PowerBI-Dashboard

A comprehensive Power BI analytics solution simulating warehouse 
logistics operations for a third-party logistics (3PL) environment.

## Project Overview

FlowMotion Logistix is a 7-page interactive Power BI report built 
as an app-style analytics platform for warehouse operations managers. 
It covers order flow, process analytics, error root cause analysis, 
picker performance benchmarking, and delivery patterns across two 
warehouse departments (Building and Grocery).

The dataset was synthetically generated using a custom Python script, 
designed to simulate realistic operational data for a 3PL warehouse 
environment. This approach allowed full control over the data model 
structure and ensured the semantic model could be built to reflect 
real warehouse data architecture.

## Data Model

The semantic model is built from multiple related tables:
- Orders
- Order Lines
- Products / Items (per department)
- Aisles
- Employees (Pickers)
- Delivery Routes
- Customers

Relationships follow a star schema pattern with Orders as the 
central fact table.

## Report Pages

| Page | Purpose |
|------|---------|
| Home | Navigation landing page |
| Overview | Executive KPI summary with map and trend visuals |
| Process Analytics | Order volume patterns, composition, and delivery benchmarks |
| Error Analysis | Error rate trends, product-level errors, and zone breakdown |
| Picker Analysis | Overall and comparative picker performance analysis |
| Table | Searchable order-level detail table |
| About | Project documentation and version history |

The report contains drillthrough pages accessible 
from data points on the main report pages.

## Drillthrough Pages

| Page | Purpose |
|------|---------|
| Order Analysis | Details about individual orders |
| Performance Profile | Individual picker performance analysis |
| Decomposition Tree | Error Root-Cause Analysis |

## Dashboard Preview

### Home
![Home Page](assets/screenshots/01_home.png)

### Overview
![Overview](assets/screenshots/02_overview.png)

### Process
![Overview](assets/screenshots/03_process.png)

### Errors
![Overview](assets/screenshots/03_errors.png)

## Key Findings

The following findings reflect the synthetic dataset.

**Overview**  
A 2% error rate across 5,577 orders appears manageable until 
applied to 1.3M items picked — producing 25,200 error instances. 
This reframes error rate as a material operational issue and 
motivates the deeper analysis in subsequent pages.

**Process Analytics**  
XL-size orders represent 86% of total volume, and Store section 
shows the highest pick time spread: P90 (113 mins) is 53% above 
its own median (74 mins). High-complexity orders are concentrating 
performance variance in a single section.

**Error Analysis**  
Medium-sized orders carry the highest error rate (2.61%) 
despite not being the dominant order type — error risk is 
disproportionate to volume. At product level, Spray Paint 
surfaces as the highest-error item.

**Picker Analysis**  
40 of 69 active pickers account for 80% of all picking errors 
(Pareto distribution). Critically, both picker speed/quantity 
and error rate show insignificant correlation (r = 0.20 and r = 0.00 
respectively), which shows speed/qty does not explain error patterns.

## Technical Stack

- **Power BI Desktop** — report development and data modelling
- **DAX** — measures and calculated columns
- **Power Query (M)** — data transformation and loading
- **Python** — synthetic data generation
- **Power BI Service** — publishing and sharing

## Key Features

- App-style navigation with persistent top nav bar and Home page cards
- Multi-table semantic model with star schema design
- Drillthrough pages for order-level and picker-level detail

## Data Notice

All data used in this project is synthetically generated and does 
not represent any real organisation, individual, or operational data. 
The project is intended for portfolio and educational purposes only.

## Author

**Nuhuman Abubakar**  
Data Analyst & BI Developer  
[LinkedIn](http://www.linkedin.com/in/nuhuman-abubakar)



