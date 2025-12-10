# Security & Permissions Deep Dive
## Document 07 - How Permissions Work in REVENTION

**Generated:** 2025-12-10 15:15:00
**Database:** REVENTION

---

## Overview

The REVENTION database uses a hierarchical security model:

1. **Security Groups (SecGrp)** - Define permission sets
2. **Security Rights (SecGrpRights)** - Specific permissions per group
3. **Employees** - Linked to security groups via `SecLevel`
4. **Individual Rights (SecIndRights)** - Override group settings per user

---

## Security Tables Found (7 tables)

| Table | Rows | Purpose |
|-------|------|---------|
| `SecGrp` | 7 | Security groups/roles |
| `SecGrpRights` | 1,428 | Permissions per group |
| `SecRightsDefault` | 244 | Default permission definitions |
| `SecIndGrp` | 54 | Individual user group assignments |
| `SecIndRights` | 1,389 | Individual user permission overrides |
| `SecChgAudit` | 3,207 | Audit trail for security changes |
| `OrdPreAuth` | - | Pre-authorization records (security-related) |

---

## Key Table Schemas

### SecGrp (Security Groups)

| Column | Type | Description |
|--------|------|-------------|
| `SecGroupKey` | int | Primary key |
| `Name` | nvarchar(50) | Group name (e.g., "Manager", "Cashier") |
| `CreatedBy` | nvarchar(50) | Who created the group |
| `CreatedDate` | datetime | When created |
| `SecLevel` | int | Security level (default 9) |

### SecGrpRights (Group Permissions)

| Column | Type | Description |
|--------|------|-------------|
| `SecGroupRightsKey` | int | Primary key |
| `SecGroupKey` | int | FK to SecGrp |
| `RightKey` | int | FK to SecRightsDefault |
| `Setting` | smallint | Permission value (0=denied, 1=allowed, etc.) |

### SecRightsDefault (Permission Definitions)

| Column | Type | Description |
|--------|------|-------------|
| `SecRightsKey` | int | Primary key |
| `ModuleName` | nvarchar(50) | Module/area (e.g., "Orders", "Reports") |
| `ItemName` | nvarchar(50) | Specific permission name |
| `DefaultVal` | smallint | Default permission value |
| `Ident` | nvarchar(4) | Short identifier |

### Employee Security Link

The Employee table has a `SecLevel` column that links to security:

| Column | Type | Description |
|--------|------|-------------|
| `SecLevel` | int | Security level assigned to employee |

---

## Working Permission Queries

### 1. List All Security Groups

```sql
SELECT
    SecGroupKey,
    Name,
    SecLevel,
    CreatedBy,
    CreatedDate
FROM SecGrp
ORDER BY SecLevel, Name;
```

### 2. List Permission Definitions

```sql
SELECT
    SecRightsKey,
    ModuleName,
    ItemName,
    DefaultVal,
    Ident
FROM SecRightsDefault
ORDER BY ModuleName, ItemName;
```

### 3. View Permissions for a Security Group

```sql
-- Replace @GroupName with actual group name
SELECT
    sg.Name AS GroupName,
    sd.ModuleName,
    sd.ItemName,
    sr.Setting,
    CASE sr.Setting
        WHEN 0 THEN 'Denied'
        WHEN 1 THEN 'Allowed'
        WHEN 2 THEN 'Requires Approval'
        ELSE 'Unknown'
    END AS PermissionStatus
FROM SecGrpRights sr
INNER JOIN SecGrp sg ON sr.SecGroupKey = sg.SecGroupKey
INNER JOIN SecRightsDefault sd ON sr.RightKey = sd.SecRightsKey
WHERE sg.Name = 'Manager'  -- Replace with group name
ORDER BY sd.ModuleName, sd.ItemName;
```

### 4. Find Employees and Their Security Level

```sql
SELECT
    e.EmployeeKey,
    e.FirstName,
    e.LastName,
    e.SecLevel,
    sg.Name AS SecurityGroupName
FROM Employee e
LEFT JOIN SecGrp sg ON e.SecLevel = sg.SecLevel
ORDER BY e.LastName, e.FirstName;
```

### 5. Check if Employee Has Specific Permission

```sql
-- Check if an employee (by key) has a specific permission
DECLARE @EmployeeKey INT = 1;  -- Replace with employee key
DECLARE @PermissionName VARCHAR(50) = 'Void Order';  -- Replace with permission

SELECT
    e.FirstName + ' ' + e.LastName AS EmployeeName,
    e.SecLevel,
    sd.ModuleName,
    sd.ItemName,
    COALESCE(sr.Setting, sd.DefaultVal) AS PermissionValue,
    CASE COALESCE(sr.Setting, sd.DefaultVal)
        WHEN 0 THEN 'DENIED'
        WHEN 1 THEN 'ALLOWED'
        WHEN 2 THEN 'REQUIRES APPROVAL'
        ELSE 'UNKNOWN'
    END AS PermissionStatus
FROM Employee e
CROSS JOIN SecRightsDefault sd
LEFT JOIN SecGrpRights sr ON sr.RightKey = sd.SecRightsKey
    AND sr.SecGroupKey IN (SELECT SecGroupKey FROM SecGrp WHERE SecLevel = e.SecLevel)
WHERE e.EmployeeKey = @EmployeeKey
  AND sd.ItemName LIKE '%' + @PermissionName + '%';
```

### 6. Security Change Audit

```sql
SELECT TOP 50
    ChgTime,
    EmpName AS Employee,
    SecType,
    SecItem AS Permission,
    SecGrp AS AffectedGroup,
    OrigValue,
    NewValue,
    ChgEmpName AS ChangedBy
FROM SecChgAudit
ORDER BY ChgTime DESC;
```

---

## Permission Architecture Diagram

```
┌─────────────────┐
│   Employee      │
│  (SecLevel)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│    SecGrp       │◄────►│  SecGrpRights    │
│ (SecLevel,Name) │      │ (SecGroupKey,    │
└─────────────────┘      │  RightKey)       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ SecRightsDefault │
                         │ (Permission      │
                         │  definitions)    │
                         └──────────────────┘

Optional Individual Overrides:
┌─────────────────┐      ┌──────────────────┐
│   SecIndGrp     │      │  SecIndRights    │
│ (User-Group     │      │ (User-specific   │
│  assignments)   │      │  overrides)      │
└─────────────────┘      └──────────────────┘
```

---

## Common Permission Issues

### Problem: Cashier can't void items

**Check this query:**

```sql
SELECT
    sg.Name AS SecurityGroup,
    sd.ModuleName,
    sd.ItemName,
    sr.Setting
FROM SecGrpRights sr
JOIN SecGrp sg ON sr.SecGroupKey = sg.SecGroupKey
JOIN SecRightsDefault sd ON sr.RightKey = sd.SecRightsKey
WHERE sd.ItemName LIKE '%void%'
ORDER BY sg.Name, sd.ItemName;
```

### Problem: Employee missing from security group

**Check assignment:**

```sql
SELECT
    e.EmployeeKey,
    e.FirstName,
    e.LastName,
    e.SecLevel,
    sg.Name AS AssignedGroup
FROM Employee e
LEFT JOIN SecGrp sg ON e.SecLevel = sg.SecLevel
WHERE e.SecLevel IS NULL OR sg.SecGroupKey IS NULL;
```

---

## Notes

- The primary link between Employee and SecGrp is via `SecLevel`
- `SecIndGrp` provides additional group assignments per user
- `SecIndRights` allows per-user permission overrides
- All security changes are logged in `SecChgAudit`
- Permission values: 0=Denied, 1=Allowed, 2=Requires Approval

---

*Document created from REVENTION database analysis*
