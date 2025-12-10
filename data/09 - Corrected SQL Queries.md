# Corrected SQL Queries - VERIFIED WORKING
## Document 09 - Tested Against Actual Database

**Generated:** 2025-12-10 15:10:23
**Database:** REVENTION

---

## Query Status Legend

- **Working** - Query tested and returned results successfully
- **Error** - Query failed, see error message

---

### Recent Orders

**Status:** Working (10 rows)

```sql
SELECT TOP 10 OrdKey, OrdNumber, BizDate FROM Ord ORDER BY OrdKey DESC
```

**Columns:** `OrdKey, OrdNumber, BizDate`

---

### Active Employees

**Status:** Working (10 rows)

```sql
SELECT TOP 10 EmployeeKey, FirstName, LastName, IsActive FROM Employee WHERE IsActive = 1 ORDER BY EmployeeKey DESC
```

**Columns:** `EmployeeKey, FirstName, LastName, IsActive`

---

### Security Groups

**Status:** Working (7 rows)

```sql
SELECT * FROM SecGrp ORDER BY SecGroupKey
```

**Columns:** `SecGroupKey, Name, CreatedBy, CreatedDate, EntSync, SyncStatus, EntID, SecLevel`

---

### Menu Items

**Status:** Working (10 rows)

```sql
SELECT TOP 10 ItemName FROM MenuItms ORDER BY ItemName DESC
```

**Columns:** `ItemName`

---

### Cash Drawer Status

**Status:** Working (10 rows)

```sql
SELECT TOP 10 * FROM CashDrawer ORDER BY CashDrawerKey DESC
```

**Columns:** `CashDrawerKey, CashDrawerName, BusinessDate, Computer, StartingAmt, Shared, CDType, DelDrvKey, OpenedBy, OpenedByKey, OpenTime, ClosedBy, CloseTime, CashRequired, CashActual, ChecksRequired, ChecksActual, CreditRequired, CreditActual, GiftCertRequired, GiftCertActual, AcctRequired, AcctActual, TotalSales, OverShort, ReconciledBy, ReconcileTime, DelComp, CashoutToDwr, CCTips, RegTips, Grat, CCTipFee, OnlineCCPmts, BegMileage, EndMileage, DwrOpen, MaxCash, OpenRestrict, TCKey, OtherPmts, TippedEmp, NoSaleCnt, TipOut, GCCnt, GCAmt, MaxErrCnt, CurErrCnt, DrvCCTipsDrop, CCTipsFromOther, Tax, EntSync, SyncStatus, EntID`

---

### Recent Payments

**Status:** Working (10 rows)

```sql
SELECT TOP 10 * FROM OrdPayment ORDER BY OrdPaymentKey DESC
```

**Columns:** `OrdPaymentKey, BizDate, OrdNumber, PaymentTime, CashDrawerKey, OrigCashDrawerKey, PmtToDriver, PaymentType, PaymentTypeCategory, CardType, Amount, PreAuthTip, Tip, Reconciled, AddedByDriver, AuthCode, TransId, Last4Digits, PayerName, VReconciled, ToDwr, PaymentBizDate, SplitNumber, EmployeeKey, GiftSeqNum, CustAcctNum, ApprovalKey, ExcessTender, Tendered, TipSvrDwrKey, DeferCC, LUuuid, Signature, EyeDeliverTip, EntSync, SyncStatus, EntID, PMSInquiry, PMSInquiryType, PMSRoomNum, PMSProfileID, PMSGuestName, Grat`

---

### Time Clock Entries

**Status:** Working (10 rows)

```sql
SELECT TOP 10 * FROM TimeClock ORDER BY TimeClockKey DESC
```

**Columns:** `TimeClockKey, BusinessDate, EmployeeKey, EmployeeFName, EmployeeLName, RecordType, InTime, OutTime, LaborType, Rate, AdditionalComp, LastUpdateBy, LastUpdateTime, Tips, BegMileage, EndMileage, ShiftPay, BreakType, MinTime, BreakAppr, AutoOut, EntSync, SyncStatus, EntID, EstMiles, AddMiles`

---

### Customers

**Status:** Working (10 rows)

```sql
SELECT TOP 10 * FROM Customer ORDER BY CustomerKey DESC
```

**Columns:** `CustomerKey, AddrKey, LastName, FirstName, CustID, SpNote, DelNote, FirstOrdDate, LastOrdDate, LastOrdNum, OrdCnt, OrdAmt, TaxExempt, TaxNum, AcceptChecks, LastChanged, Created, BadChecksCust, PctDiscount, Points, Email, PctDiscAppr, FirstOLDate, LastOLDate, OLCnt, OLAmt, OptOut, LoyaltyPoints, LoyaltyCredit, AVSZip, AVSStNum, AVSManual, CpnUsage, RewardsMember, LoyaltyNum, EntSync, SyncStatus, EntID, LtyChkTime`

---

### Delivery Orders

**Status:** Working (10 rows)

```sql
SELECT TOP 10 * FROM DeliveryOrder ORDER BY DeliveryOrderKey DESC
```

**Columns:** `DeliveryOrderKey, BizDate, DriverKey, OrderNum, DispatchTime, ReturnTime, Amt, Tip, SubTotal, Sum, DeliveryTime, SyncStatus, PmtType, EntSync, EntID, EstTime, EstDist, TPMessage, TPStatus`

---

### Credit Card Transactions

**Status:** Working (10 rows)

```sql
SELECT TOP 10 * FROM CCTrans ORDER BY CCTransKey DESC
```

**Columns:** `CCTransKey, BizDate, AppType, StationId, Signature, EntID, EntSync, SyncStatus, InitTime`

---


## Common Query Patterns (Corrected)

### Find Order by Number

Based on actual Ord table columns:

```sql
-- First, check what columns exist in Ord
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Ord' ORDER BY ORDINAL_POSITION;

-- Then use the correct column names in your query
SELECT * FROM Ord WHERE OrdNumber = 12345;
```

### Employee Permissions

```sql
-- Find security-related columns in Employee
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Employee' AND COLUMN_NAME LIKE '%Sec%';

-- Join Employee to SecGrp (adjust column names as needed)
SELECT e.*, s.Name AS SecurityGroupName
FROM Employee e
LEFT JOIN SecGrp s ON e.SecGroupKey = s.SecGroupKey;
```

### Cash Drawer Reconciliation

```sql
-- Cash drawer with closing info
SELECT
    CashDrawerKey,
    CashDrawerName,
    BusinessDate,
    OpenedBy,
    OpenTime,
    ClosedBy,
    CloseTime,
    CashRequired,
    CashActual,
    OverShort
FROM CashDrawer
WHERE BusinessDate = CAST(GETDATE() AS DATE)
ORDER BY OpenTime;
```

