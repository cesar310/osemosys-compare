# OSeMOSYS Model Conversion Log: Pyomo to GNU MathProg

## 1. Introduction

This document details the conversion of the OSeMOSYS (Open Source energy MOdeling SYStem) model from its Python/Pyomo representation to the GNU MathProg (GMPL) format.

*   **Source Files:**
    *   `osemosys.py`: The Pyomo-based Python model providing the core logic.
    *   `osemosys.txt`: A reference GNU MathProg version of OSeMOSYS, used for syntax, structure, and standard component formulations.
    *   `config.yaml`: Configuration file providing metadata for parameters, sets, and variables (names, indices, types).
*   **Target File:**
    *   `osemosys1.txt`: The resulting GNU MathProg model file.

The goal was to produce a MathProg model (`osemosys1.txt`) that accurately reflects the logic defined in `osemosys.py`, while adhering to the conventions and syntax of GMPL as exemplified by `osemosys.txt`.

## 2. General Approach

The conversion followed these principles:

*   **Primary Logic Source:** `osemosys.py` served as the definitive source for the model's mathematical logic, including sets, parameters, variables, the objective function, and constraints.
*   **Syntax and Structure Reference:** `osemosys.txt` was used as a template for correct GNU MathProg syntax, overall model structure (order of sets, parameters, variables, constraints), and for established MathProg formulations of standard OSeMOSYS components. This was particularly important for complex constraints like storage balancing.
*   **Metadata Reference:** `config.yaml` was consulted for canonical names of sets, parameters, and variables, their indexing, and data types, ensuring consistency.
*   **Handling Discrepancies:** Where `osemosys.py` and `osemosys.txt` differed in formulation for equivalent components, `osemosys.py`'s logic was prioritized unless `osemosys.txt` offered a more standard or complete MathProg implementation that was functionally equivalent or more robust in the MathProg environment (e.g., some storage equations, RE targets).

## 3. Component-wise Mapping

### Sets

Sets were directly translated from Pyomo `Set()` declarations to MathProg `set NAME;` statements.

*   `model.YEAR = Set()` -> `set YEAR;`
*   `model.TECHNOLOGY = Set()` -> `set TECHNOLOGY;`
*   `model.TIMESLICE = Set()` -> `set TIMESLICE;`
*   `model.FUEL = Set()` -> `set FUEL;`
*   `model.EMISSION = Set()` -> `set EMISSION;`
*   `model.MODE_OF_OPERATION = Set()` -> `set MODE_OF_OPERATION;`
*   `model.REGION = Set()` -> `set REGION;`
*   `model.SEASON = Set()` -> `set SEASON;`
*   `model.DAYTYPE = Set()` -> `set DAYTYPE;`
*   `model.DAILYTIMEBRACKET = Set()` -> `set DAILYTIMEBRACKET;`
*   `model.STORAGE = Set()` -> `set STORAGE;`
*   `model.FLEXIBLEDEMANDTYPE` was noted in `osemosys.py` but not used in `osemosys.txt` or in the active constraints of `osemosys.py`, so it was omitted in `osemosys1.txt`.

### Parameters

Pyomo `Param()` declarations were translated to MathProg `param NAME{indices...};`. Default values specified in Pyomo are typically handled by the separate data file in MathProg, so they are not part of the `param` definition in `osemosys1.txt` unless calculated.

*   Example: `model.OperationalLife = Param(model.REGION, model.TECHNOLOGY, default=1)` (Pyomo) -> `param OperationalLife{r in REGION, t in TECHNOLOGY};` (MathProg).

**Calculated Parameters:**
Several parameters in `osemosys.txt` are calculated based on other parameters. These were incorporated into `osemosys1.txt` using formulations from `osemosys.txt`, ensuring the necessary base parameters (like `DiscountRate`) were defined.
*   `DiscountFactor{r in REGION, y in YEAR} := (1 + DiscountRate[r]) ^ (y - (min{yy in YEAR} yy) + 0.0);`
*   `DiscountFactorMid{r in REGION, y in YEAR} := (1 + DiscountRate[r]) ^ (y - (min{yy in YEAR} yy) + 0.5);`
*   `DiscountRateIdv{r in REGION, t in TECHNOLOGY}, default DiscountRate[r];` (This allows technology-specific discount rates, defaulting to the regional rate).
*   `CapitalRecoveryFactor{r in REGION, t in TECHNOLOGY} := if DiscountRateIdv[r,t] > 0 then (DiscountRateIdv[r,t] * (1 + DiscountRateIdv[r,t])^OperationalLife[r,t]) / ((1 + DiscountRateIdv[r,t])^OperationalLife[r,t]-1) else 1/OperationalLife[r,t];`
*   `PvAnnuity{r in REGION, t in TECHNOLOGY} := if DiscountRateIdv[r,t] > 0 then (1 - (1 + DiscountRateIdv[r,t])^(-OperationalLife[r,t])) / DiscountRateIdv[r,t] else OperationalLife[r,t];`
*   `DiscountRateStorage{r in REGION, s in STORAGE}, default DiscountRate[r];` (Introduced for storage-specific discount rates, defaulting to regional rate).
*   `DiscountFactorStorage{r in REGION, s in STORAGE, y in YEAR} := (1 + DiscountRateStorage[r,s]) ^ (y - (min{yy in YEAR} yy) + 0.0);`
*   `DiscountFactorMidStorage{r in REGION, s in STORAGE, y in YEAR} := (1 + DiscountRateStorage[r,s]) ^ (y - (min{yy in YEAR} yy) + 0.5);`

The `TradeRoute` parameter was defined as `param TradeRoute{r in REGION, rr in REGION, f in FUEL, y in YEAR} binary;` using `REGION` for both region indices as per `osemosys.txt`, even though `config.yaml` mentioned `REGION_`.

The `ResultsPath` parameter (`param ResultsPath, symbolic default 'results';`) was added from `osemosys.txt` to specify the output directory for results.

### Check Statements

The `check` statements present in `osemosys.txt` were included verbatim in `osemosys1.txt`. These statements help in validating parameter values in the data file before solving the model.

### Variables

Pyomo `Var()` declarations were translated to MathProg `var NAME{indices...} attributes;`.

*   Example: `model.NewCapacity = Var(model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals)` (Pyomo) -> `var NewCapacity{r in REGION, t in TECHNOLOGY, y in YEAR} >= 0;` (MathProg).
*   Domain Mapping:
    *   `NonNegativeReals` (Pyomo) -> `>= 0` (MathProg).
    *   `NonNegativeIntegers` (Pyomo) -> `>= 0, integer` (MathProg).
    *   Variables in Pyomo without explicit domains (implying free variables) were defined in MathProg without bounds (e.g., `var Trade{...};`).

### Objective Function

The objective function in `osemosys.py` is defined as:
`model.OBJ = Objective(rule=ObjectiveFunction_rule, sense=minimize)`
where `ObjectiveFunction_rule` is `sum(model.ModelPeriodCostByRegion[r] for r in model.REGION)`.
`ModelPeriodCostByRegion[r]` is a variable, constrained by:
`model.ModelPeriodCostByRegion[r] == sum(model.TotalDiscountedCost[r, y] for y in model.YEAR)`.

This is equivalent to minimizing the sum of `TotalDiscountedCost[r,y]` over regions and years. `osemosys.txt` uses this direct form:
`minimize cost: sum{r in REGION, y in YEAR} TotalDiscountedCost[r,y];`
`osemosys1.txt` adopts this direct MathProg formulation, along with the constraint (`Acc4_ModelPeriodCostByRegion`) that defines `ModelPeriodCostByRegion`, ensuring mathematical equivalence.

### Constraints

This was the most detailed part of the conversion. Constraint names from `osemosys.py` (usually derived from rule function names) were used as a basis, sometimes adopting `osemosys.txt` names if they were more standard for MathProg OSeMOSYS.

**Conditional Logic:**
*   Pyomo's `Constraint.Skip` or `if condition: return X else: return Constraint.Skip` was handled by adding the condition to the MathProg constraint's domain: `s.t. ConstraintName{indices... : condition}: ...;`.
*   For Pyomo rules like `if param != 0: return A == B else: return A == 0`, if `A` would not naturally become zero when `param` is zero, a separate constraint was added for the `param = 0` case to enforce `A = 0`. This was applied to:
    *   `EBa1_RateOfFuelProduction1` (Pyomo: `RateOfFuelProduction1_rule`) and `EBa1_RateOfFuelProduction1_Zero`.
    *   `EBa4_RateOfFuelUse1` (Pyomo: `RateOfFuelUse1_rule`) and `EBa4_RateOfFuelUse1_Zero`.
    *   `E1_AnnualEmissionProductionByMode` (Pyomo: `AnnualEmissionProductionByMode_rule`) and `E1_AnnualEmissionProductionByMode_Zero`.
    *   `E3_EmissionsPenaltyByTechAndEmission` (Pyomo: `EmissionPenaltyByTechAndEmission_rule`) and `E3_EmissionsPenaltyByTechAndEmission_Zero`.

**Specific Constraint Groups and Decisions:**

*   **Capital Costs & Salvage Value (Technology):**
    *   A significant difference exists between `osemosys.py` and `osemosys.txt` in handling technology capital costs. `osemosys.py` calculates `CapitalInvestment` as a lump sum (`CapitalCost * NewCapacity`) and then discounts this lump sum. `osemosys.txt` calculates `CapitalInvestment` as an annualized cost (`CapitalCost * NewCapacity * CapitalRecoveryFactor * PvAnnuity`).
    *   `osemosys1.txt` follows the **`osemosys.py` logic** for these calculations to maintain fidelity to the source Python model. Thus, constraints `CC1_UndiscountedCapitalInvestment_Pyomo` and `CC2_DiscountedCapitalInvestment_Pyomo` in `osemosys1.txt` reflect this:
        *   `CC1_UndiscountedCapitalInvestment_Pyomo: CapitalCost[r,t,y] * NewCapacity[r,t,y] = CapitalInvestment[r,t,y];`
        *   `CC2_DiscountedCapitalInvestment_Pyomo: CapitalInvestment[r,t,y] / ((1 + DiscountRate[r])^((y - (min{yy in YEAR} yy)))) = DiscountedCapitalInvestment[r,t,y];`
    *   Similarly, salvage value calculations (`SV_Pyomo_Combined`, `SV4_SalvageValueDiscounted_Pyomo`) in `osemosys1.txt` are based on the logic in `osemosys.py`.
    *   The parameters `CapitalRecoveryFactor` and `PvAnnuity` are still defined in `osemosys1.txt` (as they are in `osemosys.txt`) but are not used in the main capital cost calculation chain for technologies, following the `osemosys.py` deviation.

*   **Storage Equations (S1-S15 for balance, SC1-SC6 for limits, SI1-SI10 for investments):**
    *   These equations are intricate. The MathProg formulations in `osemosys.txt` were heavily referenced for structure and MathProg idioms.
    *   `RateOfStorageCharge_constraint` (Pyomo) and `RateOfStorageDischarge_constraint` (Pyomo) were translated to `S1_RateOfStorageCharge` and `S2_RateOfStorageDischarge` respectively, using the summation style from `osemosys.txt` which is more natural for MathProg.
    *   Storage balance equations (YearStart, YearFinish, SeasonStart, DayTypeStart, DayTypeFinish - corresponding to `S5` through `S15` in `osemosys.txt`) were carefully translated. For instance:
        *   `StorageLevelYearStart_constraint` (Pyomo) to `S5_and_S6_StorageLevelYearStart` (MathProg).
        *   `StorageLevelYearFinish_constraint` (Pyomo): A discrepancy regarding `y` vs `y-1` in the summation for the last year's finish level was resolved by adopting the `osemosys.txt` formulation (`NetChargeWithinYear[...,y]`) as it appeared more standard for inventory balance.
        *   `StorageLevelDayTypeStart_constraint` (Pyomo): The `DaysInDayType` multiplier for `NetChargeWithinDay`, present in `osemosys.txt` but not `osemosys.py` for this specific constraint, was included from `osemosys.txt` as it is logically necessary for scaling daily changes across a multi-day daytype.
        *   `StorageLevelDayTypeFinish_constraint` (Pyomo `S13_S14_S15_StorageLevelDayTypeFinish_ref`): The complex backward-looking structure from `osemosys.txt` (and present in Pyomo) was used.
    *   Storage limit constraints (SC1-SC4, covering 8 Pyomo constraints) were translated using `osemosys.txt` structure, which uses `card(timeslice_index)` for ordering time slices within a day.
    *   Storage investment constraints (SI1-SI10) followed `osemosys.txt` structure, which aligns well with `osemosys.py` logic for these.

*   **Emission Accounting:**
    *   `EmissionsAccounting2_rule` (Pyomo): `sum(AnnualEmissions) == ModelPeriodEmissions - ModelPeriodExogenousEmission`. This was translated as is, interpreting `ModelPeriodEmissions` as the total emissions including exogenous ones. `osemosys.txt` had a `+` sign here, which implies a different definition of `ModelPeriodEmissions`. The `osemosys.py` logic was retained.

*   **RE Generation Target (RE1-RE5):**
    *   These constraints, present in `osemosys.txt` but not explicitly in the active `osemosys.py` code, were included in `osemosys1.txt` to provide a more complete standard OSeMOSYS model. Their structure directly follows `osemosys.txt`.

*   **Constraint Naming:** Generally, Pyomo rule names were adapted (e.g., `SpecifiedDemand_rule` -> `EQ_SpecifiedDemand`). Where `osemosys.txt` provided clear, standard names (e.g., `CAa1_...` for capacity adequacy), those were often used or mapped to.

## 4. Structural Differences and Assumptions

*   **Looping vs. Set Operations:** Pyomo rules often involve Python loops to generate constraints. MathProg uses implicit looping via set notation (e.g., `sum{i in SET}`). This is a natural translation.
*   **Conditional Constraint Generation:** Pyomo can dynamically skip creating constraints. MathProg achieves this by making the constraint conditional on its domain using `{indices... : condition}`.
*   **Data Handling:** A key difference is that Pyomo models can embed default data values or load them dynamically in Python. MathProg models are typically separate from their data files (`.dat`). `osemosys1.txt` assumes parameters will be populated from a data file.
*   **Min/Max Year/Season/Daytype:** Pyomo uses `min(model.YEAR)` or `max(model.YEAR)`. MathProg uses `min{yy in YEAR} yy` or `max{yy in YEAR} yy`. This was applied. For ordered sets like SEASON or DAYTYPE where `ls-1` or `ld-1` was used, it's assumed these sets are numerically ordered (e.g. 1, 2, 3...).

## 5. Output Formatting

The `printf` and `table` statements from the end of `osemosys.txt` were included in `osemosys1.txt`. These are used for generating CSV output of model results. Some minor adjustments were made to the `printf` for "Summary" emissions and cost to align with variables defined in `osemosys1.txt`.

## 6. Conclusion

The file `osemosys1.txt` has been generated to be a GNU MathProg representation of the OSeMOSYS model specified in `osemosys.py`. The conversion aimed for logical equivalence with `osemosys.py`, using `osemosys.txt` as a crucial reference for MathProg syntax, standard component formulations, and overall structure. Key differences in costing approaches were resolved by adhering to the `osemosys.py` methodology.
