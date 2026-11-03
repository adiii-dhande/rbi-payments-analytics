# RBI Payments Analytics

**An end-to-end banking analytics pipeline using publicly available Reserve Bank of India (RBI) payment-system data.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Analytics-4479A1?logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811?logo=powerbi&logoColor=black)
![Data Source](https://img.shields.io/badge/Data_Source-RBI-0B6E4F)
![Status](https://img.shields.io/badge/Status-In_Development-orange)

> **Project status:** In development. Only implemented and tested features are marked complete. No unverified performance or business-impact claims are made.

---

## 1. Overview

India's digital payment ecosystem includes multiple payment channels such as UPI, IMPS, NEFT, RTGS, and card-based transactions. Understanding their growth and contribution requires reliable data processing, consistent financial metrics, and structured analytical reporting.

**RBI Payments Analytics** is a data analytics project designed to transform publicly available RBI payment-system statistics into structured, validated, and analysis-ready datasets.

The project follows an end-to-end analytical workflow:

**RBI Data → Python ETL → Data Validation → PostgreSQL → SQL Analytics → Power BI**

The objective is to demonstrate practical banking-data analytics, financial KPI development, database management, and business intelligence reporting.

## 2. Business Problem

Banking payment statistics are published across different datasets, reporting periods, and payment categories. Analyzing them independently makes it difficult to:

- Compare the growth of different digital payment channels.
- Identify changes in transaction volume and monetary value.
- Understand digital payment adoption patterns.
- Analyze monthly and yearly payment trends.
- Maintain consistent and reliable analytical datasets.
- Generate consolidated reports for financial analysis.

### Proposed Solution

Build a centralized analytics pipeline that:

1. Collects publicly available RBI payment-system datasets.
2. Cleans and standardizes financial records using Python.
3. Validates data types, missing values, duplicates, and reporting periods.
4. Loads structured datasets into PostgreSQL.
5. Uses SQL to calculate financial and operational KPIs.
6. Connects Power BI to the analytical database for interactive reporting.

## 3. Data Sources

**Primary source:** [Reserve Bank of India – Database on Indian Economy](https://data.rbi.org.in/)

Potential datasets include:

| Dataset | Analytical purpose |
|---|---|
| RBI Payment System Indicators | Payment transaction volume and value |
| UPI Statistics | Digital payment growth |
| NEFT Statistics | Electronic funds transfer trends |
| RTGS Statistics | High-value payment activity |
| IMPS Statistics | Immediate interbank transfer trends |
| Card Payment Statistics | Debit and credit card usage |

> Include only datasets actually downloaded and processed in this repository. Dataset availability, historical coverage, and reporting frequency may differ.

### Data Characteristics

| Attribute | Description |
|---|---|
| Source | Reserve Bank of India |
| Data type | Structured financial statistics |
| Reporting frequency | Monthly / Annual, depending on dataset |
| Geography | India |
| Measures | Transaction volume and monetary value |
| Data nature | Public aggregate statistics |

## 4. System Architecture

```mermaid
flowchart TD
    A["RBI Public Data Sources"] --> B["Data Ingestion"]
    B --> C["Python ETL Pipeline"]
    C --> D["Data Cleaning and Standardization"]
    D --> E["Data Quality Validation"]
    E --> F["PostgreSQL Database"]
    F --> G["SQL Transformations and KPI Layer"]
    G --> H["Power BI Dashboard"]
    E --> I["Validation Logs and Exceptions"]
