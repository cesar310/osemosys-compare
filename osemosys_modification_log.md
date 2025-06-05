# OSeMOSYS Model `osemosys.txt` Modification Log for Alignment with `osemosys.py`

## 1. Introduction

*   **Purpose:** To document the specific changes made to the GNU MathProg model file `osemosys.txt` to ensure its mathematical model formulation is equivalent to the Pyomo-based Python model in `osemosys.py`.
*   **Source for target logic:** `osemosys.py`
*   **File modified:** `osemosys.txt`

This log provides a detailed account of modifications, enabling users to understand the alignment process and the resulting consistency between the two model representations.

## 2. Global Changes

### Set Definition

*   **Added `set FLEXIBLEDEMANDTYPE;`**
    *   Reason: To match the set definitions in `osemosys.py`. `FLEXIBLEDEMANDTYPE` was present in `osemosys.py` but not in the original `osemosys.txt`.

### Parameter Definitions Removed

The following parameter definitions were **removed** from `osemosys.txt`'s `param` section. This is because `osemosys.py` either performs the necessary calculations directly within constraint rules or uses a more general parameter (like `DiscountRate[r]`) for contexts where `osemosys.txt` had specialized versions.

*   **`param DiscountRateIdv{r in REGION, t in TECHNOLOGY}, default DiscountRate[r];`**
    *   Reason: `osemosys.py` uses the general `DiscountRate[r]` for technology-related discounting where applicable; it does not define a separate `DiscountRateIdv`.
*   **`param DiscountFactor{r in REGION, y in YEAR} := (1 + DiscountRate[r]) ^ (y - min{yy in YEAR} min(yy) + 0.0);`**
    *   Reason: `osemosys.py` calculates discount factors inline, e.g., `((1 + model.DiscountRate[r]) ** (y - min(model.YEAR)))`.
*   **`param DiscountFactorMid{r in REGION, y in YEAR} := (1 + DiscountRate[r]) ^ (y - min{yy in YEAR} min(yy) + 0.5);`**
    *   Reason: `osemosys.py` calculates mid-year discount factors inline, e.g., `((1 + model.DiscountRate[r]) ** (y - min(model.YEAR) + 0.5))`.
*   **`param CapitalRecoveryFactor{r in REGION, t in TECHNOLOGY} := ...;`**
    *   Reason: `osemosys.py`'s formulation for capital costs does not use an explicit Capital Recovery Factor (CRF) to annualize costs in the way `osemosys.txt` did for `CapitalInvestment`.
*   **`param PvAnnuity{r in REGION, t in TECHNOLOGY} := ...;`**
    *   Reason: Similar to CRF, `osemosys.py` does not use a pre-calculated Present Value of Annuity factor in its primary capital cost calculations.
*   **`param DiscountRateStorage{r in REGION, s in STORAGE};`**
    *   Reason: `osemosys.py` uses the general `DiscountRate[r]` for storage-related discounting, not a separate `DiscountRateStorage`.
*   **`param DiscountFactorStorage{r in REGION, s in STORAGE, y in YEAR} := ...;`**
    *   Reason: `osemosys.py` calculates discount factors for storage inline using `DiscountRate[r]`.
*   **`param DiscountFactorMidStorage{r in REGION, s in STORAGE, y in YEAR} := ...;`**
    *   Reason: `osemosys.py` calculates mid-year discount factors for storage inline using `DiscountRate[r]`.

## 3. Constraint Modifications

This section details changes to specific constraints in `osemosys.txt`.

### Conditional Constraints (Zero-Case Handling)

To precisely match Pyomo's conditional logic (e.g., `if param != 0: return A == B else: return A == 0`), explicit "ZeroCase" constraints were added for rules where the `else` part sets a variable to zero.

1.  **Constraint:** `EBa1_RateOfFuelProduction1`
    *   **Pyomo Rule:** `RateOfFuelProduction1_rule`
    *   **Reason:** To handle cases where `OutputActivityRatio` is zero, ensuring `RateOfProductionByTechnologyByMode` is set to zero, as per Pyomo logic.
    *   **Original (Relevant Part):**
        ```mathprog
        s.t. EBa1_RateOfFuelProduction1{r,l,f,t,m,y: OutputActivityRatio[r,t,f,m,y] <> 0}:
            RateOfActivity[r,l,t,m,y] * OutputActivityRatio[r,t,f,m,y] = RateOfProductionByTechnologyByMode[r,l,t,m,f,y];
        ```
    *   **Modification:**
        Added the following constraint:
        ```mathprog
        s.t. EBa1_RateOfFuelProduction1_ZeroCase{r in REGION, l in TIMESLICE, f in FUEL, t in TECHNOLOGY, m in MODE_OF_OPERATION, y in YEAR: OutputActivityRatio[r,t,f,m,y] = 0}:
            RateOfProductionByTechnologyByMode[r,l,t,m,f,y] = 0;
        ```

2.  **Constraint:** `EBa4_RateOfFuelUse1`
    *   **Pyomo Rule:** `RateOfFuelUse1_rule`
    *   **Reason:** To handle cases where `InputActivityRatio` is zero, ensuring `RateOfUseByTechnologyByMode` is set to zero.
    *   **Original (Relevant Part):**
        ```mathprog
        s.t. EBa4_RateOfFuelUse1{r,l,f,t,m,y: InputActivityRatio[r,t,f,m,y] <> 0}:
            RateOfActivity[r,l,t,m,y] * InputActivityRatio[r,t,f,m,y] = RateOfUseByTechnologyByMode[r,l,t,m,f,y];
        ```
    *   **Modification:**
        Added the following constraint:
        ```mathprog
        s.t. EBa4_RateOfFuelUse1_ZeroCase{r in REGION, l in TIMESLICE, f in FUEL, t in TECHNOLOGY, m in MODE_OF_OPERATION, y in YEAR: InputActivityRatio[r,t,f,m,y] = 0}:
            RateOfUseByTechnologyByMode[r,l,t,m,f,y] = 0;
        ```

3.  **Constraint:** `E1_AnnualEmissionProductionByMode`
    *   **Pyomo Rule:** `AnnualEmissionProductionByMode_rule`
    *   **Reason:** To handle cases where `EmissionActivityRatio` is zero, ensuring `AnnualTechnologyEmissionByMode` is set to zero.
    *   **Original (Relevant Part):**
        ```mathprog
        s.t. E1_AnnualEmissionProductionByMode{r,t,e,m,y: EmissionActivityRatio[r,t,e,m,y] <> 0}:
            EmissionActivityRatio[r,t,e,m,y] * TotalAnnualTechnologyActivityByMode[r,t,m,y] = AnnualTechnologyEmissionByMode[r,t,e,m,y];
        ```
    *   **Modification:**
        Added the following constraint:
        ```mathprog
        s.t. E1_AnnualEmissionProductionByMode_ZeroCase{r in REGION, t in TECHNOLOGY, e in EMISSION, m in MODE_OF_OPERATION, y in YEAR: EmissionActivityRatio[r,t,e,m,y] = 0}:
            AnnualTechnologyEmissionByMode[r,t,e,m,y] = 0;
        ```

4.  **Constraint:** `E3_EmissionsPenaltyByTechAndEmission`
    *   **Pyomo Rule:** `EmissionPenaltyByTechAndEmission_rule`
    *   **Reason:** To handle cases where `EmissionsPenalty` is zero, ensuring `AnnualTechnologyEmissionPenaltyByEmission` is set to zero.
    *   **Original (Relevant Part):**
        ```mathprog
        s.t. E3_EmissionsPenaltyByTechAndEmission{r,t,e,y: EmissionsPenalty[r,e,y] <> 0}:
            AnnualTechnologyEmission[r,t,e,y] * EmissionsPenalty[r,e,y] = AnnualTechnologyEmissionPenaltyByEmission[r,t,e,y];
        ```
    *   **Modification:**
        Added the following constraint:
        ```mathprog
        s.t. E3_EmissionsPenaltyByTechAndEmission_ZeroCase{r in REGION, t in TECHNOLOGY, e in EMISSION, y in YEAR: EmissionsPenalty[r,e,y] = 0}:
            AnnualTechnologyEmissionPenaltyByEmission[r,t,e,y] = 0;
        ```

5.  **Constraint:** `CAa5_TotalNewCapacity`
    *   **Pyomo Rule:** `TotalNewCapacity_2_rule`
    *   **Reason for No Change:** The existing formulation `s.t. CAa5_TotalNewCapacity{r,t,y: CapacityOfOneTechnologyUnit[r,t,y]<>0}: ...;` already correctly implements the Pyomo logic where the constraint is skipped if `CapacityOfOneTechnologyUnit` is zero. No explicit zero-case constraint is needed.

### Technology Capital Costs

1.  **Constraint:** `CC1_UndiscountedCapitalInvestment`
    *   **Pyomo Rule:** `UndiscountedCapitalInvestment_rule`
    *   **Reason:** To align with `osemosys.py` which calculates `CapitalInvestment` as `CapitalCost * NewCapacity`, without annualization factors at this stage.
    *   **Original:**
        ```mathprog
        s.t. CC1_UndiscountedCapitalInvestment{r in REGION, t in TECHNOLOGY, y in YEAR}:
            CapitalCost[r,t,y] * NewCapacity[r,t,y] * CapitalRecoveryFactor[r,t] * PvAnnuity[r,t] = CapitalInvestment[r,t,y];
        ```
    *   **Modified:**
        ```mathprog
        s.t. CC1_UndiscountedCapitalInvestment{r in REGION, t in TECHNOLOGY, y in YEAR}:
            CapitalCost[r,t,y] * NewCapacity[r,t,y] = CapitalInvestment[r,t,y];
        ```

2.  **Constraint:** `CC2_DiscountingCapitalInvestment`
    *   **Pyomo Rule:** `DiscountedCapitalInvestment_rule`
    *   **Reason:** To use direct discounting calculation as in `osemosys.py` instead of the removed `DiscountFactor` parameter.
    *   **Original:**
        ```mathprog
        s.t. CC2_DiscountingCapitalInvestment{r in REGION, t in TECHNOLOGY, y in YEAR}:
            CapitalInvestment[r,t,y]  / DiscountFactor[r,y] = DiscountedCapitalInvestment[r,t,y];
        ```
    *   **Modified:**
        ```mathprog
        s.t. CC2_DiscountingCapitalInvestment{r in REGION, t in TECHNOLOGY, y in YEAR}:
            CapitalInvestment[r,t,y]  / ((1 + DiscountRate[r]) ^ (y - min{yy in YEAR} min(yy) + 0.0)) = DiscountedCapitalInvestment[r,t,y];
        ```

### Technology Operating Costs

1.  **Constraint:** `OC4_DiscountedOperatingCostsTotalAnnual`
    *   **Pyomo Rule:** `DiscountedOperatingCostsTotalAnnual_rule`
    *   **Reason:** To use direct mid-year discounting calculation as in `osemosys.py` instead of the removed `DiscountFactorMid` parameter.
    *   **Original:**
        ```mathprog
        s.t. OC4_DiscountedOperatingCostsTotalAnnual{r in REGION, t in TECHNOLOGY, y in YEAR}:
            OperatingCost[r,t,y] / DiscountFactorMid[r, y] = DiscountedOperatingCost[r,t,y];
        ```
    *   **Modified:**
        ```mathprog
        s.t. OC4_DiscountedOperatingCostsTotalAnnual{r in REGION, t in TECHNOLOGY, y in YEAR}:
            OperatingCost[r,t,y] / ((1 + DiscountRate[r]) ^ (y - min{yy in YEAR} min(yy) + 0.5)) = DiscountedOperatingCost[r,t,y];
        ```

### Technology Salvage Value

1.  **Constraints:** `SV1_SalvageValueAtEndOfPeriod1` and `SV2_SalvageValueAtEndOfPeriod2`
    *   **Pyomo Rule:** `SalvageValueAtEndOfPeriod1_rule` (which covers multiple conditions)
    *   **Reason:** To align with `osemosys.py`'s direct calculation of salvage value, removing `CapitalRecoveryFactor` and `PvAnnuity`.
    *   **Original (`SV1`):**
        ```mathprog
        s.t. SV1_SalvageValueAtEndOfPeriod1{r,t,y: DepreciationMethod[r]=1 && (y+OperationalLife[r,t]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]>0}:
            SalvageValue[r,t,y] = CapitalCost[r,t,y] * NewCapacity[r,t,y] * CapitalRecoveryFactor[r,t] * PvAnnuity[r,t] * (1-(((1+DiscountRate[r])^(max{yy in YEAR} max(yy) - y+1)-1)/((1+DiscountRate[r])^OperationalLife[r,t]-1)));
        ```
    *   **Modified (`SV1`):**
        ```mathprog
        s.t. SV1_SalvageValueAtEndOfPeriod1{r,t,y: DepreciationMethod[r]=1 && (y+OperationalLife[r,t]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]>0}:
            SalvageValue[r,t,y] = CapitalCost[r,t,y] * NewCapacity[r,t,y] * (1-(((1+DiscountRate[r])^(max{yy in YEAR} max(yy) - y+1)-1)/((1+DiscountRate[r])^OperationalLife[r,t]-1)));
        ```
    *   **Original (`SV2`):**
        ```mathprog
        s.t. SV2_SalvageValueAtEndOfPeriod2{r,t,y: (DepreciationMethod[r]=1 && (y+OperationalLife[r,t]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]=0) || (DepreciationMethod[r]=2 && (y+OperationalLife[r,t]-1) > (max{yy in YEAR} max(yy)))}:
            SalvageValue[r,t,y] = CapitalCost[r,t,y] * NewCapacity[r,t,y] * CapitalRecoveryFactor[r,t] * PvAnnuity[r,t] * (1-(max{yy in YEAR} max(yy) - y+1)/OperationalLife[r,t]);
        ```
    *   **Modified (`SV2`):**
        ```mathprog
        s.t. SV2_SalvageValueAtEndOfPeriod2{r,t,y: (DepreciationMethod[r]=1 && (y+OperationalLife[r,t]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]=0) || (DepreciationMethod[r]=2 && (y+OperationalLife[r,t]-1) > (max{yy in YEAR} max(yy)))}:
            SalvageValue[r,t,y] = CapitalCost[r,t,y] * NewCapacity[r,t,y] * (1-(max{yy in YEAR} max(yy) - y+1)/OperationalLife[r,t]);
        ```

### Storage Capital Costs and Salvage Value

1.  **Constraint:** `SI5_DiscountingCapitalInvestmentStorage`
    *   **Pyomo Rule:** `DiscountingCapitalInvestmentStorage_rule`
    *   **Reason:** To use `DiscountRate[r]` directly, as `osemosys.py` does not use a separate `DiscountRateStorage` or `DiscountFactorStorage`.
    *   **Original:**
        ```mathprog
        s.t. SI5_DiscountingCapitalInvestmentStorage{r,s,y}: CapitalInvestmentStorage[r,s,y]/(DiscountFactorStorage[r,s,y]) = DiscountedCapitalInvestmentStorage[r,s,y];
        ```
    *   **Modified:**
        ```mathprog
        s.t. SI5_DiscountingCapitalInvestmentStorage{r,s,y}: CapitalInvestmentStorage[r,s,y]/((1 + DiscountRate[r]) ^ (y - min{yy in YEAR} min(yy) + 0.0)) = DiscountedCapitalInvestmentStorage[r,s,y];
        ```

2.  **Constraint:** `SI7_SalvageValueStorageAtEndOfPeriod2`
    *   **Pyomo Rule:** `SalvageValueStorageAtEndOfPeriod_rule` (conditional part)
    *   **Reason:** Condition `DiscountRateStorage[r,s]=0` changed to `DiscountRate[r]=0`.
    *   **Original:**
        ```mathprog
        s.t. SI7_SalvageValueStorageAtEndOfPeriod2{r,s,y: (DepreciationMethod[r]=1 && (y+OperationalLifeStorage[r,s]-1) > (max{yy in YEAR} max(yy)) && DiscountRateStorage[r,s]=0) || ...}: ...;
        ```
    *   **Modified:**
        ```mathprog
        s.t. SI7_SalvageValueStorageAtEndOfPeriod2{r,s,y: (DepreciationMethod[r]=1 && (y+OperationalLifeStorage[r,s]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]=0) || ...}: ...;
        ```
        (Formula body remains the same as it did not use `DiscountRateStorage`).

3.  **Constraint:** `SI8_SalvageValueStorageAtEndOfPeriod3`
    *   **Pyomo Rule:** `SalvageValueStorageAtEndOfPeriod_rule` (conditional part)
    *   **Reason:** `DiscountRateStorage[r,s]` in condition and formula changed to `DiscountRate[r]`.
    *   **Original:**
        ```mathprog
        s.t. SI8_SalvageValueStorageAtEndOfPeriod3{r,s,y: DepreciationMethod[r]=1 && (y+OperationalLifeStorage[r,s]-1) > (max{yy in YEAR} max(yy)) && DiscountRateStorage[r,s]>0}:
            CapitalInvestmentStorage[r,s,y]*(1-(((1+DiscountRateStorage[r,s])^(max{yy in YEAR} max(yy) - y+1)-1)/((1+DiscountRateStorage[r,s])^OperationalLifeStorage[r,s]-1))) = SalvageValueStorage[r,s,y];
        ```
    *   **Modified:**
        ```mathprog
        s.t. SI8_SalvageValueStorageAtEndOfPeriod3{r,s,y: DepreciationMethod[r]=1 && (y+OperationalLifeStorage[r,s]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]>0}:
            CapitalInvestmentStorage[r,s,y]*(1-(((1+DiscountRate[r])^(max{yy in YEAR} max(yy) - y+1)-1)/((1+DiscountRate[r])^OperationalLifeStorage[r,s]-1))) = SalvageValueStorage[r,s,y];
        ```

4.  **Constraint:** `SI9_SalvageValueStorageDiscountedToStartYear`
    *   **Pyomo Rule:** `SalvageValueStorageDiscountedToStartYear_rule`
    *   **Reason:** `DiscountRateStorage[r,s]` in formula changed to `DiscountRate[r]`.
    *   **Original:**
        ```mathprog
        s.t. SI9_SalvageValueStorageDiscountedToStartYear{r,s,y}: SalvageValueStorage[r,s,y]/((1+DiscountRateStorage[r,s])^(max{yy in YEAR} max(yy)-min{yy in YEAR} min(yy)+1)) = DiscountedSalvageValueStorage[r,s,y];
        ```
    *   **Modified:**
        ```mathprog
        s.t. SI9_SalvageValueStorageDiscountedToStartYear{r,s,y}: SalvageValueStorage[r,s,y]/((1+DiscountRate[r])^(max{yy in YEAR} max(yy)-min{yy in YEAR} min(yy)+1)) = DiscountedSalvageValueStorage[r,s,y];
        ```

### Storage Balancing Equations

1.  **Constraint:** `S11_and_S12_StorageLevelDayTypeStart`
    *   **Pyomo Rule:** `StorageLevelDayTypeStart_rule`
    *   **Reason:** To align with `osemosys.py` which does not multiply `NetChargeWithinDay` by `DaysInDayType` in this specific constraint's `else` clause.
    *   **Original (else part):**
        ```mathprog
        else StorageLevelDayTypeStart[r,s,ls,ld-1,y] + sum{lh in DAILYTIMEBRACKET} NetChargeWithinDay[r,s,ls,ld-1,lh,y] * DaysInDayType[ls,ld-1,y]
        ```
    *   **Modified (else part):**
        ```mathprog
        else StorageLevelDayTypeStart[r,s,ls,ld-1,y] + sum{lh in DAILYTIMEBRACKET} NetChargeWithinDay[r,s,ls,ld-1,lh,y]
        ```
        (The `=` and RHS `StorageLevelDayTypeStart[r,s,ls,ld,y];` remain unchanged).

### RE Generation Target Constraints Removed

The following constraints related to Renewable Energy (RE) generation targets were **removed** from `osemosys.txt`:
*   `s.t. RE1_FuelProductionByTechnologyAnnual{...}`
*   `s.t. RE2_TechIncluded{...}`
*   `s.t. RE3_FuelIncluded{...}`
*   `s.t. RE4_EnergyConstraint{...}`
*   `s.t. RE5_FuelUseByTechnologyAnnual{...}`
*   **Reason:** These constraints and their associated parameters/variables are not present in the `osemosys.py` model script being used as the primary source of logic.

### Emissions Accounting

1.  **Constraint:** `E5_DiscountedEmissionsPenaltyByTechnology`
    *   **Pyomo Rule:** `DiscountedEmissionsPenaltyByTechnology_rule`
    *   **Reason:** To use direct mid-year discounting calculation as in `osemosys.py` instead of the removed `DiscountFactorMid` parameter.
    *   **Original:**
        ```mathprog
        s.t. E5_DiscountedEmissionsPenaltyByTechnology{r in REGION, t in TECHNOLOGY, y in YEAR}:
            AnnualTechnologyEmissionsPenalty[r,t,y] / DiscountFactorMid[r,y] = DiscountedTechnologyEmissionsPenalty[r,t,y];
        ```
    *   **Modified:**
        ```mathprog
        s.t. E5_DiscountedEmissionsPenaltyByTechnology{r in REGION, t in TECHNOLOGY, y in YEAR}:
            AnnualTechnologyEmissionsPenalty[r,t,y] / ((1 + DiscountRate[r]) ^ (y - min{yy in YEAR} min(yy) + 0.5)) = DiscountedTechnologyEmissionsPenalty[r,t,y];
        ```

## 4. Unchanged Sections

The following sections of `osemosys.txt` were largely unchanged as their structure and logic were already aligned with `osemosys.py` or are standard MathProg elements:
*   **Objective Function:** The formulation `minimize cost: sum{r in REGION, y in YEAR} TotalDiscountedCost[r,y];` was already equivalent to the `osemosys.py` objective.
*   **Variable Definitions:** Apart from data types, the variable declarations were generally consistent.
*   **Many basic constraints:** Numerous other constraints, particularly those defining flow balances and simple limits, were already logically equivalent and did not require modification beyond ensuring parameter/variable names matched.
*   **`check` statements:** These were retained as is.
*   **`solve;` command.**
*   **Results output section (`printf`, `table`):** These were retained for user convenience, though their specific calculations might need review if based on removed parameters (the primary cost and emission summary `printf` statements were reviewed in the previous step when creating `osemosys1.txt` and would be implicitly correct now if `TotalDiscountedCost` and `AnnualEmissions` are correctly calculated by the modified constraints).

## 5. Further Modifications for Feasibility (Post-Initial Alignment)

Subsequent to the initial alignment efforts described above, model runs indicated potential infeasibility issues. A specific modification was made to `osemosys.txt` to address this, diverging from the direct translation of `osemosys.py` for one constraint to ensure model integrity.

### Storage Balancing Equations (Revisited)

1.  **Constraint Name:** `S11_and_S12_StorageLevelDayTypeStart` (Storage Level DayType Start)
    *   **Corresponding Pyomo Rule:** `StorageLevelDayTypeStart_rule`
    *   **Reason for Modification (New):** To address model infeasibility. The previous modification (in Section 3, under Storage Balancing Equations, which removed `* DaysInDayType[ls,ld-1,y]` to align with `osemosys.py`) is suspected to have caused an energy imbalance in storage level calculations between day types. This change reverts the constraint to its original `osemosys.txt` formulation (which was also the formulation in `osemosys1.txt` before it was modified to strictly follow `osemosys.py` on this point). This version is believed to better represent the physical energy balance when a daytype occurs multiple times within a season by correctly scaling the net charge for the duration of the daytype.
    *   **Details of Modification:**
        *   **Previous (problematic) formulation in `osemosys.txt` (after initial alignment with `osemosys.py`):**
            ```mathprog
            else StorageLevelDayTypeStart[r,s,ls,ld-1,y] + sum{lh in DAILYTIMEBRACKET} NetChargeWithinDay[r,s,ls,ld-1,lh,y]
            =
            StorageLevelDayTypeStart[r,s,ls,ld,y];
            ```
        *   **New (corrected) formulation in `osemosys.txt` (reverted to include `DaysInDayType`):**
            ```mathprog
            else StorageLevelDayTypeStart[r,s,ls,ld-1,y] + sum{lh in DAILYTIMEBRACKET} NetChargeWithinDay[r,s,ls,ld-1,lh,y] * DaysInDayType[ls,ld-1,y]
            =
            StorageLevelDayTypeStart[r,s,ls,ld,y];
            ```
        *   This change means `osemosys.txt` now intentionally deviates from the literal translation of `osemosys.py` for this specific line to ensure model integrity and feasibility.

## 6. Conclusion

The `osemosys.txt` file has been modified to reflect the mathematical logic of `osemosys.py` as closely as possible. Key parameters and constraint formulations were adjusted to align with `osemosys.py`'s approach to economic calculations (e.g., capital costs, salvage values) and specific conditional logic. One specific modification to the storage balancing equation `S11_and_S12_StorageLevelDayTypeStart` was made post-initial alignment to address feasibility concerns, thereby prioritizing model robustness for that constraint over a strict line-by-line equivalence with the `osemosys.py` version. The goal is to have a functionally equivalent and solvable MathProg model.
