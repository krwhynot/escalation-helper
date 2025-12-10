# Revention Data Dictionary

## Overview

Comprehensive column-level documentation for the REVENTION database.

- **Database:** REVENTION
- **Total Tables:** 324
- **Total Columns:** 5,131
- **Schema:** dbo (all tables)
- **Generated:** 2025-12-08

---

## Data Type Distribution

| Data Type | Count | Usage |
|-----------|-------|-------|
| int | ~1,800 | Primary keys, foreign keys, counters |
| nvarchar | ~1,500 | Text fields, names, descriptions |
| bit | ~800 | Boolean flags |
| datetime | ~400 | Timestamps, dates |
| decimal | ~300 | Prices, amounts, quantities |
| money | ~100 | Currency values |
| smallint | ~100 | Small integers |
| image/varbinary | ~30 | Binary data, files |
| text/ntext | ~20 | Large text fields |

---

## Common Column Patterns

### Primary Key Convention
Most tables use `[TableName]Key` as the primary key:
- `OrdKey`, `CustomerKey`, `EmployeeKey`, `MenuKey`, etc.
- All PKs are `int` with IDENTITY(1,1)

### Sync/Enterprise Columns
Many tables include enterprise synchronization fields:
- `EntID` (int) - Enterprise identifier
- `EntSync` (datetime) - Last sync timestamp
- `SyncStatus` (int) - Sync state (0=synced, 1=pending, etc.)

### Audit Columns
Common audit/tracking fields:
- `CreateDate` / `Created` (datetime)
- `ModifyDate` / `Modified` (datetime)
- `CreatedBy` / `ModifiedBy` (int or nvarchar)

### Status Flags
- `Active` (bit) - Record active status
- `Deleted` (bit) - Soft delete flag
- `Enabled` (bit) - Feature enabled

---

## Table Documentation by Domain

### Order Management Tables

#### dbo.Ord
**Purpose:** Main orders table - central transactional entity
**Row Count:** 355,648
**Primary Key:** OrdKey (identity)

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| OrdKey | int | NO | IDENTITY | Unique order identifier |
| OrdNumber | int | NO | | Order number (business key) |
| BizDate | datetime | NO | | Business date |
| OrdDate | datetime | NO | | Order creation timestamp |
| OrdTime | datetime | YES | | Order time |
| OrdType | nvarchar(20) | NO | | Order type code |
| OrdStatus | int | NO | 0 | Order status |
| TableNum | nvarchar(10) | YES | | Table number |
| SeatNum | int | YES | | Seat number |
| CheckNum | int | YES | | Check number |
| SubTotal | money | NO | 0 | Subtotal amount |
| Tax | money | NO | 0 | Tax amount |
| Total | money | NO | 0 | Total amount |
| Tip | money | YES | 0 | Tip amount |
| Discount | money | YES | 0 | Discount amount |
| Balance | money | YES | 0 | Remaining balance |
| PaidAmount | money | YES | 0 | Amount paid |
| CustomerKey | int | YES | | FK to Customer |
| EmployeeKey | int | YES | | Server/cashier |
| ComputerKey | int | YES | | Terminal used |
| ... | | | | (82 total columns) |

#### dbo.OrdItem
**Purpose:** Order line items
**Row Count:** 954,111
**Primary Key:** OrdItemKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| OrdItemKey | int | NO | IDENTITY | Unique item identifier |
| OrdKey | int | NO | | FK to Ord |
| ItemName | nvarchar(50) | NO | | Menu item name |
| GroupName | nvarchar(50) | YES | | Menu group |
| SizeName | nvarchar(20) | YES | | Size ordered |
| StyleName | nvarchar(20) | YES | | Style ordered |
| Qty | decimal(10,3) | NO | 1 | Quantity |
| Price | money | NO | 0 | Unit price |
| ExtPrice | money | NO | 0 | Extended price |
| Tax | money | YES | 0 | Item tax |
| Discount | money | YES | 0 | Item discount |
| Voided | bit | NO | 0 | Item voided |
| SentToKitchen | bit | NO | 0 | Sent to kitchen |
| ... | | | | (102 total columns) |

#### dbo.OrdItemMod
**Purpose:** Item modifications/toppings
**Row Count:** 796,558
**Primary Key:** OrdItemModKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| OrdItemModKey | int | NO | IDENTITY | Unique modifier identifier |
| OrdItemKey | int | NO | | FK to OrdItem |
| ModName | nvarchar(50) | NO | | Modifier name |
| ModType | nvarchar(10) | YES | | Type (ADD, NO, EXTRA, etc.) |
| Qty | decimal(10,3) | YES | 1 | Quantity |
| Price | money | YES | 0 | Modifier price |
| ... | | | | (40 total columns) |

#### dbo.OrdPayment
**Purpose:** Payment transactions for orders
**Row Count:** 322,830
**Primary Key:** OrdPaymentKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| OrdPaymentKey | int | NO | IDENTITY | Unique payment identifier |
| OrdKey | int | NO | | FK to Ord |
| PaymentType | nvarchar(20) | NO | | Payment method |
| Amount | money | NO | 0 | Payment amount |
| Tip | money | YES | 0 | Tip on payment |
| Change | money | YES | 0 | Change given |
| CCTransKey | int | YES | | FK to CCTrans |
| AuthCode | nvarchar(20) | YES | | Authorization code |
| ... | | | | (43 total columns) |

---

### Customer Tables

#### dbo.Customer
**Purpose:** Customer master records
**Row Count:** 34,020
**Primary Key:** CustomerKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| CustomerKey | int | NO | IDENTITY | Unique customer ID |
| FirstName | nvarchar(50) | YES | | First name |
| LastName | nvarchar(50) | YES | | Last name |
| Company | nvarchar(100) | YES | | Company name |
| Email | nvarchar(100) | YES | | Email address |
| Notes | nvarchar(500) | YES | | Customer notes |
| TaxExempt | bit | NO | 0 | Tax exempt status |
| DoNotCall | bit | NO | 0 | Marketing opt-out |
| ... | | | | (39 total columns) |

#### dbo.CustomerPhone
**Purpose:** Customer phone numbers (multi-valued)
**Row Count:** 35,649
**Primary Key:** CustomerPhoneKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| CustomerPhoneKey | int | NO | IDENTITY | Unique phone ID |
| CustomerKey | int | NO | | FK to Customer |
| Phone | nvarchar(20) | NO | | Phone number |
| PhoneType | nvarchar(10) | YES | | Type (Home, Work, Cell) |
| IsPrimary | bit | NO | 0 | Primary phone flag |
| ... | | | | (9 total columns) |

#### dbo.CustomerAddr
**Purpose:** Customer addresses (multi-valued)
**Row Count:** 11,229
**Primary Key:** AddrKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| AddrKey | int | NO | IDENTITY | Unique address ID |
| CustomerKey | int | NO | | FK to Customer |
| Street1 | nvarchar(100) | YES | | Address line 1 |
| Street2 | nvarchar(100) | YES | | Address line 2 |
| City | nvarchar(50) | YES | | City |
| State | nvarchar(20) | YES | | State/Province |
| Zip | nvarchar(20) | YES | | Postal code |
| Country | nvarchar(50) | YES | | Country |
| ... | | | | (18 total columns) |

---

### Menu System Tables

#### dbo.Menus
**Purpose:** Menu definitions
**Primary Key:** MenuName (natural key)

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| MenuName | nvarchar(50) | NO | | Menu identifier |
| Description | nvarchar(100) | YES | | Menu description |
| Active | bit | NO | 1 | Active status |
| DisplaySeq | int | YES | 0 | Display order |
| ... | | | | (43 total columns) |

#### dbo.MenuGrps
**Purpose:** Menu groups/categories
**Primary Key:** GroupName

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| GroupName | nvarchar(50) | NO | | Group identifier |
| Description | nvarchar(100) | YES | | Group description |
| DisplaySeq | int | YES | 0 | Display order |
| ... | | | | (8 total columns) |

#### dbo.MenuItms
**Purpose:** Menu items
**Row Count:** 97
**Primary Key:** ItemName

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| ItemName | nvarchar(50) | NO | | Item identifier |
| Description | nvarchar(100) | YES | | Item description |
| DisplaySeq | int | YES | 0 | Display order |
| ... | | | | (10 total columns) |

#### dbo.MenuMds (Modifiers)
**Purpose:** Menu modifiers/toppings
**Row Count:** 84

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| ModName | nvarchar(50) | NO | | Modifier identifier |
| Description | nvarchar(100) | YES | | Description |
| ModCatKey | int | YES | | Category key |
| ... | | | | (10 total columns) |

---

### Employee Tables

#### dbo.Employee
**Purpose:** Employee master records
**Row Count:** 87
**Primary Key:** EmployeeKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| EmployeeKey | int | NO | IDENTITY | Unique employee ID |
| EmpNumber | nvarchar(20) | YES | | Employee number |
| FirstName | nvarchar(50) | NO | '' | First name |
| LastName | nvarchar(50) | NO | '' | Last name |
| PIN | nvarchar(20) | YES | | Login PIN |
| Password | nvarchar(50) | YES | | Password hash |
| SecGroupKey | int | YES | | Security group |
| HireDate | datetime | YES | | Hire date |
| TermDate | datetime | YES | | Termination date |
| Active | bit | NO | 1 | Active status |
| ... | | | | (52 total columns) |

#### dbo.TimeClock
**Purpose:** Time clock entries
**Row Count:** 25,487
**Primary Key:** TimeClockKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| TimeClockKey | int | NO | IDENTITY | Entry identifier |
| EmployeeKey | int | NO | | FK to Employee |
| LaborTypeKey | int | YES | | Labor type |
| BizDate | datetime | NO | | Business date |
| ClockIn | datetime | NO | | Clock in time |
| ClockOut | datetime | YES | | Clock out time |
| Hours | decimal(10,2) | YES | | Hours worked |
| Tips | money | YES | 0 | Tips received |
| ... | | | | (26 total columns) |

---

### Cash/Payment Tables

#### dbo.CashDrawer
**Purpose:** Cash drawer sessions
**Row Count:** 12,622
**Primary Key:** CashDrawerKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| CashDrawerKey | int | NO | IDENTITY | Drawer session ID |
| CashDrawerCfgKey | int | NO | | Drawer config |
| ComputerKey | int | YES | | Terminal |
| BizDate | datetime | NO | | Business date |
| OpenTime | datetime | YES | | Open time |
| CloseTime | datetime | YES | | Close time |
| OpeningBalance | money | YES | 0 | Starting cash |
| ClosingBalance | money | YES | 0 | Ending cash |
| ... | | | | (54 total columns) |

#### dbo.CCTransLog
**Purpose:** Credit card transaction log
**Row Count:** 307,573
**Primary Key:** CCTransLogKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| CCTransLogKey | int | NO | IDENTITY | Log entry ID |
| CCTransKey | int | YES | | FK to CCTrans |
| TransType | nvarchar(20) | YES | | Transaction type |
| Amount | money | YES | 0 | Amount |
| AuthCode | nvarchar(20) | YES | | Auth code |
| ResponseCode | nvarchar(10) | YES | | Response code |
| ... | | | | (42 total columns) |

---

### Summary/Reporting Tables

#### dbo.SumProduct
**Purpose:** Product-level sales summary
**Row Count:** 1,469,864
**Primary Key:** SumProductKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| SumProductKey | int | NO | IDENTITY | Summary ID |
| BizDate | datetime | NO | | Business date |
| ItemName | nvarchar(50) | YES | | Item name |
| GroupName | nvarchar(50) | YES | | Group name |
| Qty | decimal(18,3) | YES | 0 | Quantity sold |
| Sales | money | YES | 0 | Sales amount |
| Cost | money | YES | 0 | Cost amount |
| ... | | | | (28 total columns) |

#### dbo.SumSales
**Purpose:** Daily sales summary
**Row Count:** 3,990
**Primary Key:** SumSalesKey

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| SumSalesKey | int | NO | IDENTITY | Summary ID |
| BizDate | datetime | NO | | Business date |
| GrossSales | money | YES | 0 | Gross sales |
| NetSales | money | YES | 0 | Net sales |
| Tax | money | YES | 0 | Tax collected |
| Discounts | money | YES | 0 | Total discounts |
| Voids | money | YES | 0 | Voided amount |
| ... | | | | (31 total columns) |

---

### Synchronization Table

#### dbo.SyncRecords
**Purpose:** Enterprise synchronization tracking
**Row Count:** 247,659

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| SyncRecordsKey | int | NO | IDENTITY | Sync record ID |
| TableKey | int | NO | | Record key |
| TableName | nvarchar(50) | NO | | Table name |
| EntKey | int | YES | | Enterprise key |
| Operation | nvarchar(10) | YES | | Operation (I/U/D) |
| SyncStatus | int | NO | 0 | Sync status |
| SyncTime | datetime | YES | | Sync timestamp |
| ... | | | | (8 total columns) |

**Note:** This table has a missing index recommendation for columns `[EntKey], [SyncStatus], [Operation], [TableKey]` with 99.88% potential impact.

---

## Configuration Tables

Large configuration tables with many columns:

| Table | Columns | Purpose |
|-------|---------|---------|
| SysConfig | 175 | System-wide configuration |
| Computer | 93 | Terminal configuration |
| Ord | 82 | Order settings embedded |
| Business | 83 | Business configuration |
| ComputerCCOpts | 75 | Credit card options |
| DeliveryOpts | 64 | Delivery configuration |
| MenuCpns | 66 | Coupon configuration |
| MenuGrpXRef | 62 | Menu group cross-ref |

---

## Empty/Reference Tables

Tables with zero or minimal rows (configuration/lookup):

| Table | Rows | Purpose |
|-------|------|---------|
| RefreshSchedule | 2 | Refresh config |
| SysServicesXRef | 2 | Service mapping |
| TableMgmtRoom | 3 | Room config |
| TblMgmtEmplXRef | 4 | Table-employee mapping |
| TM_* tables | <10 | Table management |

---

## Naming Conventions

### Table Names
- PascalCase: `CustomerPhone`, `OrdItem`
- Abbreviations: `Ord` (Order), `Itm` (Item), `Md` (Modifier)
- XRef suffix: Cross-reference tables (`MenuGrpItmXRef`)
- Sum prefix: Summary tables (`SumSales`, `SumProduct`)
- RU_ prefix: Remote Update system (`RU_Jobs`)
- KD prefix: Kitchen Display (`KDOrd`, `KDOrdItem`)

### Column Names
- PascalCase: `CustomerKey`, `FirstName`
- Key suffix: Primary/foreign keys
- Date/Time suffix: Temporal columns
- Is/Has prefix: Boolean flags (less common)
- Ent prefix: Enterprise sync fields

---

## Data Quality Notes

1. **No CHECK constraints** - Data validation in application
2. **No UNIQUE constraints** (except PKs) - Business rules in app
3. **Nullable columns** - Many columns allow NULL
4. **Default values** - Common defaults: 0, '', GETDATE()
5. **No computed columns** - Calculations in application
6. **No foreign keys on major tables** - App-enforced integrity

---

## Files Reference

- Raw data: `2_columns.json` (5,131 columns)
- Table list: `1_tables.json` (324 tables)
- Primary keys: `3_primary_keys.json` (388 entries)
- Foreign keys: `4_foreign_keys.json` (59 relationships)
