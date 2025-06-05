# Detailed Item-by-Item Model Comparison

This document provides a rigorous comparison of `osemosys.py`, `osemosys.txt`, and `config.yaml`.

## Sets Comparison

| Pyomo Set Name | Pyomo Definition | config.yaml Definition | osemosys.txt Definition | Status/Action |
|---|---|---|---|---|
| YEAR | `model.YEAR = Set()` | `YEAR: {dtype: int, type: set}` | `set YEAR;` | Consistent. |
| TECHNOLOGY | `model.TECHNOLOGY = Set()` | `TECHNOLOGY: {dtype: str, type: set}` | `set TECHNOLOGY;` | Consistent. |
| TIMESLICE | `model.TIMESLICE = Set()` | `TIMESLICE: {dtype: str, type: set}` | `set TIMESLICE;` | Consistent. |
| FUEL | `model.FUEL = Set()` | `FUEL: {dtype: str, type: set}` | `set FUEL;` | Consistent. |
| EMISSION | `model.EMISSION = Set()` | `EMISSION: {dtype: str, type: set}` | `set EMISSION;` | Consistent. |
| MODE_OF_OPERATION | `model.MODE_OF_OPERATION = Set()` | `MODE_OF_OPERATION: {dtype: str, type: set}` | `set MODE_OF_OPERATION;` | Consistent. |
| REGION | `model.REGION = Set()` | `REGION: {dtype: str, type: set}` | `set REGION;` | Consistent. |
| SEASON | `model.SEASON = Set()` | `SEASON: {dtype: int, type: set}` | `set SEASON;` | Consistent. |
| DAYTYPE | `model.DAYTYPE = Set()` | `DAYTYPE: {dtype: int, type: set}` | `set DAYTYPE;` | Consistent. |
| DAILYTIMEBRACKET | `model.DAILYTIMEBRACKET = Set()` | `DAILYTIMEBRACKET: {dtype: int, type: set}` | `set DAILYTIMEBRACKET;` | Consistent. |
| FLEXIBLEDEMANDTYPE | `model.FLEXIBLEDEMANDTYPE = Set()` | `FLEXIBLEDEMANDTYPE: {dtype: str, type: set}` | `set FLEXIBLEDEMANDTYPE;` | Consistent. |
| STORAGE | `model.STORAGE = Set()` | `STORAGE: {dtype: str, type: set}` | `set STORAGE;` | Consistent. |
| REGION_ | Not defined in osemosys.py | `REGION_: {dtype: str, type: set}` | `set REGION_;` (original) | Inconsistent. `REGION_` is not in `osemosys.py`. Action: Confirmed `REGION_` was removed from the updated `osemosys.txt` in Subtask 5 & 7. |

## Parameters Comparison

| Pyomo Param Name | Pyomo Definition (Indices, Default) | config.yaml Definition (Indices, Default, Type) | osemosys.txt Definition (Indices) | Status/Action |
|---|---|---|---|---|
| DiscountRate | `model.DiscountRate = Param(model.REGION, default=0.05)` | `DiscountRate: {indices: [REGION], type: param, dtype: float, default: 0.05}` | `param DiscountRate{r in REGION};` | Consistent. Default handling relies on data pipeline for `osemosys.txt` to match `osemosys.py`'s 0.05 default if data is missing. |
| YearSplit | `model.YearSplit = Param(model.TIMESLICE, model.YEAR)` | `YearSplit: {indices: [TIMESLICE,YEAR], type: param, dtype: float, default: 0.00137}` | `param YearSplit{l in TIMESLICE, y in YEAR};` | Potentially Divergent Default. `osemosys.py` (implicit 0 default if no data) vs `config.yaml` (0.00137). Action: For strict `osemosys.py` equivalence, `osemosys.txt` data pipeline must ensure 0 if data missing, unless `osemosys.py` is intended to use `config.yaml`'s default (non-standard Pyomo). |
| Conversionls | `model.Conversionls = Param(model.TIMESLICE, model.SEASON, default=0)` | `Conversionls: {indices: [TIMESLICE,SEASON], type: param, dtype: float, default: 0}` | `param Conversionls{l in TIMESLICE, ls in SEASON};` (original: `binary;`) | Type Aligned. Changed from `binary` to numeric in `osemosys.txt` (Subtask 7) to match Pyomo's float definition. Data must ensure 0/1. |
| Conversionld | `model.Conversionld = Param(model.TIMESLICE, model.DAYTYPE, default=0)` | `Conversionld: {indices: [TIMESLICE,DAYTYPE], type: param, dtype: float, default: 0}` | `param Conversionld{l in TIMESLICE, ld in DAYTYPE};` (original: `binary;`) | Type Aligned. Changed from `binary` to numeric in `osemosys.txt` (Subtask 7). |
| Conversionlh | `model.Conversionlh = Param(model.TIMESLICE, model.DAILYTIMEBRACKET, default=0)` | `Conversionlh: {indices: [TIMESLICE,DAILYTIMEBRACKET], type: param, dtype: float, default: 0}` | `param Conversionlh{l in TIMESLICE, lh in DAILYTIMEBRACKET};` (original: `binary;`) | Type Aligned. Changed from `binary` to numeric in `osemosys.txt` (Subtask 7). |
| TradeRoute | `model.TradeRoute = Param(model.REGION, model.REGION, model.FUEL, model.YEAR, default=0)` | `TradeRoute: {indices: [REGION,REGION_,FUEL,YEAR], type: param, dtype: float, default: 0}` | `param TradeRoute {r in REGION, rr in REGION, f in FUEL, y in YEAR};` (original: `binary;`) | Type Aligned & Indexing Confirmed. Changed from `binary` to numeric in `osemosys.txt` (Subtask 7). `REGION_` impact handled by its removal. |
| ReserveMarginTagTechnology | `model.ReserveMarginTagTechnology = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0)` | `ReserveMarginTagTechnology: {indices: [REGION,TECHNOLOGY,YEAR], type: param, dtype: float, default: 0}` | `param ReserveMarginTagTechnology{r in REGION, t in TECHNOLOGY, y in YEAR};` (original: `>= 0 <= 1;`) | Declaration Aligned. Removed explicit bounds ` >= 0 <= 1` in `osemosys.txt` (Subtask 7) to match Pyomo's standard Param declaration style. Actual 0/1 behavior relies on data or usage context. |
| ReserveMarginTagFuel | `model.ReserveMarginTagFuel = Param(model.REGION, model.FUEL, model.YEAR, default=0)` | `ReserveMarginTagFuel: {indices: [REGION,FUEL,YEAR], type: param, dtype: float, default: 0}` | `param ReserveMarginTagFuel{r in REGION, f in FUEL, y in YEAR};` (original: `binary;`) | Type Aligned. Changed from `binary` to numeric in `osemosys.txt` (Subtask 7). |
| RETagTechnology | `model.RETagTechnology = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0)` | `RETagTechnology: {indices: [REGION,TECHNOLOGY,YEAR], type: param, dtype: float, default: 0}` | `param RETagTechnology{r in REGION, t in TECHNOLOGY, y in YEAR};` (original: `binary;`) | Type Aligned. Changed from `binary` to numeric in `osemosys.txt` (Subtask 7). |
| RETagFuel | `model.RETagFuel = Param(model.REGION, model.FUEL, model.YEAR, default=0)` | `RETagFuel: {indices: [REGION,FUEL,YEAR], type: param, dtype: float, default: 0}` | `param RETagFuel{r in REGION, f in FUEL, y in YEAR};` (original: `binary;`) | Type Aligned. Changed from `binary` to numeric in `osemosys.txt` (Subtask 7). |
(Note: This would continue for all other parameters.)

## Variables Comparison

| Pyomo Var Name | Pyomo Definition (Domain, Initialize) | osemosys.txt Definition (Domain - post Subtask 7) | Status/Action |
|---|---|---|---|
| RateOfDemand | `model.RateOfDemand = Var(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, domain=NonNegativeReals, initialize=0.0)` | `var RateOfDemand{r in REGION, l in TIMESLICE, f in FUEL, y in YEAR}>= 0;` | Consistent. |
| NumberOfNewTechnologyUnits | `model.NumberOfNewTechnologyUnits = Var(model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeIntegers, initialize=0)` | `var NumberOfNewTechnologyUnits{r in REGION, t in TECHNOLOGY, y in YEAR} >= 0,integer;` | Consistent. |
| RateOfStorageCharge | `model.RateOfStorageCharge = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, initialize=0.0)` | `var RateOfStorageCharge{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR};` (original: `>= 0;`) | Domain Aligned. Changed from `>= 0` to `Reals` (no explicit bound) in `osemosys.txt` (Subtask 7) to match Pyomo's default `Reals` domain. |
| RateOfStorageDischarge | `model.RateOfStorageDischarge = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, initialize=0.0)` | `var RateOfStorageDischarge{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR};` (original: `>= 0;`) | Domain Aligned. Changed from `>= 0` to `Reals` in `osemosys.txt` (Subtask 7). |
| NetChargeWithinYear | `model.NetChargeWithinYear = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, initialize=0.0)` | `var NetChargeWithinYear{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR};` | Consistent. (Already Reals) |
| NetChargeWithinDay | `model.NetChargeWithinDay = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, initialize=0.0)` | `var NetChargeWithinDay{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR};` | Consistent. (Already Reals) |
| Trade | `model.Trade = Var(model.REGION, model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, initialize=0.0)` | `var Trade{r in REGION, rr in REGION, l in TIMESLICE, f in FUEL, y in YEAR};` | Consistent. (Already Reals) |
| TradeAnnual | `model.TradeAnnual = Var(model.REGION, model.REGION, model.FUEL, model.YEAR, initialize=0.0)` | `var TradeAnnual{r in REGION, rr in REGION, f in FUEL, y in YEAR};` | Consistent. (Already Reals) |
| TotalTechnologyModelPeriodActivity | `model.TotalTechnologyModelPeriodActivity = Var(model.REGION, model.TECHNOLOGY, initialize=0.0)` | `var TotalTechnologyModelPeriodActivity{r in REGION, t in TECHNOLOGY};` | Consistent. (Already Reals) |
| TotalREProductionAnnual | `model.TotalREProductionAnnual = Var(model.REGION, model.YEAR, initialize=0.0)` | `var TotalREProductionAnnual{r in REGION, y in YEAR};` | Consistent. (Already Reals) |
| RETotalProductionOfTargetFuelAnnual | `model.RETotalProductionOfTargetFuelAnnual = Var(model.REGION, model.YEAR, initialize=0.0)` | `var RETotalProductionOfTargetFuelAnnual{r in REGION, y in YEAR};` | Consistent. (Already Reals) |
(Note: All variables would be listed with similar detailed analysis.)

## Objective Function Comparison

| Pyomo Definition | osemosys.txt Definition | Status/Action |
|---|---|---|
| `model.OBJ = Objective(rule=lambda model: sum(model.ModelPeriodCostByRegion[r] for r in model.REGION), sense=minimize)` | `minimize cost: sum{r in REGION} ModelPeriodCostByRegion[r];` | Consistent. Both minimize sum of ModelPeriodCostByRegion over REGION. |

## Constraints Comparison (Summary - Full details in update_log.md)
(This section would be populated by Subtask 8, summarizing findings from the detailed constraint comparison and cross-referencing actions taken in Subtask 7.)

## Committed Changes to `osemosys.txt` (Subtask 7)

This section documents the specific modifications applied to `osemosys.txt` in Subtask 7 to align it more strictly with `osemosys.py` based on the re-evaluation.

1.  **Set `REGION_` Removal**:
    *   The declaration `set REGION_;` was confirmed removed from `osemosys.txt`.

2.  **Parameter Type Adjustments (Debinarization)**:
    *   `param Conversionls{...} binary;` changed to `param Conversionls{...};`
    *   `param Conversionld{...} binary;` changed to `param Conversionld{...};`
    *   `param Conversionlh{...} binary;` changed to `param Conversionlh{...};`
    *   `param TradeRoute{...} binary;` changed to `param TradeRoute{...};`
    *   `param ReserveMarginTagFuel{...} binary;` changed to `param ReserveMarginTagFuel{...};`
    *   `param RETagTechnology{...} binary;` changed to `param RETagTechnology{...};`
    *   `param RETagFuel{...} binary;` changed to `param RETagFuel{...};`
    *   `param ReserveMarginTagTechnology{...} >= 0 <= 1;` changed to `param ReserveMarginTagTechnology{...};` (bounds removed).

3.  **Variable Domain Adjustments (to Reals where Pyomo implies Reals)**:
    *   `var RateOfStorageCharge{...} >= 0;` changed to `var RateOfStorageCharge{...};`
    *   `var RateOfStorageDischarge{...} >= 0;` changed to `var RateOfStorageDischarge{...};`
    *   Variables like `Trade`, `TradeAnnual`, `NetChargeWithinYear`, `NetChargeWithinDay`, `TotalTechnologyModelPeriodActivity`, `TotalREProductionAnnual`, `RETotalProductionOfTargetFuelAnnual` were already consistent with Pyomo's `Reals` default and needed no change in this step.

4.  **Constraint Iteration Condition Removals**:
    *   `EQ_SpecifiedDemand`: Condition `SpecifiedAnnualDemand[r,f,y] > 0` removed from iterator.
    *   `EBa9_EnergyBalanceEachTS3`: Condition `SpecifiedAnnualDemand[r,f,y] > 0` removed from iterator.
    *   `TCC1_TotalAnnualMaxCapacityConstraint`: Condition `TotalAnnualMaxCapacity[r,t,y] <> 99999` removed.
    *   `TCC2_TotalAnnualMinCapacityConstraint`: Condition `TotalAnnualMinCapacity[r,t,y]>0` removed.
    *   `NCC1_TotalAnnualMaxNewCapacityConstraint`: Condition `TotalAnnualMaxCapacityInvestment[r,t,y] <> 99999` removed.
    *   `NCC2_TotalAnnualMinNewCapacityConstraint`: Condition `TotalAnnualMinCapacityInvestment[r,t,y]>0` removed.
    *   `AAC2_TotalAnnualTechnologyActivityUpperLimit`: Condition `TotalTechnologyAnnualActivityUpperLimit[r,t,y] <> 99999` removed.
    *   `AAC3_TotalAnnualTechnologyActivityLowerLimit`: Condition `TotalTechnologyAnnualActivityLowerLimit[r,t,y]>0` removed.
    *   `TAC2_TotalModelHorizonTechnologyActivityUpperLimit`: Condition `TotalTechnologyModelPeriodActivityUpperLimit[r,t]<>99999` removed.
    *   `TAC3_TotalModelHorizenTechnologyActivityLowerLimit`: Condition `TotalTechnologyModelPeriodActivityLowerLimit[r,t]>0` removed (original "Horizen" typo was part of the search pattern).
    *   `E8_AnnualEmissionsLimit`: Condition `AnnualEmissionLimit[r, e, y] <> 99999` removed.
    *   `E9_ModelPeriodEmissionsLimit`: Condition `ModelPeriodEmissionLimit[r, e] <> 99999` removed.

These changes aim for a stricter component-level correspondence with `osemosys.py` declarations, as per the project's requirements. The functional implications of these changes (e.g., relying on data pipeline for defaults, or Pyomo's default behavior for unconstrained variables) are noted.
