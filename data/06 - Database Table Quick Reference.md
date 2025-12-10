# Database Table Quick Reference
## Document 06 - Table Organization by Category

**Generated:** 2025-12-10 15:10:23
**Database:** REVENTION
**Total Tables:** 324

---

## Key Tables with Row Counts

### Orders & Transactions

| Table | Rows | Status |
|-------|------|--------|
| `Ord` | 355,648 | Found |
| `OrdItem` | 954,111 | Found |
| `OrdItemMod` | 796,558 | Found |
| `OrdCpn` | 63,205 | Found |
| `OrdTax` | 345,568 | Found |
| `OrdPayment` | 322,830 | Found |
| `OrdDefer` | 25,859 | Found |
| `OrdNote` | 23,827 | Found |
| `OrdLock` | 3 | Found |
| `OrdAdj` | 7,055 | Found |
| `OrdCust` | 355,646 | Found |
| `OrdData` | 1 | Found |

### Payments & Credit Cards

| Table | Rows | Status |
|-------|------|--------|
| `OrdPayment` | 322,830 | Found |
| `CCTrans` | 164,114 | Found |
| `CCBatches` | 2,576 | Found |
| `PaymentType` | 6 | Found |
| `CCTransLog` | 307,573 | Found |

### Cash Drawers

| Table | Rows | Status |
|-------|------|--------|
| `CashDrawer` | 12,622 | Found |
| `CashDrawerCfg` | 2 | Found |
| `CashDrawerAudit` | 238 | Found |
| `CashDrawerDrop` | 0 | Found |
| `CashDrawerUser` | 22,282 | Found |

### Employees & Time Clock

| Table | Rows | Status |
|-------|------|--------|
| `Employee` | 87 | Found |
| `TimeClock` | 25,487 | Found |
| `EmployeeSched` | 12,606 | Found |
| `TimeClockAudit` | 29,316 | Found |
| `LaborType` | 7 | Found |
| `Breaks` | 0 | Found |
| `EmployeeJob` | - | **Not Found** |

### Security & Permissions

| Table | Rows | Status |
|-------|------|--------|
| `SecGrp` | 7 | Found |
| `SecGrpRights` | 1,428 | Found |
| `SecRightsDefault` | 244 | Found |
| `SecIndGrp` | 54 | Found |
| `SecIndRights` | 1,389 | Found |
| `SecChgAudit` | 3,207 | Found |

### Menu System

| Table | Rows | Status |
|-------|------|--------|
| `Menus` | 1 | Found |
| `MenuGrps` | 10 | Found |
| `MenuItms` | 97 | Found |
| `MenuMds` | 84 | Found |
| `MenuCategory` | 13 | Found |
| `MenuItmOrdTypes` | - | **Not Found** |

### Printing & Kitchen Display

| Table | Rows | Status |
|-------|------|--------|
| `Printer` | 3 | Found |
| `PrintJobs` | 0 | Found |
| `PrinterGroup` | 0 | Found |
| `KDOrd` | 55 | Found |
| `KDOrdItem` | 135 | Found |
| `KtchDisp` | 0 | Found |

### Delivery

| Table | Rows | Status |
|-------|------|--------|
| `DeliveryOrder` | 87,571 | Found |
| `DeliveryDriver` | 5,815 | Found |
| `DeliveryOpts` | 1 | Found |
| `DeliveryQueue` | 1,543 | Found |

### Customers

| Table | Rows | Status |
|-------|------|--------|
| `Customer` | 34,020 | Found |
| `CustomerPhone` | 35,649 | Found |
| `CustomerAddr` | 11,229 | Found |
| `CustomerNote` | - | **Not Found** |
| `CustAcct` | 17 | Found |

### Reports & Summaries

| Table | Rows | Status |
|-------|------|--------|
| `SumPayment` | 3,990 | Found |
| `SumAccounting` | 0 | Found |
| `SumAdj` | 16,785 | Found |
| `SumCreditCards` | 10,410 | Found |
| `SumInventory` | 0 | Found |

### Synchronization

| Table | Rows | Status |
|-------|------|--------|
| `SyncRecords` | 247,659 | Found |

### System & Configuration

| Table | Rows | Status |
|-------|------|--------|
| `SysConfig` | 1 | Found |
| `Computer` | 2 | Found |
| `Business` | 1 | Found |
| `BusinessDate` | 3,999 | Found |
| `BusinessHours` | 7 | Found |

---

## Top 20 Tables by Row Count

| Rank | Table | Rows |
|------|-------|------|
| 1 | `SumProduct` | 1,469,864 |
| 2 | `OrdItem` | 954,111 |
| 3 | `OrdItemMod` | 796,558 |
| 4 | `Ord` | 355,648 |
| 5 | `OrdCust` | 355,646 |
| 6 | `OrdTax` | 345,568 |
| 7 | `OrdPayment` | 322,830 |
| 8 | `CCTransLog` | 307,573 |
| 9 | `SyncRecords` | 247,659 |
| 10 | `OrdItemNoMod` | 215,545 |
| 11 | `CCTrans` | 164,114 |
| 12 | `SumSalesByTime` | 146,345 |
| 13 | `AuditLog` | 119,200 |
| 14 | `DeliveryOrder` | 87,571 |
| 15 | `OrdCpnItm` | 85,222 |
| 16 | `SumAdjDetail` | 68,766 |
| 17 | `OrdCpn` | 63,205 |
| 18 | `CustomerPhone` | 35,649 |
| 19 | `Customer` | 34,020 |
| 20 | `SumSalesByOrdType` | 32,219 |
