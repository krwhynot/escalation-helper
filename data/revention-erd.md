# Revention Database - Entity Relationship Diagram

## Overview
- **Database:** REVENTION
- **Server:** 172.31.240.1\Revention
- **Generated:** 2025-12-08
- **Tables:** 324
- **Views:** 0
- **Stored Procedures:** 0 (application-layer logic)
- **Triggers:** 0 (application-layer logic)
- **Foreign Key Relationships:** 59
- **Total Columns:** 5,131
- **Identity Columns:** 309

## Database Summary

The Revention database is a comprehensive **Point-of-Sale (POS) system** designed for restaurant and food service operations. It features a highly normalized menu system, robust order management, and extensive operational tracking capabilities.

### Key Characteristics
- **Compatibility Level:** SQL Server 2008 (Level 100)
- **Recovery Model:** SIMPLE
- **Collation:** SQL_Latin1_General_CP1_CI_AS
- **Schema:** All tables in `dbo` schema

---

## Domain Areas

### 1. Order Management (Core Transactional)
| Table | Rows | Size | Description |
|-------|------|------|-------------|
| Ord | 355,648 | 149 MB | Main orders table |
| OrdItem | 954,111 | 679 MB | Order line items |
| OrdItemMod | 796,558 | 216 MB | Item modifications |
| OrdCust | 355,646 | 66 MB | Order customer info |
| OrdPayment | 322,830 | 74 MB | Payment transactions |
| OrdTax | 345,568 | 34 MB | Tax calculations |
| OrdCpn | 63,205 | 22 MB | Applied coupons |
| OrdNote | 23,827 | 2 MB | Order notes |

### 2. Menu System (Highly Normalized)
| Table | Columns | Description |
|-------|---------|-------------|
| Menus | 43 | Menu definitions |
| MenuGrps | 8 | Menu groups |
| MenuItms | 10 | Menu items |
| MenuMds | 10 | Modifiers |
| MenuSzs | 9 | Sizes |
| MenuStys | 9 | Styles |
| MenuPrfs | 8 | Preferences |
| MenuPrfMbrs | 9 | Preference members |
| MenuCpns | 66 | Coupons |
| MenuGrpXRef | 62 | Group cross-references |
| MenuGrpItmXRef | 59 | Group-item mappings |
| MenuGrpMdXRef | 32 | Group-modifier mappings |

### 3. Customer Management
| Table | Rows | Description |
|-------|------|-------------|
| Customer | 34,020 | Customer records |
| CustomerPhone | 35,649 | Phone numbers |
| CustomerAddr | 11,229 | Addresses |
| CustomerLoc | 2,146 | Locations |
| CustMkt | - | Marketing data |
| CustAcct | 17 | Customer accounts |

### 4. Employee & Labor Management
| Table | Rows | Description |
|-------|------|-------------|
| Employee | 87 | Employee records |
| TimeClock | 25,487 | Time clock entries |
| TimeClockAudit | 29,316 | Audit trail |
| EmployeeSched | 12,606 | Schedules |
| EmployeeLaborType | 103 | Labor types |
| LaborType | - | Labor type definitions |

### 5. Cash & Payment Processing
| Table | Rows | Description |
|-------|------|-------------|
| CashDrawer | 12,622 | Drawer sessions |
| CashDrawerUser | 22,282 | User assignments |
| CCTransLog | 307,573 | CC transaction logs |
| CCTrans | 164,114 | CC transactions |
| CCBatches | 2,576 | Settlement batches |
| PaymentType | - | Payment definitions |

### 6. Inventory Management
| Table | Description |
|-------|-------------|
| InventItem | Inventory items |
| InventPO | Purchase orders |
| InventPOItems | PO line items |
| InventRecipe | Recipe definitions |
| InventVendor | Vendors |
| InventCat | Categories |

### 7. Reporting & Analytics
| Table | Rows | Description |
|-------|------|-------------|
| SumProduct | 1,469,864 | Product summaries |
| SumSalesByTime | 146,345 | Time-based sales |
| SumSalesByOrdType | 32,219 | Sales by order type |
| SumSales | 3,990 | Daily sales |
| SumPayment | 3,990 | Payment summaries |
| SumAdj | 16,785 | Adjustments |

### 8. Kitchen Display System
| Table | Description |
|-------|-------------|
| KtchDisp | Kitchen display config |
| KDOrd | Kitchen orders |
| KDOrdItem | Kitchen order items |
| KDOrdItemMod | Kitchen item mods |

### 9. Delivery Management
| Table | Rows | Description |
|-------|------|-------------|
| DeliveryOrder | 87,571 | Delivery orders |
| DeliveryDriver | 5,815 | Driver records |
| DeliveryQueue | 1,543 | Dispatch queue |
| Zones | - | Delivery zones |

### 10. Remote Update System (RU_*)
| Table | Description |
|-------|-------------|
| RU_Jobs | Scheduled jobs |
| RU_Files | Update files |
| RU_Schedules | Update schedules |
| RU_JobHistory | Execution history |

---

## Foreign Key Relationships

### Relationship Summary
- **Total FKs:** 59
- **CASCADE DELETE:** 37 (62.7%)
- **NO_ACTION:** 22 (37.3%)
- **CASCADE UPDATE:** 37 (62.7%)

### Key Relationship Groups

#### Employee Domain
```
Employee (EmployeeKey)
    ├── EmployeeLaborRate (CASCADE DELETE/UPDATE)
    └── EmployeeLaborType (CASCADE DELETE/UPDATE)
```

#### Menu Domain
```
Menus (MenuName)
    ├── MenuGrpXRef (CASCADE)
    ├── MenuGrpMdXRef (CASCADE)
    ├── MenuGrpMdSzXRef (CASCADE)
    ├── MenuGrpPrfXRef (CASCADE)
    ├── MenuGrpStySzXRef (CASCADE)
    ├── MenuItmMdXRef (CASCADE)
    ├── MenuItmMdSzXRef (CASCADE)
    ├── MenuItmPrfXRef (CASCADE)
    └── MenuItmStySzXRef (CASCADE)

MenuGrps (GroupName)
    ├── MenuGrpXRef (CASCADE)
    ├── MenuGrpMdXRef (CASCADE)
    ├── MenuItmMdXRef (CASCADE)
    └── ... (multiple cross-references)

MenuItms (ItemName)
    ├── MenuItmMdSzXRef (CASCADE)
    ├── MenuItmMdXRef (CASCADE)
    ├── MenuItmPrfXRef (CASCADE)
    └── MenuItmStySzXRef (CASCADE)
```

#### Security Domain
```
SecGrp (SecGroupKey)
    └── SecGrpRights (CASCADE DELETE)
```

#### Remote Update Domain
```
RU_Jobs (JobID)
    ├── RU_FileJobs (CASCADE)
    ├── RU_JobHistory (NO_ACTION)
    ├── RU_JobParameters (CASCADE DELETE)
    └── RU_JobSchedules (CASCADE DELETE)

RU_Files (FileID)
    ├── RU_FileAccessLog (CASCADE)
    └── RU_FileJobs (CASCADE)

RU_Schedules (ScheduleID)
    ├── RU_JobSchedules (CASCADE DELETE)
    └── RU_JobHistory (NO_ACTION)
```

#### Other Relationships
```
Computer (ComputerKey)
    └── APIUsers (NO_ACTION)

Surcharges (SCKey)
    ├── SurchargeOrderType (NO_ACTION)
    └── SurchargePaymentType (NO_ACTION)

Zones (ZoneKey)
    └── ZoneGeocodes (CASCADE)

EventQuestions (EventQuestionsKey)
    ├── EventQuestionValues (CASCADE)
    ├── TimeclockEventQuestions (CASCADE)
    └── TimeclockEventResponse (NO_ACTION)
```

---

## Tables Without Foreign Keys (Orphan Tables)

The majority of tables (265 out of 324) do not have explicit foreign key constraints. This indicates that referential integrity is primarily enforced at the application layer. Key orphan tables include:

- All `Sum*` tables (reporting/summary)
- All `Ord*` tables except cross-references
- Customer tables
- Cash/Payment tables
- Most configuration tables

---

## Largest Tables by Row Count

| Rank | Table | Rows | Size (MB) |
|------|-------|------|-----------|
| 1 | SumProduct | 1,469,864 | 421 |
| 2 | OrdItem | 954,111 | 679 |
| 3 | OrdItemMod | 796,558 | 216 |
| 4 | Ord | 355,648 | 149 |
| 5 | OrdCust | 355,646 | 66 |
| 6 | OrdTax | 345,568 | 34 |
| 7 | OrdPayment | 322,830 | 74 |
| 8 | CCTransLog | 307,573 | 122 |
| 9 | SyncRecords | 247,659 | 26 |
| 10 | OrdItemNoMod | 215,545 | 57 |

---

## Index Summary

- **Total Indexes:** 467
- **Clustered:** 256 (54.8%)
- **Non-Clustered:** 211 (45.2%)
- **Primary Key Indexes:** 321
- **Unique Indexes:** 1 (non-PK)

### Missing Index Recommendations

| Priority | Table | Columns | Impact |
|----------|-------|---------|--------|
| HIGH | SyncRecords | EntKey, SyncStatus, Operation, TableKey | 99.88% |
| HIGH | OrdDefer | Activated, PrintTime (INCLUDE OrdNumber) | 79.17% |
| MEDIUM | BackupLog | BUTypeCode, Status (INCLUDE BUTime, BUType, Path, BUBy) | 9.83% |

---

## Data Integrity Notes

1. **Limited FK Constraints:** Only 59 FKs for 324 tables indicates application-layer integrity
2. **No CHECK Constraints:** Data validation handled by application
3. **No UNIQUE Constraints:** (except PKs) Business rules in application
4. **No Views:** Reporting done via direct table queries or external tools
5. **No Triggers:** All business logic in application layer
6. **No Stored Procedures:** All data access via application

---

## Mermaid ERD

See `revention-erd.mermaid` for the visual entity relationship diagram.
