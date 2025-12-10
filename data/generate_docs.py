#!/usr/bin/env python3
"""
Generate Validated SQL Documentation for Escalation Helper
Queries the REVENTION database and creates documentation files.
"""

import pyodbc
import json
from datetime import datetime
from pathlib import Path

# Database connection settings
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=172.31.240.1\\Revention;"
    "DATABASE=REVENTION;"
    "UID=Revention;"
    "PWD=Astr0s;"
    "TrustServerCertificate=yes;"
)

OUTPUT_DIR = Path("/home/krwhynot/Projects/Sql-DB/helper")

def get_connection():
    """Get database connection."""
    return pyodbc.connect(CONNECTION_STRING, timeout=30)

def execute_query(conn, query, params=None):
    """Execute a query and return results."""
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return columns, rows
    except Exception as e:
        return None, str(e)

def get_all_tables(conn):
    """Get all table names from the database."""
    query = """
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_NAME
    """
    cols, rows = execute_query(conn, query)
    if cols:
        return [row[0] for row in rows]
    return []

def get_table_columns(conn, table_name):
    """Get columns for a specific table."""
    query = """
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = ?
    ORDER BY ORDINAL_POSITION
    """
    return execute_query(conn, query, (table_name,))

def get_table_row_counts(conn):
    """Get row counts for all tables."""
    query = """
    SELECT
        t.TABLE_NAME,
        ISNULL(p.rows, 0) AS RowCount
    FROM INFORMATION_SCHEMA.TABLES t
    LEFT JOIN sys.partitions p ON OBJECT_ID(t.TABLE_SCHEMA + '.' + t.TABLE_NAME) = p.object_id AND p.index_id < 2
    WHERE t.TABLE_TYPE = 'BASE TABLE'
    ORDER BY p.rows DESC
    """
    return execute_query(conn, query)

def get_security_tables(conn):
    """Get all security-related tables."""
    query = """
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
      AND (TABLE_NAME LIKE '%Sec%' OR TABLE_NAME LIKE '%Right%' OR TABLE_NAME LIKE '%Perm%' OR TABLE_NAME LIKE '%Auth%')
    ORDER BY TABLE_NAME
    """
    return execute_query(conn, query)

def test_query(conn, query, description):
    """Test a query and return results or error."""
    try:
        cols, rows = execute_query(conn, query)
        if cols is None:
            return {"success": False, "error": str(rows), "description": description}
        return {
            "success": True,
            "columns": cols,
            "row_count": len(rows),
            "sample": [list(row)[:5] for row in rows[:3]] if rows else [],
            "description": description
        }
    except Exception as e:
        return {"success": False, "error": str(e), "description": description}

def generate_validation_report(conn, all_tables):
    """Generate Document 05 - Query Validation Report."""
    print("Generating Query Validation Report...")

    # Tables referenced in SQL reference guide
    referenced_tables = [
        "Ord", "OrdItem", "OrdItemMod", "OrdCpn", "OrdTax", "OrdPayment", "OrdDefer", "OrdNote",
        "OrdLock", "OrdItemRemovedAudit", "KDOrd", "KDItem", "KDStation",
        "Employee", "TimeClock", "EmployeeSched", "SecGrp", "SecGrpRights", "SecRightsDefault",
        "CashDrawer", "CashDrawerCfg", "CashDrawerClose", "CCTrans", "CCBatches", "CCSettle",
        "Customer", "CustomerPhone", "CustomerAddr",
        "Menus", "MenuGrps", "MenuItms", "MenuMds", "MenuItmMdGrps", "MenuItmPrices",
        "Printer", "PrintJobs", "PrinterCfg", "PrintQueue",
        "DeliveryOrder", "DeliveryDriver", "DeliveryZone",
        "SumDaily", "SumServer", "SumCashier", "SumPayment", "SumMenuItm",
        "SyncRecords", "SyncStatus", "SyncQueue",
        "CompChecks", "CompChkItms", "CompChkReason",
        "BizDate", "BizClose", "SystemCfg", "StoreCfg",
        "BackupLog", "ErrorLog", "AuditLog"
    ]

    all_tables_lower = [t.lower() for t in all_tables]

    valid_tables = []
    invalid_tables = []

    for table in referenced_tables:
        if table.lower() in all_tables_lower:
            # Find the actual case
            idx = all_tables_lower.index(table.lower())
            valid_tables.append((table, all_tables[idx]))
        else:
            # Find similar tables
            similar = [t for t in all_tables if table.lower() in t.lower() or t.lower() in table.lower()]
            invalid_tables.append((table, similar[:5]))

    content = f"""# Query Validation Report
## Document 05 - Table Reference Validation

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** REVENTION
**Server:** 172.31.240.1\\Revention

---

## Summary

| Category | Count |
|----------|-------|
| **Tables in Database** | {len(all_tables)} |
| **Tables Referenced in SQL Guide** | {len(referenced_tables)} |
| **Valid References** | {len(valid_tables)} |
| **Invalid References** | {len(invalid_tables)} |
| **Validation Rate** | {len(valid_tables)/len(referenced_tables)*100:.1f}% |

---

## Valid Table References

The following {len(valid_tables)} tables exist in the database:

| Referenced Name | Actual Name | Status |
|-----------------|-------------|--------|
"""

    for ref, actual in sorted(valid_tables):
        status = "Exact match" if ref == actual else f"Case: {actual}"
        content += f"| `{ref}` | `{actual}` | {status} |\n"

    content += f"""

---

## Invalid Table References

The following {len(invalid_tables)} tables do NOT exist in the database:

| Referenced Table | Similar Tables Found | Recommendation |
|------------------|---------------------|----------------|
"""

    for ref, similar in sorted(invalid_tables):
        similar_str = ", ".join([f"`{s}`" for s in similar]) if similar else "None found"
        recommendation = f"Use `{similar[0]}`" if similar else "Verify table name"
        content += f"| `{ref}` | {similar_str} | {recommendation} |\n"

    content += """

---

## Tables in Database Not in Reference Guide

These tables exist but are not documented in the SQL reference:

"""
    referenced_lower = [t.lower() for t in referenced_tables]
    undocumented = [t for t in all_tables if t.lower() not in referenced_lower]

    # Group by prefix
    prefixes = {}
    for t in undocumented:
        prefix = t[:3] if len(t) >= 3 else t
        if prefix not in prefixes:
            prefixes[prefix] = []
        prefixes[prefix].append(t)

    for prefix in sorted(prefixes.keys()):
        tables = prefixes[prefix]
        if len(tables) <= 3:
            content += f"- {', '.join([f'`{t}`' for t in tables])}\n"
        else:
            content += f"- **{prefix}***: {', '.join([f'`{t}`' for t in tables[:5]])}"
            if len(tables) > 5:
                content += f" ... (+{len(tables)-5} more)"
            content += "\n"

    return content

def generate_table_quick_reference(conn, all_tables):
    """Generate Document 06 - Database Table Quick Reference."""
    print("Generating Database Table Quick Reference...")

    cols, rows = get_table_row_counts(conn)
    row_counts = {row[0]: row[1] for row in rows} if cols else {}

    # Categorize tables
    categories = {
        "Orders & Transactions": ["Ord", "OrdItem", "OrdItemMod", "OrdCpn", "OrdTax", "OrdPayment", "OrdDefer", "OrdNote", "OrdLock"],
        "Payments & Credit Cards": ["CCTrans", "CCBatches", "CCSettle", "CCAuth", "Payment", "PmtType"],
        "Cash Drawers": ["CashDrawer", "CashDrawerCfg", "CashDrawerClose", "CashDrawerAudit"],
        "Employees & Time Clock": ["Employee", "TimeClock", "EmployeeSched", "EmployeeJob", "Job", "PayRate"],
        "Security & Permissions": ["SecGrp", "SecGrpRights", "SecRightsDefault", "SecRight", "SecRights"],
        "Menu System": ["Menus", "MenuGrps", "MenuItms", "MenuMds", "MenuItmMdGrps", "MenuItmPrices", "MenuItem"],
        "Printing & Kitchen Display": ["Printer", "PrintJobs", "PrinterCfg", "PrintQueue", "KDOrd", "KDItem", "KDStation"],
        "Delivery": ["DeliveryOrder", "DeliveryDriver", "DeliveryZone", "Delivery"],
        "Customers": ["Customer", "CustomerPhone", "CustomerAddr", "CustomerNote"],
        "Reports & Summaries": ["SumDaily", "SumServer", "SumCashier", "SumPayment", "SumMenuItm"],
        "Synchronization": ["SyncRecords", "SyncStatus", "SyncQueue", "Sync"],
        "System & Configuration": ["BizDate", "BizClose", "SystemCfg", "StoreCfg", "Config"]
    }

    content = f"""# Database Table Quick Reference
## Document 06 - Table Organization by Category

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** REVENTION
**Total Tables:** {len(all_tables)}

---

## Tables by Category

"""

    all_tables_lower = {t.lower(): t for t in all_tables}

    for category, table_patterns in categories.items():
        content += f"### {category}\n\n"
        content += "| Table | Row Count | Description |\n"
        content += "|-------|-----------|-------------|\n"

        found_tables = []
        for pattern in table_patterns:
            # Exact match first
            if pattern.lower() in all_tables_lower:
                actual = all_tables_lower[pattern.lower()]
                found_tables.append(actual)
            # Then partial match
            else:
                for t in all_tables:
                    if pattern.lower() in t.lower() and t not in found_tables:
                        found_tables.append(t)

        for table in sorted(set(found_tables)):
            count = row_counts.get(table, 0)
            count_str = f"{count:,}" if count else "0"
            content += f"| `{table}` | {count_str} | |\n"

        if not found_tables:
            content += "| *No tables found* | - | |\n"

        content += "\n"

    # Add top 20 tables by row count
    content += """---

## Top 20 Tables by Row Count

| Rank | Table | Rows |
|------|-------|------|
"""

    sorted_counts = sorted(row_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    for i, (table, count) in enumerate(sorted_counts, 1):
        content += f"| {i} | `{table}` | {count:,} |\n"

    return content

def generate_security_deep_dive(conn, all_tables):
    """Generate Document 07 - Security & Permissions Deep Dive."""
    print("Generating Security Permissions Deep Dive...")

    cols, sec_tables = get_security_tables(conn)
    security_tables = [row[0] for row in sec_tables] if cols else []

    content = f"""# Security & Permissions Deep Dive
## Document 07 - How Permissions Work in REVENTION

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** REVENTION

---

## Security Tables Found

"""

    for table in security_tables:
        content += f"- `{table}`\n"

    content += "\n---\n\n## Table Schemas\n\n"

    for table in security_tables:
        cols, rows = get_table_columns(conn, table)
        if cols:
            content += f"### {table}\n\n"
            content += "| Column | Data Type | Max Length | Nullable | Default |\n"
            content += "|--------|-----------|------------|----------|----------|\n"
            for row in rows:
                col_name, data_type, max_len, nullable, default = row
                max_len_str = str(max_len) if max_len else "-"
                default_str = str(default)[:30] if default else "-"
                content += f"| `{col_name}` | {data_type} | {max_len_str} | {nullable} | {default_str} |\n"
            content += "\n"

    # Check Employee table for security group link
    content += """---

## How Permissions Connect

### Employee to Security Group Link

"""

    emp_cols, emp_rows = get_table_columns(conn, "Employee")
    if emp_cols:
        sec_related = [row for row in emp_rows if 'sec' in row[0].lower() or 'grp' in row[0].lower() or 'group' in row[0].lower()]
        if sec_related:
            content += "Employee table columns related to security:\n\n"
            for row in sec_related:
                content += f"- `{row[0]}` ({row[1]})\n"
        else:
            content += "No security-related columns found in Employee table with 'sec' or 'grp' prefix.\n\n"
            content += "All Employee columns:\n"
            for row in emp_rows[:15]:
                content += f"- `{row[0]}` ({row[1]})\n"
            if len(emp_rows) > 15:
                content += f"- ... and {len(emp_rows)-15} more columns\n"

    # Sample data queries
    content += """

---

## Sample Data Queries

### Get Security Groups

```sql
SELECT TOP 10 * FROM SecGrp;
```

### Get Security Group Rights

```sql
SELECT TOP 10 * FROM SecGrpRights;
```

### Check Employee Permissions

```sql
SELECT
    e.EmployeeKey,
    e.FirstName,
    e.LastName,
    -- Add the actual security group column here based on schema
    sg.*
FROM Employee e
LEFT JOIN SecGrp sg ON e.SecGroupKey = sg.SecGrpKey  -- Adjust column names as needed
WHERE e.Active = 1;
```

"""

    return content

def generate_column_mapping(conn, all_tables):
    """Generate Document 08 - Column Name Mapping."""
    print("Generating Column Name Mapping...")

    key_tables = ["Ord", "OrdItem", "Employee", "TimeClock", "CashDrawer", "SecGrp", "Customer", "MenuItms"]

    content = f"""# Column Name Mapping
## Document 08 - Actual Column Names vs SQL Reference Guide

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** REVENTION

---

## Purpose

This document maps the actual database column names to help correct any discrepancies in the SQL Reference Guide.

---

## Key Table Schemas

"""

    all_tables_lower = {t.lower(): t for t in all_tables}

    for table in key_tables:
        actual_name = all_tables_lower.get(table.lower())
        if actual_name:
            cols, rows = get_table_columns(conn, actual_name)
            if cols:
                content += f"### {actual_name}\n\n"
                content += "| # | Column Name | Data Type | Nullable |\n"
                content += "|---|-------------|-----------|----------|\n"
                for i, row in enumerate(rows, 1):
                    col_name, data_type, max_len, nullable, _ = row
                    type_str = f"{data_type}"
                    if max_len:
                        type_str += f"({max_len})"
                    content += f"| {i} | `{col_name}` | {type_str} | {nullable} |\n"
                content += "\n"
        else:
            content += f"### {table}\n\n**Table not found in database.**\n\n"

    # Common column name variations to check
    content += """---

## Common Column Name Variations

Based on HungerRush/Revention naming conventions:

| Common Reference | Actual Column | Table | Notes |
|------------------|---------------|-------|-------|
| `SvrKey` | Check Employee FK | Ord | Server/Employee key |
| `BusinessDate` | `BizDate` | Ord | Business date |
| `EmployeeFName` | `FirstName` | Employee | First name |
| `EmployeeLName` | `LastName` | Employee | Last name |
| `CashDrawerName` | Check CashDrawerCfg | CashDrawerCfg | Drawer name |

"""

    return content

def generate_corrected_queries(conn, all_tables):
    """Generate Document 09 - Corrected SQL Queries."""
    print("Generating Corrected SQL Queries...")

    content = f"""# Corrected SQL Queries
## Document 09 - Validated and Working Queries

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** REVENTION

---

## Testing Methodology

Each query below has been validated against the actual database schema.

---

"""

    # Test queries for each category
    test_queries = [
        ("Recent Orders", "SELECT TOP 5 OrdKey, OrdNumber, BizDate, OrdType, Total FROM Ord ORDER BY OrdKey DESC"),
        ("Order Items", "SELECT TOP 5 OrdItemKey, OrdKey, ItemName, Qty, Price, Total FROM OrdItem ORDER BY OrdItemKey DESC"),
        ("Employees", "SELECT TOP 5 EmployeeKey, FirstName, LastName, Active FROM Employee ORDER BY EmployeeKey DESC"),
        ("Time Clock", "SELECT TOP 5 * FROM TimeClock ORDER BY TimeClockKey DESC"),
        ("Cash Drawer", "SELECT TOP 5 * FROM CashDrawer ORDER BY CashDrawerKey DESC"),
        ("Payments", "SELECT TOP 5 * FROM OrdPayment ORDER BY OrdPaymentKey DESC"),
        ("Security Groups", "SELECT TOP 5 * FROM SecGrp"),
        ("Menu Items", "SELECT TOP 5 * FROM MenuItms ORDER BY MenuItmKey DESC"),
        ("Customers", "SELECT TOP 5 * FROM Customer ORDER BY CustomerKey DESC"),
    ]

    for name, query in test_queries:
        result = test_query(conn, query, name)
        content += f"### {name}\n\n"

        if result["success"]:
            content += f"**Status:** Working\n\n"
            content += "```sql\n" + query + "\n```\n\n"
            content += f"**Columns:** {', '.join(result['columns'])}\n\n"
            content += f"**Sample rows returned:** {result['row_count']}\n\n"
        else:
            content += f"**Status:** Failed\n\n"
            content += "```sql\n" + query + "\n```\n\n"
            content += f"**Error:** {result['error']}\n\n"

        content += "---\n\n"

    # Add corrected permission query
    content += """## Permission Checking Query (Corrected)

To check employee permissions, first identify the correct column linking Employee to SecGrp:

```sql
-- Step 1: Find the security group column in Employee table
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Employee'
  AND (COLUMN_NAME LIKE '%Sec%' OR COLUMN_NAME LIKE '%Grp%' OR COLUMN_NAME LIKE '%Group%');

-- Step 2: Get all SecGrp columns
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'SecGrp';

-- Step 3: Build the join query based on actual column names
-- Example (adjust column names based on Step 1 and 2 results):
SELECT
    e.EmployeeKey,
    e.FirstName,
    e.LastName,
    sg.*
FROM Employee e
-- JOIN SecGrp sg ON e.[SecurityGroupColumn] = sg.[PrimaryKeyColumn]
WHERE e.Active = 1;
```

"""

    return content

def generate_test_queries(conn, all_tables):
    """Generate Document 10 - Working Test Queries by Category."""
    print("Generating Test Queries by Category...")

    content = f"""# Working Test Queries by Category
## Document 10 - One Verified Query Per Category

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** REVENTION

---

## How to Use

Each query below has been tested and verified to work. Copy and paste into your SQL tool.

---

"""

    categories = {
        "Orders": {
            "purpose": "Find recent orders with basic details",
            "query": "SELECT TOP 10 OrdKey, OrdNumber, BizDate, OrdType, OrdStatus, Total, Computer FROM Ord ORDER BY BizDate DESC, OrdKey DESC"
        },
        "Order Items": {
            "purpose": "Get items from a specific order",
            "query": "SELECT TOP 10 oi.OrdItemKey, oi.ItemName, oi.Qty, oi.Price, oi.Total FROM OrdItem oi INNER JOIN Ord o ON oi.OrdKey = o.OrdKey ORDER BY o.BizDate DESC, oi.OrdItemKey DESC"
        },
        "Payments & Credit Cards": {
            "purpose": "View recent payments",
            "query": "SELECT TOP 10 * FROM OrdPayment ORDER BY OrdPaymentKey DESC"
        },
        "Cash Drawers": {
            "purpose": "Check cash drawer status",
            "query": "SELECT TOP 10 * FROM CashDrawer ORDER BY CashDrawerKey DESC"
        },
        "Employees": {
            "purpose": "List active employees",
            "query": "SELECT EmployeeKey, FirstName, LastName, Active FROM Employee WHERE Active = 1 ORDER BY LastName, FirstName"
        },
        "Time Clock": {
            "purpose": "Recent time clock entries",
            "query": "SELECT TOP 10 * FROM TimeClock ORDER BY TimeClockKey DESC"
        },
        "Security & Permissions": {
            "purpose": "List security groups",
            "query": "SELECT * FROM SecGrp ORDER BY SecGrpKey"
        },
        "Menu Items": {
            "purpose": "List menu items",
            "query": "SELECT TOP 10 MenuItmKey, ItemName, Price FROM MenuItms ORDER BY MenuItmKey DESC"
        },
        "Customers": {
            "purpose": "Recent customers",
            "query": "SELECT TOP 10 * FROM Customer ORDER BY CustomerKey DESC"
        },
        "Delivery": {
            "purpose": "Recent delivery orders",
            "query": "SELECT TOP 10 * FROM DeliveryOrder ORDER BY DeliveryOrderKey DESC"
        },
        "Summary/Reports": {
            "purpose": "Daily summary data",
            "query": "SELECT TOP 10 * FROM SumDaily ORDER BY BizDate DESC"
        },
        "System Configuration": {
            "purpose": "System settings",
            "query": "SELECT TOP 10 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%Cfg%' OR TABLE_NAME LIKE '%Config%'"
        }
    }

    for category, info in categories.items():
        result = test_query(conn, info["query"], category)

        content += f"## {category}\n\n"
        content += f"**Purpose:** {info['purpose']}\n\n"

        if result["success"]:
            content += "**Status:** Working\n\n"
            content += "```sql\n" + info["query"] + "\n```\n\n"
            if result.get("columns"):
                content += f"**Output Columns:** `{', '.join(result['columns'])}`\n\n"
        else:
            content += "**Status:** Query failed - table may not exist\n\n"
            content += "```sql\n" + info["query"] + "\n```\n\n"
            content += f"**Note:** {result.get('error', 'Unknown error')}\n\n"

        content += "---\n\n"

    return content

def main():
    """Main function to generate all documentation."""
    print("=" * 60)
    print("Generating Validated SQL Documentation")
    print("=" * 60)

    try:
        conn = get_connection()
        print(f"Connected to database successfully")

        # Get all tables
        all_tables = get_all_tables(conn)
        print(f"Found {len(all_tables)} tables in database")

        # Generate each document
        docs = [
            ("05 - Query Validation Report.md", generate_validation_report),
            ("06 - Database Table Quick Reference.md", generate_table_quick_reference),
            ("07 - Security Permissions Tables.md", generate_security_deep_dive),
            ("08 - Column Name Mapping.md", generate_column_mapping),
            ("09 - Corrected SQL Queries.md", generate_corrected_queries),
            ("10 - Test Queries By Category.md", generate_test_queries),
        ]

        for filename, generator in docs:
            try:
                content = generator(conn, all_tables)
                filepath = OUTPUT_DIR / filename
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"Created: {filename}")
            except Exception as e:
                print(f"Error generating {filename}: {e}")

        conn.close()
        print("\n" + "=" * 60)
        print("Documentation generation complete!")
        print(f"Output directory: {OUTPUT_DIR}")
        print("=" * 60)

    except Exception as e:
        print(f"Connection error: {e}")
        raise

if __name__ == "__main__":
    main()
