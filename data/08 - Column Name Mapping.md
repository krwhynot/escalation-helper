# Column Name Mapping - VERIFIED
## Document 08 - Actual Database Column Names

**Generated:** 2025-12-10 15:10:19
**Database:** REVENTION
**Server:** 172.31.240.1\Revention

---

## Important Column Naming Discoveries

Based on actual database queries, here are the correct column names to use:


### Ord (355,648 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `OrdKey` | int | NO |
| 2 | `BizDate` | datetime | NO |
| 3 | `OrdNumber` | int | NO |
| 4 | `Menu` | nvarchar(25) | YES |
| 5 | `OrdType` | nvarchar(15) | YES |
| 6 | `OrdStation` | nvarchar(15) | YES |
| 7 | `OrdStartTime` | datetime | YES |
| 8 | `OrdStartEmplKey` | int | YES |
| 9 | `OrdUpdateTime` | datetime | YES |
| 10 | `OrdUpdateEmplKey` | int | YES |
| 11 | `OrigTotal` | money | YES |
| 12 | `AdjAmt` | money | YES |
| 13 | `CpnAmt` | money | YES |
| 14 | `Subtotal` | money | YES |
| 15 | `Tax` | money | YES |
| 16 | `DlvyFee` | money | NO |
| 17 | `DlvyFeeTxbl` | bit | NO |
| 18 | `ActiveTotal` | money | YES |
| 19 | `Grat` | money | NO |
| 20 | `Tip` | money | YES |
| 21 | `AmountPaid` | money | YES |
| 22 | `IsPaid` | bit | NO |
| 23 | `PagerNum` | int | YES |
| 24 | `TableNum` | int | YES |
| 25 | `TaxExempt` | bit | NO |
| 26 | `TaxNum` | nvarchar(25) | YES |
| 27 | `DisplayOrdPayment` | nvarchar(20) | YES |
| 28 | `DeferEntryTime` | datetime | YES |
| 29 | `Computer` | nvarchar(50) | YES |
| 30 | `GuestCount` | int | NO |
| 31 | `SvrKey` | int | NO |
| 32 | `SplitCnt` | int | NO |
| 33 | `GratPct` | int | NO |
| 34 | `HS` | bit | NO |
| 35 | `CpnsRejected` | nvarchar(30) | YES |
| 36 | `PreOrder` | nvarchar(15) | YES |
| 37 | `CkAppr` | int | NO |
| 38 | `CkApprMsg` | nvarchar(30) | YES |
| 39 | `CkApprMgr` | int | NO |
| 40 | `IsStagePrinted` | bit | NO |
| 41 | `IsCustPrinted` | bit | NO |
| 42 | `MergeToOrdNum` | int | NO |
| 43 | `OrdEstTime` | datetime | YES |
| 44 | `IsOnline` | bit | NO |
| 45 | `GratAsCatering` | bit | NO |
| 46 | `SplitPmt` | money | NO |
| 47 | `SplitPmtCnt` | int | NO |
| 48 | `OrdTypePriceIdx` | int | NO |
| 49 | `ManualDlvyFee` | bit | NO |
| 50 | `LoyaltySent` | money | NO |
| 51 | `LabelTotal` | money | NO |
| 52 | `Origin` | int | NO |
| 53 | `AboveStoreID` | int | NO |
| 54 | `IsWaste` | bit | NO |
| 55 | `NameLast4` | nvarchar(4) | NO |
| 56 | `OLRefNum` | nvarchar(50) | NO |
| 57 | `RsvdOrdNum` | int | NO |
| 58 | `GratBase` | money | NO |
| 59 | `AutoGratFlag` | int | NO |
| 60 | `RewardsNoAsk` | money | NO |
| 61 | `TableName` | varchar(10) | NO |
| 62 | `LoyaltyNum` | nvarchar(30) | NO |
| 63 | `LoyaltyAuthCode` | nvarchar(10) | NO |
| 64 | `KDSReadyTime` | datetime | YES |
| 65 | `KDSLastIdx` | int | NO |
| 66 | `YTDNumber` | int | NO |
| 67 | `RsvdYTDNum` | int | NO |
| 68 | `HasKDSPriority` | bit | NO |
| 69 | `PunchhSyncTime` | datetime | YES |
| 70 | `PunchhCode` | varchar(50) | YES |
| 71 | `PunchhId` | varchar(20) | NO |
| 72 | `EntSync` | datetime | YES |
| 73 | `SyncStatus` | int | NO |
| 74 | `EntID` | int | NO |
| 75 | `Tag` | tinyint | NO |
| 76 | `Dist` | decimal | NO |
| 77 | `Age` | tinyint | NO |
| 78 | `XOOrdStatus` | nvarchar(30) | NO |
| 79 | `CSArrivalTime` | datetime | YES |
| 80 | `KDSBumpTime` | datetime | YES |
| 81 | `Status` | tinyint | NO |
| 82 | `ThirdPartyID` | varchar(50) | YES |

### OrdItem (954,111 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `OrdItemKey` | int | NO |
| 2 | `BizDate` | datetime | NO |
| 3 | `OrdNumber` | int | NO |
| 4 | `OrdItemNumber` | int | NO |
| 5 | `ItemName` | nvarchar(25) | YES |
| 6 | `KtchName` | nvarchar(50) | YES |
| 7 | `RcptName` | nvarchar(25) | YES |
| 8 | `GroupName` | nvarchar(25) | YES |
| 9 | `KtchPrtCat` | nvarchar(25) | YES |
| 10 | `TaxType` | nvarchar(25) | YES |
| 11 | `RptGrp` | nvarchar(25) | YES |
| 12 | `OriginalPrice` | money | YES |
| 13 | `AdjAmt` | money | YES |
| 14 | `CpnAmt` | money | YES |
| 15 | `ActivePrice` | money | YES |
| 16 | `Qty` | int | YES |
| 17 | `ModValue` | money | NO |
| 18 | `SizeName` | nvarchar(15) | YES |
| 19 | `SizeRcptName` | nvarchar(15) | YES |
| 20 | `StyleName` | nvarchar(15) | YES |
| 21 | `StyleRcptName` | nvarchar(15) | YES |
| 22 | `IsPrinted` | bit | NO |
| 23 | `IsVoid` | bit | NO |
| 24 | `HasReqMods` | bit | NO |
| 25 | `IsHalf` | bit | NO |
| 26 | `Half2Name` | nvarchar(25) | YES |
| 27 | `SecondItemApplies` | bit | NO |
| 28 | `SecondItemPrice` | money | NO |
| 29 | `ModSecondValue` | money | NO |
| 30 | `BumpTime` | datetime | YES |
| 31 | `IsVoidPrinted` | bit | NO |
| 32 | `Seq` | int | NO |
| 33 | `GrpSeq` | int | NO |
| 34 | `SzSeq` | int | NO |
| 35 | `DisplayPrice` | money | NO |
| 36 | `IsBumped` | bit | NO |
| 37 | `DlvReminder` | bit | NO |
| 38 | `SplitNumber` | int | NO |
| 39 | `UseRollup` | bit | NO |
| 40 | `H2OrigPrice` | money | NO |
| 41 | `H2Orig2ndPrice` | money | NO |
| 42 | `H2ModValue` | money | NO |
| 43 | `H2Mod2ndValue` | money | NO |
| 44 | `SizeKtchName` | nvarchar(10) | YES |
| 45 | `StyleKtchName` | nvarchar(15) | YES |
| 46 | `UseStdMods` | bit | NO |
| 47 | `PSModCnt` | int | NO |
| 48 | `DisplayPS` | bit | NO |
| 49 | `NoDisc` | bit | NO |
| 50 | `Replaces` | int | NO |
| 51 | `IsReplaced` | bit | NO |
| 52 | `TimePriceKey` | int | NO |
| 53 | `AutoQty` | bit | NO |
| 54 | `ItemBumpTime` | datetime | YES |
| 55 | `IsItemBumped` | bit | NO |
| 56 | `MergeFromOrdNum` | int | NO |
| 57 | `PtsEarn` | int | NO |
| 58 | `PtsPrice` | int | NO |
| 59 | `Weight` | decimal | NO |
| 60 | `SeatNum` | int | NO |
| 61 | `PairPrice` | money | NO |
| 62 | `KtchOnly` | bit | NO |
| 63 | `VoidPrepared` | bit | NO |
| 64 | `OrdItemTime` | datetime | YES |
| 65 | `IsLblPrinted` | bit | NO |
| 66 | `ThirdItemPrice` | money | NO |
| 67 | `H2Orig3rdPrice` | money | NO |
| 68 | `BogoID` | int | NO |
| 69 | `EmployeeKey` | int | NO |
| 70 | `RedPrint` | bit | NO |
| 71 | `IsStageKtchPrinted` | bit | NO |
| 72 | `ComputerName` | nvarchar(25) | NO |
| 73 | `HasUniquePref` | bit | NO |
| 74 | `LastBumpTime` | datetime | YES |
| 75 | `AddlBumpTime` | datetime | YES |
| 76 | `IsAddlBumped` | bit | NO |
| 77 | `KDSDisplayTime` | datetime | YES |
| 78 | `KDSProdItmName` | varchar(25) | NO |
| 79 | `KDSProdItmCnt` | int | NO |
| 80 | `KDSPrepTimeSecs` | int | NO |
| 81 | `KDSIdx` | int | NO |
| 82 | `KDSPriority` | bit | NO |
| 83 | `ItemMultiBump` | int | NO |
| 84 | `ISpltFactor` | int | NO |
| 85 | `ISpltIdx` | int | NO |
| 86 | `ISpltKey` | int | NO |
| 87 | `ISpltWhlPrc` | money | NO |
| 88 | `ISpltWhlModVal` | money | NO |
| 89 | `EntSync` | datetime | YES |
| 90 | `SyncStatus` | int | NO |
| 91 | `EntID` | int | NO |
| 92 | `DurationRate` | money | NO |
| 93 | `DurationMins` | int | NO |
| 94 | `Status` | int | NO |
| 95 | `HoldTime` | datetime | YES |
| 96 | `FireTime` | datetime | YES |
| 97 | `ISpltWhlH2Prc` | money | NO |
| 98 | `ISpltWhlH2ModVal` | money | NO |
| 99 | `StylePrice` | money | NO |
| 100 | `ItemType` | tinyint | NO |
| 101 | `PriceType` | tinyint | NO |
| 102 | `MinAge` | tinyint | NO |

### OrdItemMod (796,558 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `OrdItemModKey` | int | NO |
| 2 | `BizDate` | datetime | YES |
| 3 | `OrdNumber` | int | YES |
| 4 | `OrdItemNumber` | int | YES |
| 5 | `ModName` | nvarchar(25) | YES |
| 6 | `KtchName` | nvarchar(25) | YES |
| 7 | `RcptName` | nvarchar(25) | YES |
| 8 | `GroupName` | nvarchar(25) | YES |
| 9 | `TaxType` | nvarchar(25) | YES |
| 10 | `RptGrp` | nvarchar(25) | YES |
| 11 | `HalfStatus` | tinyint | NO |
| 12 | `OriginalPrice` | money | YES |
| 13 | `AdjAmt` | money | YES |
| 14 | `CpnAmt` | money | YES |
| 15 | `ActivePrice` | money | YES |
| 16 | `IsVoid` | bit | NO |
| 17 | `ModCatKey` | int | NO |
| 18 | `PriceApplies` | bit | NO |
| 19 | `Seq` | int | NO |
| 20 | `Qty` | int | NO |
| 21 | `IsPreSel` | bit | NO |
| 22 | `MixedPreSel` | bit | NO |
| 23 | `SecondItemPrice` | money | NO |
| 24 | `DisplayPrice` | money | NO |
| 25 | `DlvReminder` | bit | NO |
| 26 | `HalfPrice` | money | NO |
| 27 | `NoStdMod` | bit | NO |
| 28 | `PrfMbrNumber` | int | NO |
| 29 | `KtchOnly` | bit | NO |
| 30 | `IsLite` | bit | NO |
| 31 | `IsSide` | bit | NO |
| 32 | `ISpltFactor` | int | NO |
| 33 | `ISpltIdx` | int | NO |
| 34 | `ISpltKey` | int | NO |
| 35 | `ISpltWhlPrc` | money | NO |
| 36 | `ISpltHlfPrc` | money | NO |
| 37 | `EntSync` | datetime | YES |
| 38 | `SyncStatus` | int | NO |
| 39 | `EntID` | int | NO |
| 40 | `NoKtchDisp` | bit | NO |

### OrdPayment (322,830 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `OrdPaymentKey` | int | NO |
| 2 | `BizDate` | datetime | YES |
| 3 | `OrdNumber` | int | YES |
| 4 | `PaymentTime` | datetime | YES |
| 5 | `CashDrawerKey` | int | YES |
| 6 | `OrigCashDrawerKey` | int | NO |
| 7 | `PmtToDriver` | bit | NO |
| 8 | `PaymentType` | nvarchar(15) | YES |
| 9 | `PaymentTypeCategory` | nvarchar(15) | YES |
| 10 | `CardType` | nvarchar(15) | YES |
| 11 | `Amount` | money | YES |
| 12 | `PreAuthTip` | money | NO |
| 13 | `Tip` | money | YES |
| 14 | `Reconciled` | bit | NO |
| 15 | `AddedByDriver` | bit | NO |
| 16 | `AuthCode` | nvarchar(15) | YES |
| 17 | `TransId` | int | NO |
| 18 | `Last4Digits` | nvarchar(4) | YES |
| 19 | `PayerName` | nvarchar(26) | YES |
| 20 | `VReconciled` | bit | NO |
| 21 | `ToDwr` | int | NO |
| 22 | `PaymentBizDate` | datetime | YES |
| 23 | `SplitNumber` | int | NO |
| 24 | `EmployeeKey` | int | NO |
| 25 | `GiftSeqNum` | nvarchar(10) | YES |
| 26 | `CustAcctNum` | int | NO |
| 27 | `ApprovalKey` | int | NO |
| 28 | `ExcessTender` | money | NO |
| 29 | `Tendered` | money | NO |
| 30 | `TipSvrDwrKey` | int | NO |
| 31 | `DeferCC` | bit | NO |
| 32 | `LUuuid` | nvarchar(50) | NO |
| 33 | `Signature` | varchar | YES |
| 34 | `EyeDeliverTip` | money | NO |
| 35 | `EntSync` | datetime | YES |
| 36 | `SyncStatus` | int | NO |
| 37 | `EntID` | int | NO |
| 38 | `PMSInquiry` | varchar(25) | NO |
| 39 | `PMSInquiryType` | tinyint | NO |
| 40 | `PMSRoomNum` | varchar(10) | NO |
| 41 | `PMSProfileID` | varchar(15) | NO |
| 42 | `PMSGuestName` | varchar(50) | NO |
| 43 | `Grat` | money | YES |

### OrdCpn (63,205 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `OrdCpnKey` | int | NO |
| 2 | `BizDate` | smalldatetime | NO |
| 3 | `OrdNumber` | int | NO |
| 4 | `OrdItemNumber` | int | NO |
| 5 | `CpnName` | nvarchar(30) | NO |
| 6 | `CpnRcptName` | nvarchar(50) | YES |
| 7 | `CpnScope` | tinyint | NO |
| 8 | `CpnType` | tinyint | NO |
| 9 | `CpnValue` | money | NO |
| 10 | `CpnPct` | decimal | NO |
| 11 | `ActiveValue` | money | NO |
| 12 | `MinPrice` | money | NO |
| 13 | `AdjItemPrice` | bit | NO |
| 14 | `TaxType` | nvarchar(25) | YES |
| 15 | `RptGrp` | nvarchar(25) | YES |
| 16 | `IsChanged` | bit | NO |
| 17 | `ApprovalKey` | int | NO |
| 18 | `ApprovalEmployee` | nvarchar(50) | YES |
| 19 | `FreeDlvy` | bit | NO |
| 20 | `TimeApplied` | datetime | YES |
| 21 | `SplitNum` | int | NO |
| 22 | `MaxValue` | money | NO |
| 23 | `ValCode` | nvarchar(15) | YES |
| 24 | `No2ndItm` | bit | NO |
| 25 | `BeatClock` | bit | NO |
| 26 | `LeaveTax` | bit | NO |
| 27 | `OpenValue` | bit | NO |
| 28 | `IsExclusive` | bit | NO |
| 29 | `DlvyFeeIfZero` | bit | NO |
| 30 | `NoModDisc` | bit | NO |
| 31 | `BogoID` | int | NO |
| 32 | `PickAnyCnt` | int | NO |
| 33 | `RequiredItem` | bit | NO |
| 34 | `RequireAnyCnt` | int | NO |
| 35 | `SingleUseKey` | int | NO |
| 36 | `QualAmtNoDisc` | bit | NO |
| 37 | `CpnModValue` | money | NO |
| 38 | `PunchhType` | int | NO |
| 39 | `PunchhId` | varchar(20) | NO |
| 40 | `MultiQualTtl` | money | NO |
| 41 | `EntSync` | datetime | YES |
| 42 | `SyncStatus` | int | NO |
| 43 | `EntID` | int | NO |
| 44 | `NoStyleDisc` | bit | NO |
| 45 | `NoPrefDisc` | bit | NO |
| 46 | `LtyDiscountType` | tinyint | NO |
| 47 | `LtyRedemptionID` | varchar(25) | YES |
| 48 | `LtyRedemptionCode` | varchar(25) | YES |
| 49 | `MaxModValue` | money | NO |

### OrdTax (345,568 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `OrdTaxKey` | int | NO |
| 2 | `BizDate` | smalldatetime | NO |
| 3 | `OrdNumber` | int | NO |
| 4 | `TaxName` | nvarchar(25) | NO |
| 5 | `Amount` | money | NO |
| 6 | `TaxableAmt` | money | NO |
| 7 | `TaxRate` | numeric | NO |
| 8 | `TaxAmt` | money | NO |
| 9 | `TaxIncluded` | bit | NO |
| 10 | `ExemptApplies` | bit | NO |
| 11 | `TaxExempt` | bit | NO |
| 12 | `TaxNum` | nvarchar(25) | YES |
| 13 | `RoundUp` | bit | NO |
| 14 | `TaxFullPrice` | bit | NO |
| 15 | `IsAlcohol` | bit | NO |
| 16 | `EntSync` | datetime | YES |
| 17 | `SyncStatus` | int | NO |
| 18 | `EntID` | int | NO |

### Employee (87 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `EmployeeKey` | int | NO |
| 2 | `EmployeeID` | nvarchar(20) | YES |
| 3 | `FirstName` | nvarchar(50) | YES |
| 4 | `LastName` | nvarchar(50) | YES |
| 5 | `NickName` | nvarchar(25) | YES |
| 6 | `SSNum` | nvarchar(50) | YES |
| 7 | `Address1` | nvarchar(50) | YES |
| 8 | `Address2` | nvarchar(50) | YES |
| 9 | `City` | nvarchar(50) | YES |
| 10 | `State` | nvarchar(50) | YES |
| 11 | `Zip` | nvarchar(50) | YES |
| 12 | `HomePhone` | nvarchar(50) | YES |
| 13 | `CellPhone` | nvarchar(50) | YES |
| 14 | `Pager` | nvarchar(50) | YES |
| 15 | `Email` | nvarchar(50) | YES |
| 16 | `IsActive` | bit | NO |
| 17 | `HireDate` | datetime | YES |
| 18 | `TermDate` | datetime | YES |
| 19 | `ReqTimeClock` | bit | NO |
| 20 | `DrvLicExpDate` | datetime | YES |
| 21 | `DrvLicNum` | nvarchar(30) | YES |
| 22 | `DrvInsExpDate` | datetime | YES |
| 23 | `DrvInsCo` | nvarchar(30) | YES |
| 24 | `DrvInsPh` | nvarchar(20) | YES |
| 25 | `DrvInsNum` | nvarchar(30) | YES |
| 26 | `DrvRegExpDate` | datetime | YES |
| 27 | `AddComp` | money | NO |
| 28 | `BirthDate` | datetime | YES |
| 29 | `MStatus` | nvarchar(1) | YES |
| 30 | `FedExempt` | int | NO |
| 31 | `StExempt` | int | NO |
| 32 | `EmpNum` | int | NO |
| 33 | `LastChange` | datetime | YES |
| 34 | `ChangedBy` | nvarchar(50) | YES |
| 35 | `SecLevel` | int | NO |
| 36 | `SU` | int | NO |
| 37 | `HS` | bit | NO |
| 38 | `NoStrtAmt` | bit | NO |
| 39 | `Lang` | int | NO |
| 40 | `CellPhoneProvider` | nvarchar(25) | NO |
| 41 | `CellDomain` | nvarchar(25) | NO |
| 42 | `AddCompPct` | decimal | NO |
| 43 | `DailyOT10` | bit | NO |
| 44 | `OutOfStoreRate` | money | NO |
| 45 | `PWChDate` | datetime | YES |
| 46 | `PWNoExp` | bit | NO |
| 47 | `HSSync` | datetime | YES |
| 48 | `EntSync` | datetime | YES |
| 49 | `SyncStatus` | int | NO |
| 50 | `EntID` | int | NO |
| 51 | `EmployeeContractor` | tinyint | NO |
| 52 | `NoCompensation` | bit | NO |

### TimeClock (25,487 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `TimeClockKey` | int | NO |
| 2 | `BusinessDate` | datetime | YES |
| 3 | `EmployeeKey` | int | YES |
| 4 | `EmployeeFName` | nvarchar(50) | YES |
| 5 | `EmployeeLName` | nvarchar(50) | YES |
| 6 | `RecordType` | smallint | YES |
| 7 | `InTime` | datetime | YES |
| 8 | `OutTime` | datetime | YES |
| 9 | `LaborType` | nvarchar(50) | YES |
| 10 | `Rate` | money | YES |
| 11 | `AdditionalComp` | money | NO |
| 12 | `LastUpdateBy` | nvarchar(50) | YES |
| 13 | `LastUpdateTime` | datetime | YES |
| 14 | `Tips` | money | NO |
| 15 | `BegMileage` | int | NO |
| 16 | `EndMileage` | int | NO |
| 17 | `ShiftPay` | bit | NO |
| 18 | `BreakType` | varchar(25) | NO |
| 19 | `MinTime` | int | NO |
| 20 | `BreakAppr` | int | NO |
| 21 | `AutoOut` | int | NO |
| 22 | `EntSync` | datetime | YES |
| 23 | `SyncStatus` | int | NO |
| 24 | `EntID` | int | NO |
| 25 | `EstMiles` | decimal | NO |
| 26 | `AddMiles` | decimal | NO |

### SecGrp (7 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `SecGroupKey` | int | NO |
| 2 | `Name` | nvarchar(50) | YES |
| 3 | `CreatedBy` | nvarchar(50) | YES |
| 4 | `CreatedDate` | datetime | YES |
| 5 | `EntSync` | datetime | YES |
| 6 | `SyncStatus` | int | NO |
| 7 | `EntID` | int | NO |
| 8 | `SecLevel` | int | NO |

### SecGrpRights (1,428 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `SecGroupRightsKey` | int | NO |
| 2 | `SecGroupKey` | int | YES |
| 3 | `RightKey` | int | YES |
| 4 | `Setting` | smallint | YES |
| 5 | `EntSync` | datetime | YES |
| 6 | `SyncStatus` | int | NO |
| 7 | `EntID` | int | NO |

### CashDrawer (12,622 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `CashDrawerKey` | int | NO |
| 2 | `CashDrawerName` | nvarchar(25) | YES |
| 3 | `BusinessDate` | datetime | YES |
| 4 | `Computer` | nvarchar(30) | YES |
| 5 | `StartingAmt` | money | YES |
| 6 | `Shared` | bit | NO |
| 7 | `CDType` | int | NO |
| 8 | `DelDrvKey` | int | NO |
| 9 | `OpenedBy` | nvarchar(50) | YES |
| 10 | `OpenedByKey` | int | YES |
| 11 | `OpenTime` | datetime | YES |
| 12 | `ClosedBy` | nvarchar(30) | YES |
| 13 | `CloseTime` | datetime | YES |
| 14 | `CashRequired` | money | YES |
| 15 | `CashActual` | money | YES |
| 16 | `ChecksRequired` | money | YES |
| 17 | `ChecksActual` | money | YES |
| 18 | `CreditRequired` | money | YES |
| 19 | `CreditActual` | money | YES |
| 20 | `GiftCertRequired` | money | YES |
| 21 | `GiftCertActual` | money | YES |
| 22 | `AcctRequired` | money | YES |
| 23 | `AcctActual` | money | YES |
| 24 | `TotalSales` | money | YES |
| 25 | `OverShort` | money | YES |
| 26 | `ReconciledBy` | nvarchar(50) | YES |
| 27 | `ReconcileTime` | datetime | YES |
| 28 | `DelComp` | money | NO |
| 29 | `CashoutToDwr` | int | NO |
| 30 | `CCTips` | money | NO |
| 31 | `RegTips` | money | NO |
| 32 | `Grat` | money | NO |
| 33 | `CCTipFee` | money | NO |
| 34 | `OnlineCCPmts` | bit | NO |
| 35 | `BegMileage` | int | NO |
| 36 | `EndMileage` | int | NO |
| 37 | `DwrOpen` | int | NO |
| 38 | `MaxCash` | money | NO |
| 39 | `OpenRestrict` | bit | NO |
| 40 | `TCKey` | int | NO |
| 41 | `OtherPmts` | money | NO |
| 42 | `TippedEmp` | bit | NO |
| 43 | `NoSaleCnt` | int | NO |
| 44 | `TipOut` | money | NO |
| 45 | `GCCnt` | int | NO |
| 46 | `GCAmt` | money | NO |
| 47 | `MaxErrCnt` | int | NO |
| 48 | `CurErrCnt` | int | NO |
| 49 | `DrvCCTipsDrop` | money | NO |
| 50 | `CCTipsFromOther` | money | NO |
| 51 | `Tax` | money | NO |
| 52 | `EntSync` | datetime | YES |
| 53 | `SyncStatus` | int | NO |
| 54 | `EntID` | int | NO |

### CashDrawerCfg (2 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `CashDrawerCfgKey` | int | NO |
| 2 | `DrawerName` | nvarchar(50) | YES |
| 3 | `Computer` | nvarchar(50) | YES |
| 4 | `OPOS` | bit | NO |
| 5 | `Model` | nvarchar(50) | YES |
| 6 | `Printer` | nvarchar(50) | YES |
| 7 | `Shared` | bit | NO |
| 8 | `StartingAmt` | float | YES |
| 9 | `IsPrimary` | bit | NO |
| 10 | `CreatedDate` | datetime | YES |
| 11 | `CreatedBy` | nvarchar(50) | YES |
| 12 | `Active` | bit | NO |
| 13 | `upsize_ts` | timestamp | YES |
| 14 | `Serial` | bit | NO |
| 15 | `Port` | nvarchar(5) | NO |
| 16 | `OnlineCCPmts` | bit | NO |
| 17 | `DwrOpen` | int | NO |
| 18 | `MaxCash` | money | NO |
| 19 | `OpenRestrict` | bit | NO |
| 20 | `USB` | bit | NO |
| 21 | `Rev2310` | bit | NO |
| 22 | `TippedEmp` | bit | NO |
| 23 | `Rev3310` | bit | NO |
| 24 | `MaxErrCnt` | int | NO |
| 25 | `EntSync` | datetime | YES |
| 26 | `SyncStatus` | int | NO |
| 27 | `EntID` | int | NO |
| 28 | `Rev4310` | bit | NO |
| 29 | `PT6980` | bit | NO |
| 30 | `VerifyStartAmt` | bit | NO |
| 31 | `CDPaidIn` | bit | NO |
| 32 | `AutoReconcile` | bit | NO |
| 33 | `Rev5685` | bit | NO |
| 34 | `Rev6110` | bit | NO |

### CCTrans (164,114 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `CCTransKey` | int | NO |
| 2 | `BizDate` | datetime | NO |
| 3 | `AppType` | int | NO |
| 4 | `StationId` | int | NO |
| 5 | `Signature` | varchar | YES |
| 6 | `EntID` | int | NO |
| 7 | `EntSync` | datetime | YES |
| 8 | `SyncStatus` | int | NO |
| 9 | `InitTime` | datetime | YES |

### Customer (34,020 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `CustomerKey` | int | NO |
| 2 | `AddrKey` | int | YES |
| 3 | `LastName` | nvarchar(25) | YES |
| 4 | `FirstName` | nvarchar(25) | YES |
| 5 | `CustID` | nvarchar(25) | YES |
| 6 | `SpNote` | nvarchar(100) | NO |
| 7 | `DelNote` | nvarchar(100) | NO |
| 8 | `FirstOrdDate` | datetime | YES |
| 9 | `LastOrdDate` | datetime | YES |
| 10 | `LastOrdNum` | int | NO |
| 11 | `OrdCnt` | int | NO |
| 12 | `OrdAmt` | money | NO |
| 13 | `TaxExempt` | bit | NO |
| 14 | `TaxNum` | nvarchar(25) | YES |
| 15 | `AcceptChecks` | bit | NO |
| 16 | `LastChanged` | smalldatetime | YES |
| 17 | `Created` | smalldatetime | YES |
| 18 | `BadChecksCust` | bit | NO |
| 19 | `PctDiscount` | decimal | NO |
| 20 | `Points` | int | NO |
| 21 | `Email` | nvarchar(80) | NO |
| 22 | `PctDiscAppr` | int | NO |
| 23 | `FirstOLDate` | datetime | YES |
| 24 | `LastOLDate` | datetime | YES |
| 25 | `OLCnt` | int | NO |
| 26 | `OLAmt` | money | NO |
| 27 | `OptOut` | bit | NO |
| 28 | `LoyaltyPoints` | int | NO |
| 29 | `LoyaltyCredit` | money | NO |
| 30 | `AVSZip` | nvarchar(10) | NO |
| 31 | `AVSStNum` | nvarchar(8) | NO |
| 32 | `AVSManual` | bit | NO |
| 33 | `CpnUsage` | nvarchar(120) | NO |
| 34 | `RewardsMember` | bit | NO |
| 35 | `LoyaltyNum` | nvarchar(30) | NO |
| 36 | `EntSync` | datetime | YES |
| 37 | `SyncStatus` | int | NO |
| 38 | `EntID` | int | NO |
| 39 | `LtyChkTime` | datetime | YES |

### CustomerPhone (35,649 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `CustomerPhoneKey` | int | NO |
| 2 | `CustomerKey` | int | NO |
| 3 | `PhoneNum` | nvarchar(20) | YES |
| 4 | `Description` | nvarchar(50) | YES |
| 5 | `LastUpdated` | smalldatetime | YES |
| 6 | `Created` | smalldatetime | YES |
| 7 | `EntSync` | datetime | YES |
| 8 | `SyncStatus` | int | NO |
| 9 | `EntID` | int | NO |

### CustomerAddr (11,229 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `AddrKey` | int | NO |
| 2 | `StNumber` | nvarchar(15) | YES |
| 3 | `Street` | nvarchar(50) | YES |
| 4 | `Apt` | nvarchar(25) | YES |
| 5 | `City` | nvarchar(25) | YES |
| 6 | `State` | nvarchar(20) | YES |
| 7 | `Zip` | nvarchar(20) | YES |
| 8 | `AddrType` | nvarchar(10) | YES |
| 9 | `CompanyName` | nvarchar(50) | YES |
| 10 | `EntryCode` | nvarchar(20) | YES |
| 11 | `AddrZone` | nvarchar(25) | YES |
| 12 | `CrossStreet` | nvarchar(40) | YES |
| 13 | `AddrGrid` | nvarchar(10) | YES |
| 14 | `BadChecksAddr` | bit | NO |
| 15 | `DoNotDeliver` | bit | NO |
| 16 | `EntSync` | datetime | YES |
| 17 | `SyncStatus` | int | NO |
| 18 | `EntID` | int | NO |

### MenuItms (97 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `ItemName` | nvarchar(25) | NO |
| 2 | `ButtonName` | nvarchar(25) | YES |
| 3 | `ReceiptName` | nvarchar(25) | YES |
| 4 | `KitchenName` | nvarchar(25) | YES |
| 5 | `MenuCategory` | nvarchar(10) | YES |
| 6 | `OnlineName` | nvarchar(50) | NO |
| 7 | `EntSync` | datetime | YES |
| 8 | `SyncStatus` | int | NO |
| 9 | `EntID` | int | NO |
| 10 | `MenuItmsKey` | int | NO |

### MenuGrps (10 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `GroupName` | nvarchar(25) | NO |
| 2 | `ButtonName` | nvarchar(25) | YES |
| 3 | `MenuCategory` | nvarchar(10) | YES |
| 4 | `OnlineName` | nvarchar(25) | NO |
| 5 | `EntSync` | datetime | YES |
| 6 | `SyncStatus` | int | NO |
| 7 | `EntID` | int | NO |
| 8 | `MenuGrpsKey` | int | NO |

### MenuMds (84 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `ModName` | nvarchar(25) | NO |
| 2 | `ButtonName` | nvarchar(25) | YES |
| 3 | `ReceiptName` | nvarchar(25) | YES |
| 4 | `KitchenName` | nvarchar(25) | YES |
| 5 | `MenuCategory` | nvarchar(25) | YES |
| 6 | `OnlineName` | nvarchar(50) | NO |
| 7 | `EntSync` | datetime | YES |
| 8 | `SyncStatus` | int | NO |
| 9 | `EntID` | int | NO |
| 10 | `MenuMdsKey` | int | NO |

### Menus (1 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `MenuName` | nvarchar(25) | NO |
| 2 | `StartDate` | datetime | YES |
| 3 | `ExpirationDate` | datetime | YES |
| 4 | `CreatedEmplKey` | int | YES |
| 5 | `CreatedDate` | datetime | YES |
| 6 | `ChangedEmplKey` | int | YES |
| 7 | `ChangedDate` | datetime | YES |
| 8 | `ShowDefaultPref` | bit | NO |
| 9 | `ExtraModMax` | int | YES |
| 10 | `UseModCatColor` | bit | NO |
| 11 | `IsActive` | bit | NO |
| 12 | `IsDefault` | bit | NO |
| 13 | `OpenPriceNote` | bit | NO |
| 14 | `AllowSubmenus` | bit | NO |
| 15 | `AllowUPCItem` | bit | NO |
| 16 | `AllowTimePricing` | bit | NO |
| 17 | `AllowAutoQty` | bit | NO |
| 18 | `AllowPrefMods` | bit | NO |
| 19 | `RequireMultiItem` | bit | NO |
| 20 | `AllowPoints` | bit | NO |
| 21 | `MinPoints` | int | NO |
| 22 | `GrpBtnTextSize` | int | NO |
| 23 | `UsePairsPricing` | bit | NO |
| 24 | `LongItemDesc` | bit | NO |
| 25 | `LgGrpBtns` | bit | NO |
| 26 | `VerifyVoidWaste` | bit | NO |
| 27 | `Lite4Char` | int | NO |
| 28 | `EXfor2X` | int | NO |
| 29 | `SmlGrpBtns` | bit | NO |
| 30 | `ModBtnTxtColor` | int | NO |
| 31 | `MinOpenPrice` | money | NO |
| 32 | `AllowCountdown` | bit | NO |
| 33 | `UseOrigGrpSeq` | bit | NO |
| 34 | `ManualQty` | bit | NO |
| 35 | `Side4Char` | int | NO |
| 36 | `AllowKDSPriority` | bit | NO |
| 37 | `EntSync` | datetime | YES |
| 38 | `SyncStatus` | int | NO |
| 39 | `EntID` | int | NO |
| 40 | `MenusKey` | int | NO |
| 41 | `UploadMenu` | bit | NO |
| 42 | `OpenPriceMgrAppr` | bit | NO |
| 43 | `AllowModSort` | bit | NO |

### DeliveryOrder (87,571 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `DeliveryOrderKey` | int | NO |
| 2 | `BizDate` | smalldatetime | YES |
| 3 | `DriverKey` | int | NO |
| 4 | `OrderNum` | int | NO |
| 5 | `DispatchTime` | datetime | YES |
| 6 | `ReturnTime` | datetime | YES |
| 7 | `Amt` | money | NO |
| 8 | `Tip` | money | NO |
| 9 | `SubTotal` | money | NO |
| 10 | `Sum` | bit | NO |
| 11 | `DeliveryTime` | datetime | YES |
| 12 | `SyncStatus` | int | NO |
| 13 | `PmtType` | nvarchar(20) | NO |
| 14 | `EntSync` | datetime | YES |
| 15 | `EntID` | int | NO |
| 16 | `EstTime` | decimal | NO |
| 17 | `EstDist` | decimal | NO |
| 18 | `TPMessage` | varchar(500) | YES |
| 19 | `TPStatus` | tinyint | NO |

### DeliveryDriver (5,815 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `DeliveryDriverKey` | int | NO |
| 2 | `BizDate` | smalldatetime | YES |
| 3 | `EmpKey` | int | NO |
| 4 | `DriverName` | nvarchar(50) | YES |
| 5 | `DrawerKey` | int | NO |
| 6 | `InTime` | datetime | YES |
| 7 | `OutTime` | datetime | YES |
| 8 | `DelLogonTime` | smalldatetime | YES |
| 9 | `Active` | bit | NO |
| 10 | `OnBreak` | bit | NO |
| 11 | `Lat` | decimal | NO |
| 12 | `Lon` | decimal | NO |
| 13 | `ChgTime` | datetime | YES |
| 14 | `EntSync` | datetime | YES |
| 15 | `SyncStatus` | int | NO |
| 16 | `DriverEmpID` | varchar(50) | NO |
| 17 | `EntID` | int | NO |
| 18 | `TPType` | tinyint | NO |
| 19 | `TPTime` | datetime | YES |
| 20 | `TPID` | int | NO |

### Printer (3 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `PrinterKey` | int | NO |
| 2 | `ComputerName` | nvarchar(50) | YES |
| 3 | `PrinterName` | nvarchar(50) | YES |
| 4 | `Type` | nvarchar(50) | YES |
| 5 | `Interface` | nvarchar(20) | YES |
| 6 | `OPOS` | bit | NO |
| 7 | `WinPrinterName` | nvarchar(50) | YES |
| 8 | `IsKtcn` | bit | NO |
| 9 | `IsActive` | bit | NO |
| 10 | `TimeStamp` | datetime | YES |
| 11 | `PrintPrevious` | bit | NO |
| 12 | `PrintAddl` | bit | NO |
| 13 | `ReprintVoids` | bit | NO |
| 14 | `VoidsOnCust` | bit | NO |
| 15 | `SingleItem` | bit | NO |
| 16 | `IsLbl` | bit | NO |
| 17 | `NoVoids` | bit | NO |
| 18 | `NoLocalKtch` | bit | NO |
| 19 | `RouteTo` | nvarchar(20) | NO |
| 20 | `UseOrdTypes` | bit | NO |
| 21 | `SplitsAsMaster` | bit | NO |
| 22 | `PreSelOnCust` | bit | NO |
| 23 | `AutoQty` | bit | NO |
| 24 | `AddlFontNormal` | bit | NO |
| 25 | `IndexKtch` | bit | NO |
| 26 | `PriceOnKtch` | bit | NO |
| 27 | `NoSort` | bit | NO |
| 28 | `PreSelOnKtch` | bit | NO |
| 29 | `MasterSubtotals` | bit | NO |
| 30 | `LblFormat` | int | NO |
| 31 | `Qty1Blank` | bit | NO |
| 32 | `SortBySeatNum` | bit | NO |
| 33 | `LblPrintAll` | bit | NO |
| 34 | `LblDeferHeader` | bit | NO |
| 35 | `AddlRevision` | bit | NO |
| 36 | `CompactSeatNum` | bit | NO |
| 37 | `PrintRecipes` | bit | NO |
| 38 | `StageKtchOnly` | bit | NO |
| 39 | `MultilineItems` | bit | NO |
| 40 | `CpnsOnKtch` | bit | NO |
| 41 | `StageLblOnly` | bit | NO |
| 42 | `ListEachTax` | bit | NO |
| 43 | `PrtItmsAsBumped` | bit | NO |
| 44 | `ShowDefaultPref` | bit | NO |
| 45 | `ShowSubbedPref` | bit | NO |
| 46 | `LblModifiedOnly` | bit | NO |
| 47 | `PrtSeatNum` | bit | NO |
| 48 | `EntID` | int | NO |
| 49 | `SyncStatus` | int | NO |
| 50 | `EntSync` | datetime | YES |
| 51 | `AllowPrefMbrAutoQty` | bit | NO |

### PrintJobs (0 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `PrintJobKey` | int | NO |
| 2 | `BizDate` | datetime | YES |
| 3 | `OrdNum` | int | NO |
| 4 | `PrtType` | nvarchar(25) | YES |
| 5 | `PrtQueue` | nvarchar(100) | YES |
| 6 | `PrtJob` | ntext(1073741823) | YES |
| 7 | `Attempts` | int | NO |
| 8 | `PrtName` | nvarchar(50) | YES |
| 9 | `CompName` | nvarchar(25) | YES |

### KDOrd (55 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `KDOrdKey` | int | NO |
| 2 | `OrdKey` | int | NO |
| 3 | `BizDate` | datetime | YES |
| 4 | `OrdNumber` | int | NO |
| 5 | `OrdType` | nvarchar(25) | NO |
| 6 | `OrdStartEmplKey` | int | NO |
| 7 | `OrdUpdateEmplKey` | int | NO |
| 8 | `SvrKey` | int | NO |
| 9 | `TableNum` | int | NO |
| 10 | `TableName` | nvarchar(10) | NO |
| 11 | `PagerNum` | int | NO |
| 12 | `KDSLastIdx` | int | NO |
| 13 | `HasKDSPriority` | int | NO |
| 14 | `Computer` | varchar(50) | NO |
| 15 | `CustName` | varchar(80) | NO |
| 16 | `CustAddr1` | varchar(80) | NO |
| 17 | `CustAddr2` | varchar(80) | NO |
| 18 | `ZoneName` | varchar(50) | YES |

### SyncRecords (247,659 rows)

| # | Column Name | Data Type | Nullable |
|---|-------------|-----------|----------|
| 1 | `SyncRecordsKey` | int | NO |
| 2 | `EntKey` | int | NO |
| 3 | `EntID` | int | NO |
| 4 | `TableName` | varchar(25) | NO |
| 5 | `SyncStatus` | int | NO |
| 6 | `EntSync` | datetime | YES |
| 7 | `Operation` | int | NO |
| 8 | `TableKey` | int | NO |
