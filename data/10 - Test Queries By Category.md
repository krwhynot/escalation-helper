# Working Test Queries by Category
## Document 10 - VERIFIED WORKING Queries

**Generated:** 2025-12-10 15:10:23
**Database:** REVENTION

All queries below have been tested and confirmed working.

---

## Orders

**Status:** Working

```sql
SELECT TOP 5 * FROM Ord ORDER BY 1 DESC
```

**Columns (82):** `OrdKey, BizDate, OrdNumber, Menu, OrdType, OrdStation, OrdStartTime, OrdStartEmplKey, OrdUpdateTime, OrdUpdateEmplKey` ... +72 more

**Rows returned:** 5

---

## Order Items

**Status:** Working

```sql
SELECT TOP 5 * FROM OrdItem ORDER BY 1 DESC
```

**Columns (102):** `OrdItemKey, BizDate, OrdNumber, OrdItemNumber, ItemName, KtchName, RcptName, GroupName, KtchPrtCat, TaxType` ... +92 more

**Rows returned:** 5

---

## Payments

**Status:** Working

```sql
SELECT TOP 5 * FROM OrdPayment ORDER BY OrdPaymentKey DESC
```

**Columns (43):** `OrdPaymentKey, BizDate, OrdNumber, PaymentTime, CashDrawerKey, OrigCashDrawerKey, PmtToDriver, PaymentType, PaymentTypeCategory, CardType` ... +33 more

**Rows returned:** 5

---

## Credit Cards

**Status:** Working

```sql
SELECT TOP 5 * FROM CCTrans ORDER BY CCTransKey DESC
```

**Columns (9):** `CCTransKey, BizDate, AppType, StationId, Signature, EntID, EntSync, SyncStatus, InitTime`

**Rows returned:** 5

---

## Cash Drawers

**Status:** Working

```sql
SELECT TOP 5 * FROM CashDrawer ORDER BY CashDrawerKey DESC
```

**Columns (54):** `CashDrawerKey, CashDrawerName, BusinessDate, Computer, StartingAmt, Shared, CDType, DelDrvKey, OpenedBy, OpenedByKey` ... +44 more

**Rows returned:** 5

---

## Employees

**Status:** Working

```sql
SELECT TOP 5 * FROM Employee ORDER BY EmployeeKey DESC
```

**Columns (52):** `EmployeeKey, EmployeeID, FirstName, LastName, NickName, SSNum, Address1, Address2, City, State` ... +42 more

**Rows returned:** 5

---

## Time Clock

**Status:** Working

```sql
SELECT TOP 5 * FROM TimeClock ORDER BY TimeClockKey DESC
```

**Columns (26):** `TimeClockKey, BusinessDate, EmployeeKey, EmployeeFName, EmployeeLName, RecordType, InTime, OutTime, LaborType, Rate` ... +16 more

**Rows returned:** 5

---

## Security Groups

**Status:** Working

```sql
SELECT * FROM SecGrp
```

**Columns (8):** `SecGroupKey, Name, CreatedBy, CreatedDate, EntSync, SyncStatus, EntID, SecLevel`

**Rows returned:** 7

---

## Security Rights

**Status:** Working

```sql
SELECT TOP 5 * FROM SecGrpRights
```

**Columns (7):** `SecGroupRightsKey, SecGroupKey, RightKey, Setting, EntSync, SyncStatus, EntID`

**Rows returned:** 5

---

## Menu Items

**Status:** Working

```sql
SELECT TOP 5 * FROM MenuItms ORDER BY 1 DESC
```

**Columns (10):** `ItemName, ButtonName, ReceiptName, KitchenName, MenuCategory, OnlineName, EntSync, SyncStatus, EntID, MenuItmsKey`

**Rows returned:** 5

---

## Menu Groups

**Status:** Working

```sql
SELECT TOP 5 * FROM MenuGrps ORDER BY 1 DESC
```

**Columns (8):** `GroupName, ButtonName, MenuCategory, OnlineName, EntSync, SyncStatus, EntID, MenuGrpsKey`

**Rows returned:** 5

---

## Customers

**Status:** Working

```sql
SELECT TOP 5 * FROM Customer ORDER BY CustomerKey DESC
```

**Columns (39):** `CustomerKey, AddrKey, LastName, FirstName, CustID, SpNote, DelNote, FirstOrdDate, LastOrdDate, LastOrdNum` ... +29 more

**Rows returned:** 5

---

## Delivery Orders

**Status:** Working

```sql
SELECT TOP 5 * FROM DeliveryOrder ORDER BY DeliveryOrderKey DESC
```

**Columns (19):** `DeliveryOrderKey, BizDate, DriverKey, OrderNum, DispatchTime, ReturnTime, Amt, Tip, SubTotal, Sum` ... +9 more

**Rows returned:** 5

---

## Printers

**Status:** Working

```sql
SELECT * FROM Printer
```

**Columns (51):** `PrinterKey, ComputerName, PrinterName, Type, Interface, OPOS, WinPrinterName, IsKtcn, IsActive, TimeStamp` ... +41 more

**Rows returned:** 3

---

## Print Jobs

**Status:** Working

```sql
SELECT TOP 5 * FROM PrintJobs ORDER BY 1 DESC
```

**Columns (9):** `PrintJobKey, BizDate, OrdNum, PrtType, PrtQueue, PrtJob, Attempts, PrtName, CompName`

**Rows returned:** 0

---

## Sync Records

**Status:** Working

```sql
SELECT TOP 5 * FROM SyncRecords ORDER BY 1 DESC
```

**Columns (8):** `SyncRecordsKey, EntKey, EntID, TableName, SyncStatus, EntSync, Operation, TableKey`

**Rows returned:** 5

---

