# HungerRush SQL Troubleshooting Reference Guide

> Complete reference for investigating POS issues using SQL queries
>
> **Database:** REVENTION on 172.31.240.1\Revention
> **Total Questions:** 96 across 14 categories
> **Generated:** 2025-12-09

---

## Table of Contents

1. [[#Category 1 Orders|Orders]] (Questions 1-10)
2. [[#Category 2 Payments Credit Cards|Payments & Credit Cards]] (Questions 11-17)
3. [[#Category 3 Cash Drawers Closing|Cash Drawers & Closing]] (Questions 18-27)
4. [[#Category 4 Employees Time Clock|Employees & Time Clock]] (Questions 28-36)
5. [[#Category 5 Permissions Security|Permissions & Security]] (Questions 37-41)
6. [[#Category 6 Menu Items|Menu & Items]] (Questions 42-49)
7. [[#Category 7 Printing Issues|Printing Issues]] (Questions 50-58)
8. [[#Category 8 Kitchen Display KDS|Kitchen Display - KDS]] (Questions 59-62)
9. [[#Category 9 Delivery|Delivery]] (Questions 63-68)
10. [[#Category 10 Customers|Customers]] (Questions 69-74)
11. [[#Category 11 Pricing Fees|Pricing & Fees]] (Questions 75-81)
12. [[#Category 12 Reports Daily Close|Reports & Daily Close]] (Questions 82-87)
13. [[#Category 13 Synchronization Multi-Location|Synchronization]] (Questions 88-91)
14. [[#Category 14 System Configuration|System & Configuration]] (Questions 92-96)

---

## Database Connection Info

To run these queries, connect to:
- **Server:** 172.31.240.1\Revention
- **Database:** REVENTION
- **User:** Revention
- **Password:** Astr0s
- **Port:** 1433
- **Driver:** ODBC Driver 18 for SQL Server

**Python Connection:**
```python
import pyodbc
conn_str = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=172.31.240.1\\Revention;DATABASE=REVENTION;UID=Revention;PWD=Astr0s;TrustServerCertificate=yes;'
conn = pyodbc.connect(conn_str)
```

---

## Category 1: Orders

**Key Tables:** `Ord`, `OrdItem`, `OrdItemMod`, `OrdCpn`, `OrdTax`, `OrdPayment`, `OrdDefer`, `OrdNote`

---

### Problem 1: Customer says they placed an order but it's nowhere in the system

**What to Look For:** Search for the order by customer name, phone number, date range, or approximate time.

**SQL Query:**
```sql
SELECT
    o.OrdKey,
    o.OrdNumber,
    o.BizDate,
    o.OrdType,
    o.OrdStartTime,
    o.Total,
    o.OrdStatus,
    e.LastName + ', ' + e.FirstName AS ServerName,
    o.Computer
FROM Ord o
LEFT JOIN Employee e ON o.SvrKey = e.EmployeeKey
WHERE o.BizDate >= DATEADD(day, -7, CAST(GETDATE() AS DATE))
ORDER BY o.BizDate DESC, o.OrdStartTime DESC;
```

**How to Interpret Results:**
- If no results, order was never entered or was deleted
- Check `OrdStatus` - status codes vary but typically 0=open, higher values=closed/voided

---

### Problem 2: Order shows wrong total after applying coupon

**What to Look For:** Compare the coupon discount amount to what the system calculated.

**SQL Query:**
```sql
DECLARE @OrdNumber INT = 12345;
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    o.OrdNumber,
    o.OrdType,
    o.SubTotal,
    o.Discount,
    o.Tax,
    o.Total
FROM Ord o
WHERE o.OrdNumber = @OrdNumber AND o.BizDate = @BizDate;

-- Get all coupons on the order
SELECT
    c.CpnCode,
    c.CpnName,
    c.CpnType,
    c.DiscAmt,
    c.DiscPct,
    c.AppliedAmt
FROM OrdCpn c
JOIN Ord o ON c.OrdKey = o.OrdKey
WHERE o.OrdNumber = @OrdNumber AND o.BizDate = @BizDate;
```

**How to Interpret Results:**
- Compare `AppliedAmt` to `DiscAmt` or calculated percentage
- `AppliedAmt` shows what actually came off

---

### Problem 3: Items missing from receipt but customer swears they ordered them

**What to Look For:** Check if items were voided, removed, or never added.

**SQL Query:**
```sql
DECLARE @OrdNumber INT = 12345;
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    oi.OrdItemKey,
    oi.OrdItemNumber,
    oi.ItemName,
    oi.Qty,
    oi.Price,
    oi.Total,
    CASE WHEN oi.Total = 0 AND oi.Price > 0 THEN 'Possibly Voided' ELSE 'Active' END AS ItemStatus
FROM OrdItem oi
JOIN Ord o ON oi.OrdKey = o.OrdKey
WHERE o.OrdNumber = @OrdNumber AND o.BizDate = @BizDate;
```

**How to Interpret Results:**
- Items with `Total = 0` but `Price > 0` were likely voided

---

### Problem 4: Same order printed twice

**What to Look For:** Check kitchen print logs and order modification times.

**SQL Query:**
```sql
DECLARE @OrdNumber INT = 12345;
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    k.KDOrdKey,
    k.OrdNumber,
    k.BizDate,
    k.ReceivedTime,
    k.BumpTime,
    k.Station
FROM KDOrd k
WHERE k.OrdNumber = @OrdNumber AND k.BizDate = @BizDate;
```

**How to Interpret Results:**
- Multiple entries in `KDOrd` = multiple kitchen sends

---

### Problem 5: Order got stuck and won't close out

**What to Look For:** Check for order locks, incomplete payments, or required fields.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    o.OrdKey,
    o.OrdNumber,
    o.OrdType,
    o.OrdStartTime,
    o.OrdCloseTime,
    o.Total,
    o.AmountPaid,
    (o.Total - ISNULL(o.AmountPaid, 0)) AS BalanceDue,
    o.IsPaid,
    e.LastName AS Server
FROM Ord o
LEFT JOIN Employee e ON o.SvrKey = e.EmployeeKey
WHERE o.BizDate = @BizDate
  AND o.OrdCloseTime IS NULL
  AND o.OrdStartTime < DATEADD(hour, -2, GETDATE());
```

**How to Interpret Results:**
- `OrdCloseTime IS NULL` with old `OrdStartTime` = stuck order
- `BalanceDue > 0` means payment incomplete

---

### Problem 6: Tax amount looks wrong on order

**What to Look For:** Check which tax rates were applied.

**SQL Query:**
```sql
DECLARE @OrdNumber INT = 12345;
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    o.OrdNumber,
    o.SubTotal,
    o.Tax,
    o.Total,
    CASE WHEN o.SubTotal > 0
         THEN CAST((o.Tax / o.SubTotal) * 100 AS DECIMAL(5,2))
         ELSE 0 END AS EffectiveTaxRate
FROM Ord o
WHERE o.OrdNumber = @OrdNumber AND o.BizDate = @BizDate;

SELECT
    t.TaxName,
    t.TaxRate,
    t.TaxableAmt,
    t.TaxAmt
FROM OrdTax t
JOIN Ord o ON t.OrdKey = o.OrdKey
WHERE o.OrdNumber = @OrdNumber AND o.BizDate = @BizDate;
```

**How to Interpret Results:**
- Compare `EffectiveTaxRate` to your location's actual tax rate

---

### Problem 7: Future order didn't fire at right time

**What to Look For:** Check deferred order settings and scheduled time vs actual fire time.

**SQL Query:**
```sql
DECLARE @StartDate DATE = '2025-12-09';
DECLARE @EndDate DATE = '2025-12-10';

SELECT
    d.OrdDeferKey,
    o.OrdNumber,
    o.OrdType,
    o.OrdStartTime AS OrderCreated,
    d.DeferTime AS ScheduledFor,
    d.RecallTime AS ActualFireTime,
    d.IsRecalled,
    DATEDIFF(minute, d.DeferTime, d.RecallTime) AS MinutesOffSchedule
FROM OrdDefer d
JOIN Ord o ON d.OrdKey = o.OrdKey
WHERE o.BizDate BETWEEN @StartDate AND @EndDate
ORDER BY d.DeferTime;
```

**How to Interpret Results:**
- `IsRecalled = 0` means order never fired

---

### Problem 8: Can't find an order that should exist

**What to Look For:** Search across multiple dates.

**SQL Query:**
```sql
DECLARE @ApproxTotal MONEY = 45.00;
DECLARE @DateRange INT = 7;

SELECT
    o.OrdKey,
    o.OrdNumber,
    o.BizDate,
    o.Total,
    o.OrdStatus,
    e.LastName AS Server
FROM Ord o
LEFT JOIN Employee e ON o.SvrKey = e.EmployeeKey
WHERE o.BizDate >= DATEADD(day, -@DateRange, CAST(GETDATE() AS DATE))
  AND o.Total BETWEEN @ApproxTotal - 5 AND @ApproxTotal + 5
ORDER BY o.BizDate DESC;
```

---

### Problem 9: Order stuck in wrong status

**What to Look For:** Check current status code.

**SQL Query:**
```sql
DECLARE @OrdNumber INT = 12345;
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    o.OrdNumber,
    o.OrdStatus,
    o.OrdType,
    o.IsPaid,
    o.AmountPaid,
    o.Total
FROM Ord o
WHERE o.OrdNumber = @OrdNumber AND o.BizDate = @BizDate;
```

---

### Problem 10: Split check created duplicate items

**What to Look For:** Check split configuration.

**SQL Query:**
```sql
DECLARE @OrdNumber INT = 12345;
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    oi.ItemName,
    SUM(oi.Qty) AS TotalQty,
    COUNT(*) AS AppearanceCount
FROM Ord o
JOIN OrdItem oi ON o.OrdKey = oi.OrdKey
WHERE o.BizDate = @BizDate
  AND o.TableNum = (SELECT TableNum FROM Ord WHERE OrdNumber = @OrdNumber AND BizDate = @BizDate)
GROUP BY oi.ItemName
HAVING COUNT(*) > 1;
```

---

## Category 2: Payments & Credit Cards

**Key Tables:** `OrdPayment`, `CCTrans`, `CCTransLog`, `CCBatches`, `PaymentType`

---

### Problem 11: Credit card payment went through but order shows unpaid

**What to Look For:** Payment processor approved but POS didn't record it.

**SQL Query:**
```sql
DECLARE @OrdNumber INT = 12345;
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    o.OrdNumber,
    o.Total,
    o.AmountPaid,
    o.IsPaid,
    o.Total - ISNULL(o.AmountPaid, 0) AS BalanceDue
FROM Ord o
WHERE o.OrdNumber = @OrdNumber AND o.BizDate = @BizDate;

SELECT
    p.PaymentType,
    p.Amount,
    p.Tip,
    p.AuthCode,
    p.Last4Digits,
    p.PaymentTime
FROM OrdPayment p
JOIN Ord o ON p.OrdKey = o.OrdKey
WHERE o.OrdNumber = @OrdNumber AND o.BizDate = @BizDate;
```

---

### Problem 12: Customer charged twice for same order

**What to Look For:** Look for duplicate transactions in CC logs.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';
DECLARE @Last4 VARCHAR(4) = '1234';

SELECT
    ctl.TransactionAmount,
    ctl.Last4,
    COUNT(*) AS TransactionCount,
    MIN(ctl.TransactionTime) AS FirstCharge,
    MAX(ctl.TransactionTime) AS LastCharge
FROM CCTransLog ctl
JOIN CCTrans ct ON ctl.CCTransKey = ct.CCTransKey
WHERE ct.BizDate = @BizDate
  AND ctl.Last4 = @Last4
GROUP BY ctl.TransactionAmount, ctl.Last4
HAVING COUNT(*) > 1;
```

---

### Problem 13: Credit card batch didn't settle

**What to Look For:** Check batch status and settlement response codes.

**SQL Query:**
```sql
SELECT
    b.CCBatchKey,
    b.BatchID,
    b.BizDate,
    b.IsOpen,
    b.CloseTime,
    b.HostBatchAmount,
    b.HostResponseCode,
    b.HostResponseMessage
FROM CCBatches b
WHERE b.BizDate >= DATEADD(day, -7, CAST(GETDATE() AS DATE))
ORDER BY b.BizDate DESC;
```

**How to Interpret Results:**
- `IsOpen = 1` means batch hasn't settled

---

### Problem 14: Tip amounts not matching what server reported

**What to Look For:** Compare tip amounts in OrdPayment.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    e.LastName + ', ' + e.FirstName AS Server,
    SUM(p.Tip) AS TotalCCTips,
    COUNT(DISTINCT o.OrdKey) AS OrderCount
FROM OrdPayment p
JOIN Ord o ON p.OrdKey = o.OrdKey
JOIN Employee e ON o.SvrKey = e.EmployeeKey
WHERE o.BizDate = @BizDate
GROUP BY e.LastName, e.FirstName;
```

---

### Problem 15: Card declined but system shows it went through

**What to Look For:** Check response codes.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';
DECLARE @Last4 VARCHAR(4) = '1234';

SELECT
    ctl.TransactionTime,
    ctl.TransactionAmount,
    ctl.ApprovalNumber,
    ctl.GtwyResponseCode,
    ctl.GtwyResponseMessage,
    CASE
        WHEN ctl.ApprovalNumber IS NOT NULL THEN 'APPROVED'
        WHEN ctl.GtwyResponseCode IN ('05', '51', 'DECLINED') THEN 'DECLINED'
        ELSE 'CHECK RESPONSE'
    END AS TransactionStatus
FROM CCTransLog ctl
JOIN CCTrans ct ON ctl.CCTransKey = ct.CCTransKey
WHERE ct.BizDate = @BizDate
  AND ctl.Last4 = @Last4
ORDER BY ctl.TransactionTime;
```

---

### Problem 16: Can't find a refund transaction

**What to Look For:** Check refund payment records.

**SQL Query:**
```sql
DECLARE @StartDate DATE = '2025-12-01';
DECLARE @EndDate DATE = '2025-12-09';

SELECT
    o.OrdNumber,
    o.BizDate,
    p.PaymentType,
    p.Amount,
    p.AuthCode,
    p.Last4Digits
FROM OrdPayment p
JOIN Ord o ON p.OrdKey = o.OrdKey
WHERE o.BizDate BETWEEN @StartDate AND @EndDate
  AND (p.Amount < 0 OR p.PaymentType LIKE '%Refund%');
```

---

### Problem 17: Report shows $0 credit cards but we took cards

**What to Look For:** Check if payments are categorized correctly.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    p.PaymentType,
    COUNT(*) AS TransactionCount,
    SUM(p.Amount) AS TotalAmount
FROM OrdPayment p
WHERE p.BizDate = @BizDate
GROUP BY p.PaymentType;
```

---

## Category 3: Cash Drawers & Closing

**Key Tables:** `CashDrawer`, `CashDrawerUser`, `CashDrawerCfg`, `CashDrawerCashDetail`, `CashDrawerDrop`

---

### Problem 18: Cash drawer shows over/short at end of day

**What to Look For:** Compare expected vs actual counts.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';
DECLARE @DrawerName NVARCHAR(25) = 'Drawer 1';

SELECT
    cd.CashDrawerName,
    cd.StartingAmt,
    cd.CashRequired,
    cd.CashActual,
    cd.OverShort,
    (cd.CashActual - cd.CashRequired) AS CashVariance,
    cd.ReconciledBy
FROM CashDrawer cd
WHERE cd.BusinessDate = @BizDate
  AND cd.CashDrawerName = @DrawerName;
```

**How to Interpret Results:**
- Positive variance = over, negative = short

---

### Problem 19: Employee claims they weren't assigned to this drawer

**What to Look For:** Check drawer user assignments.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';
DECLARE @DrawerName NVARCHAR(25) = 'Drawer 1';

SELECT
    cd.CashDrawerName,
    cd.OpenedBy,
    cd.OpenTime,
    cd.ClosedBy,
    cd.CloseTime
FROM CashDrawer cd
WHERE cd.BusinessDate = @BizDate
  AND cd.CashDrawerName = @DrawerName;
```

---

### Problem 20: Drawer shows open but no one clocked in

**What to Look For:** Check drawer open time vs time clock.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';

SELECT
    cd.CashDrawerName,
    cd.OpenedBy,
    cd.OpenedByKey,
    cd.OpenTime,
    cd.Shared,
    CASE
        WHEN cd.OpenedByKey = 0 OR cd.OpenedByKey IS NULL THEN 'SYSTEM OPENED'
        ELSE 'EMPLOYEE OPENED'
    END AS OpenType
FROM CashDrawer cd
WHERE cd.BusinessDate = @BizDate
  AND cd.CloseTime IS NULL;
```

---

### Problem 21: Multiple people used same drawer, can't reconcile

**What to Look For:** Identify all employees who used the drawer.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';
DECLARE @DrawerName NVARCHAR(25) = 'Drawer 1';

SELECT
    e.LastName + ', ' + e.FirstName AS EmployeeName,
    p.PaymentType,
    COUNT(*) AS TransCount,
    SUM(p.Amount) AS TotalAmount
FROM OrdPayment p
JOIN Ord o ON p.OrdKey = o.OrdKey
JOIN Employee e ON o.SvrKey = e.EmployeeKey
WHERE p.CashDrawerKey = (
    SELECT CashDrawerKey FROM CashDrawer
    WHERE BusinessDate = @BizDate AND CashDrawerName = @DrawerName
)
GROUP BY e.LastName, e.FirstName, p.PaymentType
ORDER BY e.LastName;
```

---

### Problem 22: Cash drop not recorded

**What to Look For:** Check drop records.

**SQL Query:**
```sql
DECLARE @BizDate DATE = '2025-12-09';
DECLARE @DrawerName NVARCHAR(25) = 'Drawer 1';

SELECT
    cdd.DateTime,
    cdd.DropBy,
    cdd.FromCD,
    cdd.ToCD,
    cdd.Cash,
    cdd.TotalDrop
FROM CashDrawerDrop cdd
WHERE cdd.BizDate = @BizDate
  AND cdd.FromCD = @DrawerName;
```

---

### Problem 23-27: Additional Cash Drawer Issues

See the full reference for queries covering:
- Safe drop didn't reduce drawer count
- Two drawers showing same transactions
- Driver tips don't match POS
- Paid-out not reflected in count
- Closed day but totals are wrong

---

## Category 4: Employees & Time Clock

**Key Tables:** `Employee`, `TimeClock`, `TimeClockAudit`, `EmployeeSched`, `LaborType`

---

### Problem 28: Employee can't clock in - system says already clocked in

**What to Look For:** Find open clock-in records.

**SQL Query:**
```sql
SELECT
    tc.EmployeeKey,
    tc.EmployeeFName + ' ' + tc.EmployeeLName AS EmployeeName,
    tc.BusinessDate,
    tc.InTime,
    tc.LaborType,
    tc.TimeClockKey,
    DATEDIFF(MINUTE, tc.InTime, GETDATE()) AS MinutesClocked
FROM TimeClock tc
WHERE tc.OutTime IS NULL
  AND tc.InTime IS NOT NULL
ORDER BY tc.InTime DESC;
```

**How to Interpret Results:**
- MinutesClocked > 1440 = Likely forgot to clock out

---

### Problem 29: Dashboard shows 4 clocked in but time clock shows 3

**What to Look For:** Different filtering criteria between displays.

**SQL Query:**
```sql
SELECT
    'Current Business Date' AS Source,
    COUNT(*) AS ClockedInCount
FROM TimeClock
WHERE OutTime IS NULL AND InTime IS NOT NULL
  AND BusinessDate = CAST(GETDATE() AS DATE)
UNION ALL
SELECT
    'All Open Clock-Ins' AS Source,
    COUNT(*) AS ClockedInCount
FROM TimeClock
WHERE OutTime IS NULL AND InTime IS NOT NULL;
```

---

### Problem 30: Time clock hours don't add up

**What to Look For:** Calculate actual hours between InTime and OutTime.

**SQL Query:**
```sql
SELECT TOP 50
    tc.TimeClockKey,
    tc.EmployeeFName + ' ' + tc.EmployeeLName AS EmployeeName,
    tc.BusinessDate,
    tc.InTime,
    tc.OutTime,
    CAST(DATEDIFF(MINUTE, tc.InTime, tc.OutTime) / 60.0 AS DECIMAL(10,2)) AS HoursWorked,
    CASE
        WHEN DATEDIFF(MINUTE, tc.InTime, tc.OutTime) < 0 THEN 'NEGATIVE HOURS'
        WHEN DATEDIFF(MINUTE, tc.InTime, tc.OutTime) > 1440 THEN 'OVER 24 HOURS'
        ELSE 'NORMAL'
    END AS HourStatus
FROM TimeClock tc
WHERE tc.OutTime IS NOT NULL AND tc.InTime IS NOT NULL
ORDER BY tc.BusinessDate DESC;
```

---

### Problem 31: Employee's PIN isn't working

**What to Look For:** Check employee account status.

**SQL Query:**
```sql
SELECT
    e.EmployeeKey,
    e.FirstName + ' ' + e.LastName AS EmployeeName,
    e.IsActive,
    e.ReqTimeClock,
    e.TermDate,
    CASE
        WHEN e.IsActive = 0 THEN 'INACTIVE - Cannot login'
        WHEN e.TermDate IS NOT NULL THEN 'TERMINATED - Cannot login'
        ELSE 'ACTIVE - Should work'
    END AS Status
FROM Employee e
WHERE e.LastName LIKE '%Smith%';
```

---

### Problem 32-36: Additional Employee Issues

See the full reference for queries covering:
- Schedule shows employee working but not in timeclock
- New employee added but doesn't appear on POS
- Edited time not showing in payroll
- Added clock-in created duplicate
- Hours don't match between reports

---

## Category 5: Permissions & Security

**Key Tables:** `Employee`, `LaborType`, `SecGrp`, `SecGrpRights`, `SecIndRights`, `SecRightsDefault`

---

### Problem 37: Cashier can't void or comp an order

**What to Look For:** Check "Allow Comp" and "Allow Refund" permissions.

**SQL Query:**
```sql
SELECT
    e.FirstName + ' ' + e.LastName AS EmployeeName,
    lt.LaborType,
    lt.SecurityGrp,
    srd.ItemName AS Permission,
    COALESCE(sir.Setting, sgr.Setting, srd.DefaultVal) AS EffectiveSetting,
    CASE
        WHEN COALESCE(sir.Setting, sgr.Setting, srd.DefaultVal) = 1 THEN 'ALLOWED'
        ELSE 'DENIED'
    END AS Status
FROM Employee e
LEFT JOIN LaborType lt ON lt.SecurityGrp IS NOT NULL
LEFT JOIN SecGrp sg ON lt.SecurityGrp = sg.Name
LEFT JOIN SecRightsDefault srd ON srd.ItemName IN ('Allow Comp', 'Allow Refund')
LEFT JOIN SecGrpRights sgr ON sgr.SecGroupKey = sg.SecGroupKey AND sgr.RightKey = srd.SecRightsKey
LEFT JOIN SecIndRights sir ON sir.UserKey = e.EmployeeKey AND sir.DefRightsKey = srd.SecRightsKey
WHERE e.LastName LIKE '%Smith%' AND e.IsActive = 1
ORDER BY srd.ItemName;
```

**How to Interpret Results:**
- EffectiveSetting = 0 means Permission DENIED

---

### Problem 38-41: Additional Permission Issues

See the full reference for queries covering:
- Manager override code not working
- Employee can see button but it's grayed out
- New employee can't log in
- System requiring PIN unexpectedly

---

## Category 6: Menu & Items

**Key Tables:** `Menus`, `MenuGrps`, `MenuItms`, `MenuMds`, `MenuSzs`, `MenuCpns`, `MenuGrpItmXRef`

---

### Problem 42: Menu item isn't showing up on POS screen

**What to Look For:** Check if item exists and has button position.

**SQL Query:**
```sql
DECLARE @ItemName NVARCHAR(50) = 'Pizza';

SELECT
    mi.ItemName,
    mi.ButtonName,
    mgix.MenuName,
    mgix.GroupName,
    mgix.Price,
    mgix.PosPage,
    mgix.PosX,
    mgix.PosY,
    CASE
        WHEN mgix.SyncStatus = 0 THEN 'Synced'
        ELSE 'Pending Sync'
    END AS SyncStatus
FROM MenuItms mi
LEFT JOIN MenuGrpItmXRef mgix ON mi.ItemName = mgix.ItemName
WHERE mi.ItemName LIKE '%' + @ItemName + '%';
```

**How to Interpret Results:**
- PosPage/PosX/PosY NULL = No button position assigned

---

### Problem 43-49: Additional Menu Issues

See the full reference for queries covering:
- Price shows wrong on screen
- Modifier option isn't available for item
- Coupon isn't applying to order
- Size options not appearing
- Item ringing up in wrong group
- 86'd item still showing
- New menu item not syncing

---

## Category 7: Printing Issues

**Key Tables:** `Printer`, `PrinterKtnPrtCatXref`, `MenuKtchPrtCat`, `PrintJobs`, `OrdDefer`

---

### Problem 50: Why didn't pizza print at Printer1 for order 45?

**What to Look For:** Check if the item's print category is assigned to that printer.

**SQL Query:**
```sql
SELECT
    oi.BizDate,
    oi.OrdNumber,
    oi.ItemName,
    oi.KtchPrtCat AS ItemPrintCategory,
    oi.IsPrinted,
    oi.IsVoid,
    pkx.Printer AS PrinterAssigned,
    p.IsActive AS PrinterActive,
    p.IsKtcn AS IsKitchenPrinter
FROM OrdItem oi
LEFT JOIN PrinterKtnPrtCatXref pkx ON oi.KtchPrtCat = pkx.PrtCat
LEFT JOIN Printer p ON pkx.Printer = p.PrinterName
WHERE oi.BizDate = '2025-07-23' AND oi.OrdNumber = 45;
```

**How to Interpret Results:**
- `IsPrinted = 0` means item never printed
- If `PrinterAssigned` is NULL, category isn't routed to any printer

---

### Problem 51-58: Additional Printing Issues

See the full reference for queries covering all printing scenarios.

---

## Category 8: Kitchen Display - KDS

**Key Tables:** `KDOrd`, `KDOrdItem`, `KDOrdItemMod`, `KtchDisp`

---

### Problem 59: Order not showing on kitchen display

**What to Look For:** Check if order exists in KDS tables.

**SQL Query:**
```sql
SELECT
    kd.KDOrdKey,
    kd.BizDate,
    kd.OrdNumber,
    kd.OrdType,
    kd.Computer AS DisplayStation,
    (SELECT COUNT(*) FROM KDOrdItem ki WHERE ki.OrdKey = kd.OrdKey) AS ItemCount
FROM KDOrd kd
WHERE kd.BizDate = '2025-07-23' AND kd.OrdNumber = 45;
```

---

### Problem 60-62: Additional KDS Issues

See the full reference for queries covering bumped items, wrong station, and modifier printing.

---

## Category 9: Delivery

**Key Tables:** `DeliveryOrder`, `DeliveryDriver`, `DeliveryQueue`, `Zones`, `DeliveryOpts`

---

### Problem 63: Driver says order was assigned but it's not on their list

**What to Look For:** Check delivery order assignment records.

**SQL Query:**
```sql
SELECT
    do.DeliveryOrderKey,
    do.BizDate,
    do.OrderNum,
    do.DriverKey,
    dd.DriverName,
    dd.Active AS DriverCurrentlyActive,
    do.DispatchTime,
    do.ReturnTime
FROM DeliveryOrder do
LEFT JOIN DeliveryDriver dd ON do.DriverKey = dd.DeliveryDriverKey
WHERE do.BizDate = '2025-07-23' AND do.OrderNum = 45;
```

---

### Problem 64-68: Additional Delivery Issues

See the full reference for queries covering delivery timing, addresses, fees, and driver pool.

---

## Category 10: Customers

**Key Tables:** `Customer`, `CustomerPhone`, `CustomerAddr`, `CustAcct`, `OrdCust`

---

### Problem 69: Customer has duplicate records

**What to Look For:** Multiple customer records for the same person.

**SQL Query:**
```sql
SELECT
    cp.PhoneNum,
    COUNT(DISTINCT c.CustomerKey) AS DuplicateCount,
    STRING_AGG(CAST(c.CustomerKey AS VARCHAR), ', ') AS CustomerKeys
FROM Customer c
JOIN CustomerPhone cp ON c.CustomerKey = cp.CustomerKey
WHERE cp.PhoneNum <> ''
GROUP BY cp.PhoneNum
HAVING COUNT(DISTINCT c.CustomerKey) > 1
ORDER BY DuplicateCount DESC;
```

---

### Problem 70-74: Additional Customer Issues

See the full reference for queries covering phone lookup, addresses, tax exempt, loyalty points, and order history.

---

## Category 11: Pricing & Fees

**Key Tables:** `MenuCpns`, `MenuTimePrice`, `DeliveryOpts`, `Zones`, `SysConfig`

---

### Problem 75: Delivery fee shows $2.99 but should be $2.75

**What to Look For:** Check delivery fee configuration.

**SQL Query:**
```sql
SELECT
    d.DeliveryOptKey,
    d.DeliveryFee AS FeeEnabled,
    d.DeliveryFeeType,
    d.DeliveryFeeVal AS BaseFeeAmount,
    d.UseZones
FROM DeliveryOpts d;

SELECT
    z.ZoneKey,
    z.ZoneName,
    z.Deliver AS DeliveryEnabled,
    z.AddFee AS AdditionalFee
FROM Zones z
WHERE z.Deliver = 1
ORDER BY z.ZoneName;
```

---

### Problem 76-81: Additional Pricing Issues

See the full reference for queries covering coupons, happy hour, and combo pricing.

---

## Category 12: Reports & Daily Close

**Key Tables:** `SumSales`, `SumProduct`, `SumSalesByTime`, `SumPayment`, `SumAdj`

---

### Problem 82: End of day totals don't match receipts

**What to Look For:** Compare summary sales with actual order totals.

**SQL Query:**
```sql
SELECT
    ss.BizDate,
    ss.GrossSales AS ReportedGross,
    ss.NetSales AS ReportedNet,
    ss.Tax AS ReportedTax,
    ss.OrdCnt AS ReportedOrderCount
FROM SumSales ss
WHERE ss.BizDate = '2024-01-15'
ORDER BY ss.BizDate DESC;
```

---

### Problem 83-87: Additional Report Issues

See the full reference for queries covering product mix, labor cost, hourly sales, voids, and drawer reconciliation.

---

## Category 13: Synchronization & Multi-Location

**Key Tables:** `SyncRecords`, tables with `EntID`, `EntSync`, `SyncStatus` columns

---

### Problem 88: Menu changes not syncing to other locations

**What to Look For:** Check SyncRecords for pending or error statuses.

**SQL Query:**
```sql
SELECT
    sr.SyncRecordsKey,
    sr.TableName,
    sr.SyncStatus,
    sr.EntSync,
    sr.Operation
FROM SyncRecords sr
WHERE sr.TableName IN (
    'MenuItms', 'MenuGrps', 'MenuCpns', 'MenuMds'
)
ORDER BY sr.EntSync DESC;
```

**How to Interpret Results:**
- SyncStatus 0 = Synced successfully
- SyncStatus 1 = Pending sync
- SyncStatus 2 = Error/Failed

---

### Problem 89-91: Additional Sync Issues

See the full reference for queries covering cross-location orders, sync errors, and employee syncing.

---

## Category 14: System & Configuration

**Key Tables:** `SysConfig`, `Computer`, `Business`, `BusinessDate`, `AuditLog`, `EventLog`

---

### Problem 92: Terminal not communicating with server

**What to Look For:** Check Computer table for terminal status.

**SQL Query:**
```sql
SELECT
    c.ComputerKey,
    c.ComputerName,
    c.IPAddr,
    c.IsActive,
    c.TimeStamp AS LastActivity,
    DATEDIFF(minute, c.TimeStamp, GETDATE()) AS MinutesSinceActivity,
    c.Role
FROM Computer c
ORDER BY c.TimeStamp DESC;
```

**How to Interpret Results:**
- MinutesSinceActivity > 30 = Terminal may be offline

---

### Problem 93: Settings changed but not taking effect

**What to Look For:** Verify settings in SysConfig were saved.

**SQL Query:**
```sql
SELECT
    sc.SysConfigKey,
    sc.LastUpdate,
    sc.SyncStatus,
    sc.EntSync
FROM SysConfig sc;
```

---

### Problem 94: Business date showing wrong date

**What to Look For:** Check the BusinessDate table.

**SQL Query:**
```sql
SELECT TOP 10
    bd.BusinessDateKey,
    bd.BusinessDate,
    bd.Status,
    bd.Reopened,
    bd.ClosedTime,
    bd.ClosedBy
FROM BusinessDate bd
ORDER BY bd.BusinessDate DESC;
```

**How to Interpret Results:**
- Status = 1 = Open
- Status = 3 = Closed

---

### Problem 95: Audit trail shows unauthorized access

**What to Look For:** Query AuditLog for sensitive actions.

**SQL Query:**
```sql
SELECT TOP 50
    al.AuditKey,
    al.BizDate,
    al.Computer,
    al.AuditTime,
    al.UserName,
    al.ApprovalName,
    al.ActionName,
    al.OrderNumber,
    al.Amount
FROM AuditLog al
WHERE al.ActionName IN (
    'Void Order', 'Void Item', 'Remove Payment',
    'No Sale', 'Refund', 'Comp', 'Price Override'
)
ORDER BY al.AuditTime DESC;
```

---

### Problem 96: Remote update failed

**What to Look For:** Check RU_Jobs and RU_JobHistory tables.

**SQL Query:**
```sql
SELECT TOP 30
    jh.HistoryID,
    j.JobName,
    j.JobDesc,
    jh.Run_Status,
    jh.Run_Date,
    jh.Message
FROM RU_JobHistory jh
JOIN RU_Jobs j ON jh.JobID = j.JobID
ORDER BY jh.Run_Date DESC;
```

**How to Interpret Results:**
- Run_Status = 1 = Success
- Run_Status = 0 = Failed

---

## Quick Reference Summary

| Category | Questions | Key Tables |
|----------|-----------|------------|
| Orders | 1-10 | Ord, OrdItem, OrdPayment |
| Payments | 11-17 | OrdPayment, CCTrans, CCTransLog |
| Cash Drawers | 18-27 | CashDrawer, CashDrawerUser |
| Employees | 28-36 | Employee, TimeClock |
| Permissions | 37-41 | SecGrp, SecGrpRights |
| Menu | 42-49 | MenuItms, MenuGrps |
| Printing | 50-58 | Printer, PrintJobs |
| KDS | 59-62 | KDOrd, KDOrdItem |
| Delivery | 63-68 | DeliveryOrder, Zones |
| Customers | 69-74 | Customer, CustomerPhone |
| Pricing | 75-81 | MenuCpns, DeliveryOpts |
| Reports | 82-87 | SumSales, SumProduct |
| Sync | 88-91 | SyncRecords |
| System | 92-96 | SysConfig, Computer |
| **Total** | **96** | |

---

## Status Code Reference

### SyncStatus
| Value | Meaning |
|-------|---------|
| 0 | Synced / Success |
| 1 | Pending sync |
| 2 | Error / Failed |

### BusinessDate.Status
| Value | Meaning |
|-------|---------|
| 1 | Open |
| 3 | Closed |

### Computer.Role
| Value | Meaning |
|-------|---------|
| 0 | Workstation |
| 1 | Server |

### Order Status
| Value | Meaning |
|-------|---------|
| 0 | Open/Active |
| 1 | Sent to Kitchen |
| 2 | Ready |
| 3 | Closed/Completed |
| 9 | Voided |

---

## Related Notes

- [[03 - SQL-Solvable Troubleshooting Issues]] - Master problem list
- [[01 - Cashier Cant Void or Comp]] - Detailed walkthrough example
- [[00 - RAG Project Overview]]



