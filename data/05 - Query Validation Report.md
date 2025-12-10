# Query Validation Report
## Document 05 - Table Reference Validation

**Generated:** 2025-12-10 15:08:53
**Database:** REVENTION
**Server:** 172.31.240.1\Revention

---

## Summary

| Category | Count |
|----------|-------|
| **Tables in Database** | 324 |
| **Tables Referenced in SQL Guide** | 59 |
| **Valid References** | 36 |
| **Invalid References** | 23 |
| **Validation Rate** | 61.0% |

---

## Valid Table References

The following 36 tables exist in the database:

| Referenced Name | Actual Name | Status |
|-----------------|-------------|--------|
| `AuditLog` | `AuditLog` | Exact match |
| `BackupLog` | `BackupLog` | Exact match |
| `CCBatches` | `CCBatches` | Exact match |
| `CCTrans` | `CCTrans` | Exact match |
| `CashDrawer` | `CashDrawer` | Exact match |
| `CashDrawerCfg` | `CashDrawerCfg` | Exact match |
| `Customer` | `Customer` | Exact match |
| `CustomerAddr` | `CustomerAddr` | Exact match |
| `CustomerPhone` | `CustomerPhone` | Exact match |
| `DeliveryDriver` | `DeliveryDriver` | Exact match |
| `DeliveryOrder` | `DeliveryOrder` | Exact match |
| `Employee` | `Employee` | Exact match |
| `EmployeeSched` | `EmployeeSched` | Exact match |
| `KDOrd` | `KDOrd` | Exact match |
| `MenuGrps` | `MenuGrps` | Exact match |
| `MenuItms` | `MenuItms` | Exact match |
| `MenuMds` | `MenuMds` | Exact match |
| `Menus` | `Menus` | Exact match |
| `Ord` | `Ord` | Exact match |
| `OrdCpn` | `OrdCpn` | Exact match |
| `OrdDefer` | `OrdDefer` | Exact match |
| `OrdItem` | `OrdItem` | Exact match |
| `OrdItemMod` | `OrdItemMod` | Exact match |
| `OrdItemRemovedAudit` | `OrdItemRemovedAudit` | Exact match |
| `OrdLock` | `OrdLock` | Exact match |
| `OrdNote` | `OrdNote` | Exact match |
| `OrdPayment` | `OrdPayment` | Exact match |
| `OrdTax` | `OrdTax` | Exact match |
| `PrintJobs` | `PrintJobs` | Exact match |
| `Printer` | `Printer` | Exact match |
| `SecGrp` | `SecGrp` | Exact match |
| `SecGrpRights` | `SecGrpRights` | Exact match |
| `SecRightsDefault` | `SecRightsDefault` | Exact match |
| `SumPayment` | `SumPayment` | Exact match |
| `SyncRecords` | `SyncRecords` | Exact match |
| `TimeClock` | `TimeClock` | Exact match |


---

## Invalid Table References

The following 23 tables do NOT exist in the database:

| Referenced Table | Similar Tables Found | Recommendation |
|------------------|---------------------|----------------|
| `BizClose` | None found | Verify table name |
| `BizDate` | None found | Verify table name |
| `CCSettle` | None found | Verify table name |
| `CashDrawerClose` | `CashDrawer` | Use `CashDrawer` |
| `CompChecks` | None found | Verify table name |
| `CompChkItms` | None found | Verify table name |
| `CompChkReason` | None found | Verify table name |
| `DeliveryZone` | None found | Verify table name |
| `ErrorLog` | `LoyaltyErrorLog` | Use `LoyaltyErrorLog` |
| `KDItem` | None found | Verify table name |
| `KDStation` | None found | Verify table name |
| `MenuItmMdGrps` | None found | Verify table name |
| `MenuItmPrices` | None found | Verify table name |
| `PrintQueue` | None found | Verify table name |
| `PrinterCfg` | `Printer` | Use `Printer` |
| `StoreCfg` | None found | Verify table name |
| `SumCashier` | None found | Verify table name |
| `SumDaily` | None found | Verify table name |
| `SumMenuItm` | None found | Verify table name |
| `SumServer` | None found | Verify table name |
| `SyncQueue` | None found | Verify table name |
| `SyncStatus` | None found | Verify table name |
| `SystemCfg` | None found | Verify table name |


---

## Tables in Database Not in Reference Guide

These tables exist but are not documented in the SQL reference:

- `APIUsers`
- `AboveStore_Tables_List`
- `AcctingCats`, `AcctingDefs`, `AcctingDefsFilter`
- `Apps`
- `BackupSched`
- `Breaks`
- **Bus***: `Business`, `BusinessDate`, `BusinessHours`, `BusinessServiceHours`
- `CCLanes`
- `CCMerchants`
- `CCTransLog`
- **Cal***: `CallerId`, `CallerIdCfg`, `CallerIdFilter`, `CallerIdLog`
- **Cas***: `CashDrawerAudit`, `CashDrawerCashDetail`, `CashDrawerDrop`, `CashDrawerDropDetail`, `CashDrawerUser` ... (+2 more)
- **Com***: `Computer`, `ComputerCCOpts`, `ComputerCustDisp`, `ComputerExcldPmtTypes`, `ComputerOrdTypeXRef` ... (+2 more)
- `Contest`
- **Cus***: `CustAcct`, `CustAcctAudit`, `CustAcctItem`, `CustAcctLink`, `CustAcctOpts` ... (+14 more)
- **Del***: `DeletedRecords`, `DeliveryOpts`, `DeliveryOptsTP`, `DeliveryOrderTP`, `DeliveryQueue` ... (+2 more)
- **Dep***: `Deposit`, `DepositBagNumbers`, `DepositBanks`, `DepositCashDrawer`, `DepositReason`
- `DispatchLogTP`
- `DriveThruTimes`
- **Emp***: `EmployeeFP`, `EmployeeImage`, `EmployeeLaborRate`, `EmployeeLaborType`, `EmployeeMail` ... (+2 more)
- `EventLog`, `EventQuestions`, `EventQuestionValues`
- `EvtLog`
- `GiftCardPending`, `GiftCardRange`
- `Grids`
- `HUBApiCredentials`
- `IDScan`
- `Import`
- **Inv***: `InventCat`, `InventCnt`, `InventCount`, `InventGrp`, `InventItem` ... (+12 more)
- `KDItmNote`
- **KDO***: `KDOrdItem`, `KDOrdItemMod`, `KDOrdItemNoMod`, `KDOrdItemPrfMbr`
- **Ktc***: `KtchDisp`, `KtchDispOTXRef`, `KtchDispProdItmXRef`, `KtchDispPrtXRef`, `KtchDispQueue`
- `LaborType`
- `LanguageDef`, `LanguageTrans`
- `LoyaltyErrorLog`, `LoyaltyOpts`
- **Men***: `Menu86`, `MenuCategory`, `MenuCountdown`, `MenuCpnExcldOrdType`, `MenuCpnItm` ... (+53 more)
- **Ord***: `OrdAdj`, `OrdBtnLayout`, `OrdCpnItm`, `OrdCust`, `OrdData` ... (+16 more)
- `POSCommands`
- `Paste Errors`
- `PaymentType`, `PaymentTypeCat`
- **Pri***: `PrinterCustOrdTypeXref`, `PrinterGroup`, `PrinterGroupXRef`, `PrinterInterface`, `PrinterInterfacePorts` ... (+9 more)
- **RU_***: `RU_FileAccessLog`, `RU_FileJobs`, `RU_Files`, `RU_JobCategories`, `RU_JobHistory` ... (+5 more)
- `RefreshSchedule`, `RefundOrder`, `RefundPayment`
- `RemoteLoc`
- **Rep***: `ReportCat`, `ReportEmail`, `ReportOpts`, `ReportPackage`, `ReportPkgEmail`
- `RevCenter`, `RevPayment`
- `SalesAnalysisQry`
- `ScanCodes`
- `SecChgAudit`, `SecIndGrp`, `SecIndRights`
- `Shifts`
- `StreetGrid`, `Streets`, `StreetZone`
- **Sum***: `SumAccounting`, `SumAdj`, `SumAdjDetail`, `SumCreditCards`, `SumInventory` ... (+5 more)
- `SurchargeOrderType`, `SurchargePaymentType`, `Surcharges`
- **Sys***: `SysConfig`, `SysConfigPMS`, `SysGCOpts`, `SysOrdOpts`, `SysServices` ... (+1 more)
- **TM_***: `TM_Categories`, `TM_Object_Types`, `TM_ObjectItems`, `TM_Objects`, `TM_Rooms` ... (+6 more)
- `TableMgmtRoom`
- `TblMgmtEmplXRef`
- `TimeClockAudit`, `TimeclockEventQuestions`, `TimeclockEventResponse`
- `UISvcConfig`, `UISvcGeocodes`
- `XO_SvcCon`, `XO_SvcLog`, `XO_SvcTypes`
- `ZipCodes`
- `ZoneGeocodes`, `Zones`
- `dtproperties`
- `ztemp`
