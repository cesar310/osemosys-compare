""" MODELO

OSeMOSYS: Open Source energy MOdeling SYStem

============================================================================

  Copyright [2010-2015] [OSeMOSYS Forum steering committee see: www.osemosys.org]

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
  limitations under the License.
"""

             			#########################################
#####################			Model Definition				#############
             			#########################################

from __future__ import division
from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory

model = AbstractModel()

###############
#    Sets     #
###############

model.YEAR = Set() # (y) It represents the time frame of the model, it contains all the years to be considered in the study.
model.TECHNOLOGY = Set() # (t) It includes any element of the energy system that changes a commodity from one form to
#another, uses it or supplies it. All system components are set up as a ‘technology’ in OSeMOSYS. As the model is 
# an abstraction, the modeller is free to interpret the role of a technology at will, where relevant. It may for 
# example represent a single real technology (such as a power plant) or can represent a heavily aggregated collection
#  of technologies (such as the stock of several #million light bulbs), or may even simply be a ‘dummy technology’, 
# perhaps used for accounting purposes.
model.TIMESLICE = Set() # (l) It represents the time split of each modelled year, therefore the time resolution of the model.
# Common to several energy systems modelling tools (incl. MESSAGE/ MARKAL/ TIMES), the
# annual demand is ‘sliced’ into representative fractions of the year. It is necessary to assess times
# of the year when demand is high separately from times when demand is low, for fuels that are
# expensive to store. In order to reduce the computation time, these ‘slices’ are often grouped.
# Thus, the annual demand may be split into aggregate seasons where demand levels are similar
# (such as ‘summer, winter and intermediate’). Those seasons may be subdivided into aggregate
# ‘day types’ (such as workdays and weekends), and the day further sub divided (such as into day
# and night) depending on the level of demand.
model.FUEL = Set() # (f) It includes any energy vector, energy service or proxies entering or exiting technologies. These
# can be aggregate groups, individual flows or artificially separated, depending on the requirements of the analysis.
model.EMISSION = Set() # (e) It includes any kind of emission potentially deriving from the operation of the defined
# technologies. Typical examples would include atmospheric emissions of greenhouse gasses, such as CO2
model.MODE_OF_OPERATION = Set() #(m) It defines the number of modes of operation that the technologies can have. 
 # If a technology can have various input or output fuels and it can choose the mix (i.e. any linear combination) of
# these input or output fuels, each mix can be accounted as a separate mode of operation. For  example, a CHP plant 
# may produce heat in one mode of operation and electricity in another.
model.REGION = Set() #(r)  It sets the regions to be modelled, e.g. different countries. For each of them, the supply-demand
# balances for all the energy vectors are ensured, including trades with other regions. In some
# occasions it might be computationally more convenient to model different countries within the
# same region and differentiate them simply by creating ad hoc fuels and technologies for each of them.
model.SEASON = Set() #(ls) It gives indication (by successive numerical values) of how many seasons (e.g. winter,
# intermediate, summer) are accounted for and in which order. This set is needed if storage facilities are included in the model.
model.DAYTYPE = Set() #(ld) It gives indication (by successive numerical values) of how many day types (e.g. workday,
# weekend) are accounted for and in which order. This set is needed if storage facilities are included in the model.
model.DAILYTIMEBRACKET = Set() #(lh)  It gives indication (by successive numerical values) of how many parts the day 
# is split into (e.g. night, morning, afternoon, evening) and in which order these parts are sorted. This set is needed if storage facilities are included in the model.
model.FLEXIBLEDEMANDTYPE = Set() #NEW
model.STORAGE = Set() # It includes storage facilities in the model.

#####################
#    Parameters     #
#####################

########			Global 						#############

model.YearSplit = Param(model.TIMESLICE, model.YEAR) #Duration of a modelled time slice, expressed as a fraction of the
# year. The sum of each entry over one modelled year should equal 1.
model.DiscountRate = Param(model.REGION, default=0.05) #Region specific value for the discount rate, expressed in decimals (e.g. 0.05 to indicate 5%)
model.DaySplit = Param(model.DAILYTIMEBRACKET, model.YEAR, default=0.00137) #Length of one DailyTimeBracket in one
# specific day as a fraction of the year (e.g., when distinguishing between days and night: 12h/(24h*365d)).
model.Conversionls = Param(model.TIMESLICE, model.SEASON, default=0) #Binary parameter linking one TimeSlice to a 
# certain Season. It has value 0 if the TimeSlice does not pertain to the specific season, 1 if it does.
model.Conversionld = Param(model.TIMESLICE, model.DAYTYPE, default=0) #Binary parameter linking one TimeSlice to a 
# certain DayType. It has value 0 if the TimeSlice does not pertain to the specific DayType, 1 if it does.
model.Conversionlh = Param(model.TIMESLICE, model.DAILYTIMEBRACKET, default=0) #Binary parameter linking one TimeSlice
# to a certain DaylyTimeBracket. It has value 0 if the TimeSlice does not pertain to the specific DaylyTimeBracket, 1 if it does.
model.DaysInDayType = Param(model.SEASON, model.DAYTYPE, model.YEAR, default=7) #Number of days for each day type,
# within one week (natural number, ranging from 1 to 7). 
model.TradeRoute = Param(model.REGION, model.REGION, model.FUEL, model.YEAR, default=0) #Binary parameter defining the
#links between region r and region rr, to enable or disable trading of a specific commodity. It has value 1 when two regions are linked, 0 otherwise
model.DepreciationMethod = Param(model.REGION, default=1) # Binary parameter defining the type of depreciation to be
#  applied. It has value 1 for sinking fund depreciation, value 2 for straight-line depreciation.

########			Demands 					#############

model.SpecifiedAnnualDemand = Param(model.REGION, model.FUEL, model.YEAR, default=0) #Total specified demand for the year.
model.SpecifiedDemandProfile = Param(model.REGION, model.FUEL, model.TIMESLICE, model.YEAR, default=0) #Annual fraction
# of energy-service or commodity demand that is required in each time slice. For each year, all the defined 
# SpecifiedDemandProfile input values should sum up to 1.
model.AccumulatedAnnualDemand = Param(model.REGION, model.FUEL, model.YEAR, default=0)#Accumulated Demand for a certain
# commodity in one specific year. It cannot be defined for a commodity if its SpecifiedAnnualDemand for the same year 
# is already defined and vice versa.

#########			Performance					#############

model.CapacityToActivityUnit = Param(model.REGION, model.TECHNOLOGY, default=1) #Conversion factor expressing the energy
#that would be produced when one unit of capacity is fully used in one year.
model.CapacityFactor = Param(model.REGION, model.TECHNOLOGY, model.TIMESLICE, model.YEAR, default=1) #Capacity available
# each TimeSlice expressed as a fraction of the total installed capacity, ranging from 0 to 1. It gives the possibility 
# to account for the forced outages.
model.AvailabilityFactor = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=1) #Maximum time a technology can
# run in the whole year, as a fraction of the year, ranging from 0 to 1. It gives the possibility to account for planned 
# outages.
model.OperationalLife = Param(model.REGION, model.TECHNOLOGY, default=1) #Useful lifetime of a technology, expressed in years.
model.ResidualCapacity = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0) #Capacity available from before the modelling period.
model.InputActivityRatio = Param(model.REGION,model.TECHNOLOGY,model.FUEL,model.MODE_OF_OPERATION,model.YEAR,default=0)  #Rate of fuel input (use) to a technology as a ratio of the rate of activity.
# Rate of fuel input (use) to a technology as a ratio of the rate of activity.
model.OutputActivityRatio = Param(model.REGION,model.TECHNOLOGY,model.FUEL,model.MODE_OF_OPERATION,model.YEAR,default=0)
# Rate of fuel output of a technology as a ratio of the rate of activity.
#########			Technology Costs			#############

model.CapitalCost = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0.000001) #Capital investment cost 
# of a technology, per unit of capacity.
model.VariableCost = Param(model.REGION,model.TECHNOLOGY,model.MODE_OF_OPERATION,model.YEAR,
    default=0.000001,
) #Cost of a technology for a given mode of operation (Variable O&M cost), per unit of activity.
model.FixedCost = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0)
# Fixed O&M cost of a technology, per unit of capacity.

#########           		Storage                 		#############

model.TechnologyToStorage = Param(
    model.REGION, model.TECHNOLOGY, model.STORAGE, model.MODE_OF_OPERATION, default=0
)#Binary parameter linking a technology to the storage facility it charges. 
# It has value 1 if the technology  and the storage facility are linked, 0 otherwise.
model.TechnologyFromStorage = Param(
    model.REGION, model.TECHNOLOGY, model.STORAGE, model.MODE_OF_OPERATION, default=0
) #Binary parameter linking a storage facility to the technology it feeds. It has 
# value 1 if the technology and the storage facility are linked, 0 otherwise.

model.StorageLevelStart = Param(model.REGION, model.STORAGE, default=0.0000001)# Level
#  of storage at the beginning of the first modelled year, in units of activity.

model.StorageMaxChargeRate = Param(model.REGION, model.STORAGE, default=99999) #Maximum
# charging rate for a storage facility, in units of activity per year.

model.StorageMaxDischargeRate = Param(model.REGION, model.STORAGE, default=99999)#Maximum 
# discharging rate for a storage facility, in units of activity per year.

model.MinStorageCharge = Param(model.REGION, model.STORAGE, model.YEAR, default=0)
#Lower bound to the amount of energy stored, as a fraction of the maximum, ranging between 0 and 1.
#The storage facility cannot be emptied below this level.

model.OperationalLifeStorage = Param(model.REGION, model.STORAGE, default=0) #Useful lifetime of a storage facility.
model.CapitalCostStorage = Param(model.REGION, model.STORAGE, model.YEAR, default=0) #Capital investment cost of a 
#storage facility, per unit of energy.
model.ResidualStorageCapacity = Param(model.REGION, model.STORAGE, model.YEAR, default=0) #Storage capacity available
# from before the modelling period.

#########			Capacity Constraints		#############

model.CapacityOfOneTechnologyUnit = Param(
    model.REGION, model.TECHNOLOGY, model.YEAR, default=0
)# Capacity of one new unit of a technology. In case the user sets this parameter, the related technology will
# be installed only in batches of the specified capacity and the problem will turn into a Mixed Integer Linear Problem.
model.TotalAnnualMaxCapacity = Param(
    model.REGION, model.TECHNOLOGY, model.YEAR, default=99999
)#Total maximum existing (residual plus cumulatively installed) capacity allowed for a technology in a specified year.
model.TotalAnnualMinCapacity = Param(
    model.REGION, model.TECHNOLOGY, model.YEAR, default=0
)#Total minimum existing (residual plus cumulatively installed) capacity allowed for a technology in a specified year.

#########			Investment Constraints		#############

model.TotalAnnualMaxCapacityInvestment = Param(
    model.REGION, model.TECHNOLOGY, model.YEAR, default=99999
)#Maximum capacity of a technology allowed to be newly installed in the specified year, expressed in power units.
model.TotalAnnualMinCapacityInvestment = Param(
    model.REGION, model.TECHNOLOGY, model.YEAR, default=0
)#Minimum capacity of a technology allowed to be newly installed in the specified year, expressed in power units

#########			Activity Constraints		#############

model.TotalTechnologyAnnualActivityUpperLimit = Param(
    model.REGION, model.TECHNOLOGY, model.YEAR, default=99999
)#Total maximum level of activity allowed for a technology in one year.
model.TotalTechnologyAnnualActivityLowerLimit = Param(
    model.REGION, model.TECHNOLOGY, model.YEAR, default=0
)#Total minimum level of activity allowed for a technology in one year.
model.TotalTechnologyModelPeriodActivityUpperLimit = Param(
    model.REGION, model.TECHNOLOGY, default=99999
)#Total maximum level of activity allowed for a technology in the entire modelled period.
model.TotalTechnologyModelPeriodActivityLowerLimit = Param(
    model.REGION, model.TECHNOLOGY, default=0
)#Total minimum level of activity allowed for a technology in the entire modelled period.

#########			Reserve Margin				#############

model.ReserveMarginTagTechnology = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0) #Binary parameter to tag
# the technologies which are allowed to contribute to the reserve margin. It has value 0 if a technology is not allowed, 1 if it is
model.ReserveMarginTagFuel = Param(model.REGION, model.FUEL, model.YEAR, default=0) #Binary parameter to tag the fuels
#  to which the reserve margin applies. It has value 0 if the reserve margin does not apply to the fuel, 1 if it does.
model.ReserveMargin = Param(model.REGION, model.YEAR, default=1) #Minimum level of the reserve margin required to be
# provided for all the tagged commodities, by the tagged technologies. If no reserve margin is required, the parameter 
# will have value 1; if, for instance, 20% reserve margin is required, the parameter will have value 1.2.

#########			RE Generation Target		#############

model.RETagTechnology = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0) #Binary parameter to tag the 
# renewable technologies which must contribute to reaching the indicated minimum renewable production target set in the
# model. It has value 1 for the tagged technologies, 0 otherwise.
model.RETagFuel = Param(model.REGION, model.FUEL, model.YEAR, default=0) #Binary parameter to tag the fuels contributing
# to reaching the renewable target. It has value 1 for the tagged commodities, 0 otherwise
model.REMinProductionTarget = Param(model.REGION, model.YEAR, default=0) #Minimum ratio of all renewable fuels tagged in
# the RETagFuel parameter, to be produced by the technologies tagged with the RETagTechnology parameter

#########			Emissions & Penalties		#############

model.EmissionActivityRatio = Param(model.REGION,model.TECHNOLOGY,model.EMISSION,model.MODE_OF_OPERATION,model.YEAR,
    default=0,
)#Emission factor of a technology per unit of activity, per mode of operation.
model.EmissionsPenalty = Param(model.REGION, model.EMISSION, model.YEAR, default=0) #Penalty per unit of emission.
model.AnnualExogenousEmission = Param(model.REGION, model.EMISSION, model.YEAR, default=0) #It allows the user to 
# account for additional annual emissions, on top of those computed endogenously by the model (e.g. emissions generated outside the region).
model.AnnualEmissionLimit = Param(model.REGION, model.EMISSION, model.YEAR, default=99999) #Annual upper limit for a 
#specific emission generated in the whole modelled region.
model.ModelPeriodExogenousEmission = Param(model.REGION, model.EMISSION, default=0) #It allows the user to account for 
# additional emissions over the entire modelled period, on top of those computed endogenously by the model (e.g. generated outside the region).
model.ModelPeriodEmissionLimit = Param(model.REGION, model.EMISSION, default=99999) #Annual upper limit for a specific 
# emission generated in the whole modelled region, over the entire modelled period.

######################
#   Model Variables  #
######################



########			Demands 					#############

model.RateOfDemand = Var(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Energy(per year)] : Intermediate variable. It represents the energy that would be demanded in one time slice l if the
# latter lasted the whole year. It is derived from the parameters SpecifiedAnnualDemand and SpecifiedDemandProfile.

model.Demand = Var(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Energy] : Demand for one fuel in one time slice.


########     		Storage                 		#############

model.RateOfStorageCharge = Var(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    domain=NonNegativeReals, #MODIFICADO DR
    initialize=0.0,
)#[Energy(per year)] :Intermediate variable. It represents the commodity that would be charged to storage facility s 
# in one time slice if the latter lasted the whole year. It is a function of the RateOfActivity and the parameter TechnologyToStorage.

model.RateOfStorageDischarge = Var(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    domain=NonNegativeReals, #MODIFICADO DR
    initialize=0.0,
)#[Energy(per year)] :Intermediate variable. It represents the commodity that would be discharged from storage facility s
# in one time slice if the latter lasted the whole year. It is a function of the RateOfActivity and the parameter TechnologyFromStorage.

model.NetChargeWithinYear = Var(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    domain=Reals, #MODIFICADO DR
    initialize=0.0,
)#[Energy] : Net quantity of commodity charged to storage facility s in year y. It is a function
# of the RateOfStorageCharge and the RateOfStorageDischarge and it can be negative.


model.NetChargeWithinDay = Var(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    domain=Reals, #MODIFICADO DR
    initialize=0.0,
)#[Energy] : Net quantity of commodity charged to storage facility s in daytype ld. It is a function of the 
# RateOfStorageCharge and the RateOfStorageDischarge and it can be negative.

model.StorageLevelYearStart = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[Energy] :Level of stored commodity in storage facility s in the first instance of year y.


model.StorageLevelYearFinish = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#Level of stored commodity in storage facility s in the last instance time step of year y.


model.StorageLevelSeasonStart = Var(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)# [Energy] Level of stored commodity in storage facility s in the first instance of season ls.

model.StorageLevelDayTypeStart = Var(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
) # [Energy]Level of stored commodity in storage facility s in the first instance of daytype ld.
model.StorageLevelDayTypeFinish = Var(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)# [Energy] Level of stored commodity in storage facility s in the last of daytype ld.

model.StorageLowerLimit = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)# [Energy] Minimum allowed level of stored commodity in storage facility s, as a function of
# the storage capacity and the user-defined MinStorageCharge ratio.

model.StorageUpperLimit = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)# [Energy] Maximum allowed level of stored commodity in storage facility s. It corresponds
# to the total existing capacity of storage facility s (summing newly installed and pre-existing capacities).

model.AccumulatedNewStorageCapacity = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)# [Energy] Cumulative capacity of newly installed storage from the beginning of the time domain to year y.

model.NewStorageCapacity = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
) # [Energy]  Capacity of newly installed storage in year y.

model.CapitalInvestmentStorage = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
) # [ Monetary units] Undiscounted investment in new capacity for storage facility s. Derived from the NewStorageCapacity 
# and the parameter CapitalCostStorage.
model.DiscountedCapitalInvestmentStorage = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units] Investment in new capacity for storage facility s, discounted through the parameter DiscountRate.
model.SalvageValueStorage = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units] Salvage value of storage facility s in year y, as a function of the parameters
# OperationalLifeStorage and DepreciationMethod.
model.DiscountedSalvageValueStorage = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units] Salvage value of storage facility s, discounted through the parameter DiscountRate
model.TotalDiscountedStorageCost = Var(
    model.REGION, model.STORAGE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units]: Difference between the discounted capital investment in new storage facilities
# and the salvage value in year y.

#########		    Capacity Variables 			#############

model.NumberOfNewTechnologyUnits = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeIntegers, initialize=0
) #Number of newly installed units of technology t in year y, as a function of the parameter CapacityOfOneTechnologyUnit.
model.NewCapacity = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
) # [Power] Newly installed capacity of technology t in year y.
model.AccumulatedNewCapacity = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
) # [Power]Cumulative newly installed capacity of technology t from the beginning of the time domain to year y.
model.TotalCapacityAnnual = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
) # [Power] Total existing capacity of technology t in year y (sum of cumulative newly
# installed and pre-existing capacity).

#########		    Activity Variables 			#############

model.RateOfActivity = Var(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.MODE_OF_OPERATION,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
) # [Energy (per year)]: Intermediate variable. It represents the activity of technology t in one MODE of
# operation and in time slice l, were the latter to last the whole year.
model.RateOfTotalActivity = Var(
    model.REGION,
    model.TECHNOLOGY,
    model.TIMESLICE,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
) # [Energy (per year)]: Sum of the RateOfActivity of a technology over the modes of operation.

model.TotalTechnologyAnnualActivity = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[Energy] : Total annual activity of technology t.

model.TotalAnnualTechnologyActivityByMode = Var(
    model.REGION,
    model.TECHNOLOGY,
    model.MODE_OF_OPERATION,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Energy] :Annual activity of technology t in mode of operation m.

model.RateOfProductionByTechnologyByMode = Var(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.MODE_OF_OPERATION,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)# [Energy (per year)]:Intermediate variable. It represents the quantity of fuel f which technology t
# would produce in one mode of operation and in time slice l, if the latter lasted
# the whole year. It is a function of the variable RateOfActivity and the parameter OutputActivityRatio.

model.RateOfProductionByTechnology = Var(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
) # [Energy (per year)]:Sum of the RateOfProductionByTechnologyByMode over the modes of operation.

model.ProductionByTechnology = Var(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Energy] :Production of fuel f by technology t in time slice l.
model.ProductionByTechnologyAnnual = Var(
    model.REGION,
    model.TECHNOLOGY,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Energy] :Annual production of fuel f by technology t.
model.RateOfProduction = Var(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Energy] :Sum of the RateOfProductionByTechnology over all the technologies.
model.Production = Var(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Energy] :Total production of fuel f in time slice l. It is the sum of the ProductionByTechnology over all technologies.
model.RateOfUseByTechnologyByMode = Var(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.MODE_OF_OPERATION,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)# [Energy (per year)]:Intermediate variable. It represents the quantity of fuel f which technology t
# would use in one mode of operation and in time slice l, if the latter lasted the whole year. It is the function of 
# the variable RateOfActivity and the parameter InputActivityRatio.
model.RateOfUseByTechnology = Var(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
) #[Energy (per year)]: Sum of the RateOfUseByTechnologyByMode over the modes of operation.

model.UseByTechnologyAnnual = Var(
    model.REGION,
    model.TECHNOLOGY,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)  #[Energy]:  Annual use of fuel f by technology t.

model.RateOfUse = Var(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
) #[Energy (per year)]:  Sum of the RateOfUseByTechnology over all the technologies.

model.UseByTechnology = Var(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Energy]: Use of fuel f by technology t in time slice l.
model.Use = Var(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Energy]: Total use of fuel f in time slice l. It is the sum of the UseByTechnology over all technologies.

model.Trade = Var(
    model.REGION, model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, initialize=0.0
)#[Energy]:Quantity of fuel f traded between region r and rr in time slice l.

model.TradeAnnual = Var(
    model.REGION, model.REGION, model.FUEL, model.YEAR, initialize=0.0
)#[Energy]: Annual quantity of fuel f traded between region r and rr. It is the sum of the
# variable Trade over all the time slices.

model.ProductionAnnual = Var(
    model.REGION, model.FUEL, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[Energy]: Total annual production of fuel f. It is the sum of the variable Production over all technologies.

model.UseAnnual = Var(
    model.REGION, model.FUEL, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[Energy]: Total annual use of fuel f. It is the sum of the variable Use over all technologies.


#########		    Costing Variables 			#############

model.CapitalInvestment = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units]:Undiscounted investment in new capacity of technology t. It is a function of the
# NewCapacity and the parameter CapitalCost.
model.DiscountedCapitalInvestment = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units]:Investment in new capacity of technology t, discounted through the parameter
# DiscountRate.

model.SalvageValue = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units]:Salvage value of technology t in year y, as a function of the parameters
# OperationalLife and DepreciationMethod.
model.DiscountedSalvageValue = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
) #[ Monetary units]:Salvage value of technology t, discounted through the parameter DiscountRate.
model.OperatingCost = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units]:Undiscounted sum of the annual variable and fixed operating costs of technology t.
model.DiscountedOperatingCost = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units]:Annual OperatingCost of technology t, discounted through the parameter DiscountRate

model.AnnualVariableOperatingCost = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units]:Annual variable operating cost of technology t. Derived from the
# TotalAnnualTechnologyActivityByMode and the parameter VariableCost.
model.AnnualFixedOperatingCost = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units]:Annual fixed operating cost of technology t. Derived from the TotalCapacityAnnual and the parameter FixedCost.
model.VariableOperatingCost = Var(
    model.REGION,
    model.TECHNOLOGY,
    model.TIMESLICE,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)

model.TotalDiscountedCostByTechnology = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)# [ Monetary units]: Difference between the sum of discounted operating cost/ capital cost/ emission penalties and the salvage value.
model.TotalDiscountedCost = Var(
    model.REGION, model.YEAR, domain=NonNegativeReals, initialize=0.0
) #[ Monetary units]:Sum of the TotalDiscountedCostByTechnology over all the technologies.

model.ModelPeriodCostByRegion = Var(
    model.REGION, domain=NonNegativeReals, initialize=0.0
)#[ Monetary units]:Sum of the TotalDiscountedCost over all the modelled years.

#########			Reserve Margin				#############

model.TotalCapacityInReserveMargin = Var(
    model.REGION, model.YEAR, domain=NonNegativeReals, initialize=0.0
) #[Energy] Total available capacity of the technologies required to provide reserve margin.
# It is derived from the TotalCapacityAnnual and the parameter ReserveMarginTagTechnology.
model.DemandNeedingReserveMargin = Var(
    model.REGION, model.TIMESLICE, model.YEAR, domain=NonNegativeReals, initialize=0.0
)# Quantity of produced fuel which is given a target of reserve margin. Derived
# from the RateOfProduction and the parameter ReserveMarginTagFuel.

#########			RE Gen Target				#############

model.TotalREProductionAnnual = Var(model.REGION, model.YEAR, initialize=0.0) # [Energy] Annual production by all technologies 
#tagged as renewable in the model. Derived from the ProductionByTechnologyAnnual and the parameter RETagTechnology.
model.RETotalProductionOfTargetFuelAnnual = Var(
    model.REGION, model.YEAR, initialize=0.0
) #[Energy]: Annual production of fuels tagged as renewable in the model. Derived from the
# RateOfProduction and the parameter RETagFuel.

model.TotalTechnologyModelPeriodActivity = Var(
    model.REGION, model.TECHNOLOGY, initialize=0.0
)#New

#########			Emissions					#############

model.AnnualTechnologyEmissionByMode = Var(
    model.REGION,
    model.TECHNOLOGY,
    model.EMISSION,
    model.MODE_OF_OPERATION,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Quantity of emission]: Annual emission of agent e by technology t in mode of operation m. Derived
# from the RateOfActivity and the parameter EmissionActivityRatio.
model.AnnualTechnologyEmission = Var(
    model.REGION,
    model.TECHNOLOGY,
    model.EMISSION,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Quantity of emission]: Sum of the AnnualTechnologyEmissionByMode over the modes of operation. 
model.AnnualTechnologyEmissionPenaltyByEmission = Var(
    model.REGION,
    model.TECHNOLOGY,
    model.EMISSION,
    model.YEAR,
    domain=NonNegativeReals,
    initialize=0.0,
)#[Monetary units]: Undiscounted annual cost of emission e by technology t. Product of the
# AnnualTechnologyEmission by the parameter EmissionPenalty.
model.AnnualTechnologyEmissionsPenalty = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
) #[Monetary units]: Total undiscounted annual cost of all emissions generatedby technology t. Sum
# of the AnnualTechnologyEmissionPenaltyByEmission over all the emitted agents.
model.DiscountedTechnologyEmissionsPenalty = Var(
    model.REGION, model.TECHNOLOGY, model.YEAR, domain=NonNegativeReals, initialize=0.0
)# [Monetary units]: Annual cost of emissions by technology t, discounted through the DiscountRate.
model.AnnualEmissions = Var(
    model.REGION, model.EMISSION, model.YEAR, domain=NonNegativeReals, initialize=0.0
)#[Quantity of emission]:Sum of the AnnualTechnologyEmission over all technologies
model.ModelPeriodEmissions = Var(
    model.REGION, model.EMISSION, domain=NonNegativeReals, initialize=0.0
)#[Quantity of emission]:Total system emissions of agent e in the model period, accounting for both the
# emissions by technologies and the user defined ModelPeriodExogenousEmission.


######################
# Objective Function #
######################


def ObjectiveFunction_rule(model):
    return sum(model.ModelPeriodCostByRegion[r] for r in model.REGION)
model.OBJ = Objective(rule=ObjectiveFunction_rule, sense=minimize)

# The objective of the model is to estimate the lowest net present value (NPV) cost of an energy system to meet
# given demand(s) for energy or energy services.


#####################
# Constraints       #
#####################


def SpecifiedDemand_rule(model, r, f, l, y):

    if model.SpecifiedAnnualDemand[r, f, y] > 0:  #Modificación David Romero con base en códigos GAMS y MathProg
        return (
            model.SpecifiedAnnualDemand[r, f, y]
            * model.SpecifiedDemandProfile[r, f, l, y]
            / model.YearSplit[l, y]
            == model.RateOfDemand[r, l, f, y]
    )
    else:
        return Constraint.Skip    #Modificación David Romero con base en códigos GAMS y MathProg
    


model.SpecifiedDemand = Constraint(
    model.REGION, model.FUEL, model.TIMESLICE, model.YEAR, rule=SpecifiedDemand_rule
) #  It represents the energy that would be demanded in one time slice l if the
# latter lasted the whole year. It is derived from the parameters SpecifiedAnnualDemand and SpecifiedDemandProfile.


#########       	Capacity Adequacy A	     	#############


def TotalNewCapacity_1_rule(model, r, t, y):
    return model.AccumulatedNewCapacity[r, t, y] == sum(
        model.NewCapacity[r, t, yy]
        for yy in model.YEAR
        if ((y - yy < model.OperationalLife[r, t]) and (y - yy >= 0))
    )


model.TotalNewCapacity_1 = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=TotalNewCapacity_1_rule
)


def TotalNewCapacity_2_rule(model, r, t, y):
    if model.CapacityOfOneTechnologyUnit[r, t, y] != 0:
        return (
            model.CapacityOfOneTechnologyUnit[r, t, y]
            * model.NumberOfNewTechnologyUnits[r, t, y]
            == model.NewCapacity[r, t, y]
        )
    else:
        return Constraint.Skip


model.TotalNewCapacity_2 = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=TotalNewCapacity_2_rule
)


def TotalAnnualCapacity_rule(model, r, t, y):
    return (
        model.AccumulatedNewCapacity[r, t, y] + model.ResidualCapacity[r, t, y]
        == model.TotalCapacityAnnual[r, t, y]
    )


model.TotalAnnualCapacity_constraint = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=TotalAnnualCapacity_rule
)


def TotalActivityOfEachTechnology_rule(model, r, t, l, y):
    return (
        sum(model.RateOfActivity[r, l, t, m, y] for m in model.MODE_OF_OPERATION)
        == model.RateOfTotalActivity[r, t, l, y]
    )


model.TotalActivityOfEachTechnology = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.TIMESLICE,
    model.YEAR,
    rule=TotalActivityOfEachTechnology_rule,
)


def ConstraintCapacity_rule(model, r, l, t, y):
    return (
        model.RateOfTotalActivity[r, t, l, y]
        <= model.TotalCapacityAnnual[r, t, y]
        * model.CapacityFactor[r, t, l, y]
        * model.CapacityToActivityUnit[r, t]
    )


model.ConstraintCapacity = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.YEAR,
    rule=ConstraintCapacity_rule,
)


#########       	Capacity Adequacy B		 	#############


def PlannedMaintenance_rule(model, r, t, y):
    return (
        sum(
            model.RateOfTotalActivity[r, t, l, y] * model.YearSplit[l, y]
            for l in model.TIMESLICE
        )
        <= sum(
            model.TotalCapacityAnnual[r, t, y]
            * model.CapacityFactor[r, t, l, y]
            * model.YearSplit[l, y]
            for l in model.TIMESLICE
        )
        * model.AvailabilityFactor[r, t, y]
        * model.CapacityToActivityUnit[r, t]
    )


model.PlannedMaintenance = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=PlannedMaintenance_rule
)


#########	        Energy Balance A    	 	#############


def RateOfFuelProduction1_rule(model, r, l, f, t, m, y):
    if model.OutputActivityRatio[r, t, f, m, y] != 0:
        return (
            model.RateOfProductionByTechnologyByMode[r, l, t, m, f, y]
            == model.RateOfActivity[r, l, t, m, y]
            * model.OutputActivityRatio[r, t, f, m, y]
        )
    else:
        return Constraint.Skip 


model.RateOfFuelProduction1 = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.TECHNOLOGY,
    model.MODE_OF_OPERATION,
    model.YEAR,
    rule=RateOfFuelProduction1_rule,
)



def RateOfFuelProduction2_rule(model, r, l, f, t, y):
    if sum(model.OutputActivityRatio[r, t, f, m, y] for m in model.MODE_OF_OPERATION)  !=0: # Modificado DR
        return model.RateOfProductionByTechnology[r, l, t, f, y] == sum(
            model.RateOfProductionByTechnologyByMode[r, l, t, m, f, y]
            for m in model.MODE_OF_OPERATION)
    else:
        return Constraint.Skip 


model.RateOfFuelProduction2 = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.TECHNOLOGY,
    model.YEAR,
    rule=RateOfFuelProduction2_rule,
)


def RateOfFuelProduction3_rule(model, r, l, f, y):
    return model.RateOfProduction[r, l, f, y] == sum(
        model.RateOfProductionByTechnology[r, l, t, f, y] for t in model.TECHNOLOGY 
        if sum(model.OutputActivityRatio[r, t, f, m, y] for t in model.TECHNOLOGY  for m in model.MODE_OF_OPERATION)  !=0 # Modificado DR
    )


# def RateOfFuelProduction3_rule(model, r, l, f, y):
#     if sum(model.OutputActivityRatio[r, t, f, m, y] for t in model.TECHNOLOGY  for m in model.MODE_OF_OPERATION)  !=0: # Modificado DR
#         return model.RateOfProduction[r, l, f, y] == sum(
#             model.RateOfProductionByTechnology[r, l, t, f, y] for t in model.TECHNOLOGY 
#         )
#     else:
#         return Constraint.Skip 

model.RateOfFuelProduction3 = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    rule=RateOfFuelProduction3_rule,
)


def RateOfFuelUse1_rule(model, r, l, f, t, m, y):
    if model.InputActivityRatio[r, t, f, m, y] != 0:   # Modificado DR
        return (
        model.RateOfActivity[r, l, t, m, y] * model.InputActivityRatio[r, t, f, m, y]
        == model.RateOfUseByTechnologyByMode[r, l, t, m, f, y]
        )
    else:
        return Constraint.Skip # Modificado DR

model.RateOfFuelUse1 = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.TECHNOLOGY,
    model.MODE_OF_OPERATION,
    model.YEAR,
    rule=RateOfFuelUse1_rule,
)


# def RateOfFuelUse2_rule(model, r, l, f, t, y):
#     return model.RateOfUseByTechnology[r, l, t, f, y] == sum(
#         model.RateOfUseByTechnologyByMode[r, l, t, m, f, y]
#         for m in model.MODE_OF_OPERATION
#         if model.InputActivityRatio[r, t, f, m, y] !=0   # Modificado DR
#     )

def RateOfFuelUse2_rule(model, r, l, f, t, y):
    if sum( model.InputActivityRatio[r, t, f, m, y] for m in model.MODE_OF_OPERATION) !=0:   # Modificado DR
        return model.RateOfUseByTechnology[r, l, t, f, y] == sum(
        model.RateOfUseByTechnologyByMode[r, l, t, m, f, y]
        for m in model.MODE_OF_OPERATION
    )
    else:
        return Constraint.Skip # Modificado DR



model.RateOfFuelUse2 = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.TECHNOLOGY,
    model.YEAR,
    rule=RateOfFuelUse2_rule,
)


def RateOfFuelUse3_rule(model, r, l, f, y):
    return (
        sum(model.RateOfUseByTechnology[r, l, t, f, y] for t in model.TECHNOLOGY
        if sum(model.InputActivityRatio[r, t, f, m, y] for t in model.TECHNOLOGY  for m in model.MODE_OF_OPERATION)  !=0 )# Modificado DR
        == model.RateOfUse[r, l, f, y]
    )   


# def RateOfFuelUse3_rule(model, r, l, f, y):
#     if sum(model.InputActivityRatio[r, t, f, m, y] for t in model.TECHNOLOGY  for m in model.MODE_OF_OPERATION)  !=0 :# Modificado DR
#         return (
#             sum(model.RateOfUseByTechnology[r, l, t, f, y] for t in model.TECHNOLOGY)
#             == model.RateOfUse[r, l, f, y]
#         )   
#     else:
#         return Constraint.Skip # Modificado DR

model.RateOfFuelUse3 = Constraint(
    model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=RateOfFuelUse3_rule
)


def EnergyBalanceEachTS1_rule(model, r, l, f, y):
    if sum(model.OutputActivityRatio[r, t, f, m, y] for t in model.TECHNOLOGY  for m in model.MODE_OF_OPERATION)  !=0:
        return (
            model.RateOfProduction[r, l, f, y] * model.YearSplit[l, y]
            == model.Production[r, l, f, y]
        )
    else:
        return model.Production[r, l, f, y]==0 
        # return Constraint.Skip # Modificado DR  


model.EnergyBalanceEachTS1 = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    rule=EnergyBalanceEachTS1_rule,
)


def EnergyBalanceEachTS2_rule(model, r, l, f, y):
    if sum(model.InputActivityRatio[r, t, f, m, y] for t in model.TECHNOLOGY  for m in model.MODE_OF_OPERATION)  !=0:
        return model.RateOfUse[r, l, f, y] * model.YearSplit[l, y] == model.Use[r, l, f, y]
    else:
        return (
            model.Use[r, l, f, y]==0 
        )     


model.EnergyBalanceEachTS2 = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    rule=EnergyBalanceEachTS2_rule,
)


def EnergyBalanceEachTS3_rule(model, r, l, f, y):
    if model.SpecifiedAnnualDemand[r, f, y] > 0:  #Modificación David Romero con base en códigos GAMS y MathProg
        return (
            model.RateOfDemand[r, l, f, y] * model.YearSplit[l, y]
            == model.Demand[r, l, f, y]
        )
    else:
        return Constraint.Skip    #Modificación David Romero con base en códigos GAMS y MathProg
    



model.EnergyBalanceEachTS3 = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    rule=EnergyBalanceEachTS3_rule,
)


def EnergyBalanceEachTS4_rule(model, r, rr, l, f, y):
    if model.TradeRoute[r,rr,f,y] != 0:  #Modificación David Romero con base en códigos GAMS y MathProg
        return model.Trade[r, rr, l, f, y] + model.Trade[rr, r, l, f, y] == 0
    else:
        return Constraint.Skip    #Modificación David Romero con base en códigos GAMS y MathProg

model.EnergyBalanceEachTS4 = Constraint(
    model.REGION,
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    rule=EnergyBalanceEachTS4_rule,
)


def EnergyBalanceEachTS5_rule(model, r, l, f, y):
    return model.Production[r, l, f, y] >= model.Demand[r, l, f, y] + model.Use[r, l, f, y] + sum(
        model.Trade[r, rr, l, f, y] * model.TradeRoute[r, rr, f, y]
        for rr in model.REGION
    )


# def EnergyBalanceEachTS5_rule(model, r, l, f, y):
#     if sum(model.OutputActivityRatio[r, t, f, m, y] for t in model.TECHNOLOGY  for m in model.MODE_OF_OPERATION)  !=0:
#         return model.Production[r, l, f, y] >= model.Demand[r, l, f, y] + model.Use[r, l, f, y] + sum(
#             model.Trade[r, rr, l, f, y] * model.TradeRoute[r, rr, f, y]
#             for rr in model.REGION
#         )
#     else:
#         return Constraint.Skip  



model.EnergyBalanceEachTS5 = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.FUEL,
    model.YEAR,
    rule=EnergyBalanceEachTS5_rule,
)


#########        	Energy Balance B		 	#############


def EnergyBalanceEachYear1_rule(model, r, f, y):
    return (
        sum(model.Production[r, l, f, y] for l in model.TIMESLICE)
        == model.ProductionAnnual[r, f, y]
    )


model.EnergyBalanceEachYear1 = Constraint(
    model.REGION, model.FUEL, model.YEAR, rule=EnergyBalanceEachYear1_rule
)


def EnergyBalanceEachYear2_rule(model, r, f, y):
    return (
        sum(model.Use[r, l, f, y] for l in model.TIMESLICE) == model.UseAnnual[r, f, y]
    )


model.EnergyBalanceEachYear2 = Constraint(
    model.REGION, model.FUEL, model.YEAR, rule=EnergyBalanceEachYear2_rule
)


def EnergyBalanceEachYear3_rule(model, r, rr, f, y):
    return (
        sum(model.Trade[r, rr, l, f, y] for l in model.TIMESLICE)
        == model.TradeAnnual[r, rr, f, y]
    )


model.EnergyBalanceEachYear3 = Constraint(
    model.REGION, model.REGION, model.FUEL, model.YEAR, rule=EnergyBalanceEachYear3_rule
)


def EnergyBalanceEachYear4_rule(model, r, f, y):
    return (
        model.ProductionAnnual[r, f, y]
        >= model.UseAnnual[r, f, y]
        + sum(
            model.TradeAnnual[r, rr, f, y] * model.TradeRoute[r, rr, f, y]
            for rr in model.REGION
        )
        + model.AccumulatedAnnualDemand[r, f, y]
    )


model.EnergyBalanceEachYear4 = Constraint(
    model.REGION, model.FUEL, model.YEAR, rule=EnergyBalanceEachYear4_rule
)


#########        	Accounting Technology Production/Use	#############


def FuelProductionByTechnology_rule(model, r, l, t, f, y):
    return (
        model.RateOfProductionByTechnology[r, l, t, f, y] * model.YearSplit[l, y]
        == model.ProductionByTechnology[r, l, t, f, y]
    )


model.FuelProductionByTechnology = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.FUEL,
    model.YEAR,
    rule=FuelProductionByTechnology_rule,
)


def FuelUseByTechnology_rule(model, r, l, t, f, y):
    return (
        model.RateOfUseByTechnology[r, l, t, f, y] * model.YearSplit[l, y]
        == model.UseByTechnology[r, l, t, f, y]
    )


model.FuelUseByTechnology = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.TECHNOLOGY,
    model.FUEL,
    model.YEAR,
    rule=FuelUseByTechnology_rule,
)


def AverageAnnualRateOfActivity_rule(model, r, t, m, y):
    return (
        sum(
            model.RateOfActivity[r, l, t, m, y] * model.YearSplit[l, y]
            for l in model.TIMESLICE
        )
        == model.TotalAnnualTechnologyActivityByMode[r, t, m, y]
    )


model.AverageAnnualRateOfActivity = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.MODE_OF_OPERATION,
    model.YEAR,
    rule=AverageAnnualRateOfActivity_rule,
)


def ModelPeriodCostByRegion_rule(model, r):
    return model.ModelPeriodCostByRegion[r] == sum(
        model.TotalDiscountedCost[r, y] for y in model.YEAR
    )


model.ModelPeriodCostByRegion_constraint = Constraint(
    model.REGION, rule=ModelPeriodCostByRegion_rule
)


#########			Storage equations	(15)		#############


def RateOfStorageCharge_rule(model, r, s, ls, ld, lh, y, t, m):
    if model.TechnologyToStorage[r, t, s, m] > 0:
        return (
            sum(
                model.RateOfActivity[r, l, t, m, y]
                * model.TechnologyToStorage[r, t, s, m]
                * model.Conversionls[l, ls]
                * model.Conversionld[l, ld]
                * model.Conversionlh[l, lh]
                for m in model.MODE_OF_OPERATION
                for l in model.TIMESLICE
                for t in model.TECHNOLOGY
            )
            == model.RateOfStorageCharge[r, s, ls, ld, lh, y]
        )
    else:
        return Constraint.Skip


model.RateOfStorageCharge_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    model.TECHNOLOGY,
    model.MODE_OF_OPERATION,
    rule=RateOfStorageCharge_rule,
)


def RateOfStorageDischarge_rule(model, r, s, ls, ld, lh, y, t, m):
    if model.TechnologyFromStorage[r, t, s, m] > 0:
        return (
            sum(
                model.RateOfActivity[r, l, t, m, y]
                * model.TechnologyFromStorage[r, t, s, m]
                * model.Conversionls[l, ls]
                * model.Conversionld[l, ld]
                * model.Conversionlh[l, lh]
                for m in model.MODE_OF_OPERATION
                for l in model.TIMESLICE
                for t in model.TECHNOLOGY
            )
            == model.RateOfStorageDischarge[r, s, ls, ld, lh, y]
        )
    else:
        return Constraint.Skip


model.RateOfStorageDischarge_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    model.TECHNOLOGY,
    model.MODE_OF_OPERATION,
    rule=RateOfStorageDischarge_rule,
)


def NetChargeWithinYear_rule(model, r, s, ls, ld, lh, y):
    return (
        sum(
            (
                model.RateOfStorageCharge[r, s, ls, ld, lh, y]
                - model.RateOfStorageDischarge[r, s, ls, ld, lh, y]
            )
            * model.YearSplit[l, y]
            * model.Conversionls[l, ls]
            * model.Conversionld[l, ld]
            * model.Conversionlh[l, lh]
            for l in model.TIMESLICE
        )
        == model.NetChargeWithinYear[r, s, ls, ld, lh, y]
    )


model.NetChargeWithinYear_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=NetChargeWithinYear_rule,
)


def NetChargeWithinDay_rule(model, r, s, ls, ld, lh, y):
    return (
        model.RateOfStorageCharge[r, s, ls, ld, lh, y]
        - model.RateOfStorageDischarge[r, s, ls, ld, lh, y]
    ) * model.DaySplit[lh, y] == model.NetChargeWithinDay[r, s, ls, ld, lh, y]


model.NetChargeWithinDay_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=NetChargeWithinDay_rule,
)


def StorageLevelYearStart_rule(model, r, s, y):
    if y == min(model.YEAR):
        return model.StorageLevelStart[r, s] == model.StorageLevelYearStart[r, s, y]
    else:
        return (
            model.StorageLevelYearStart[r, s, y - 1]
            + sum(
                model.NetChargeWithinYear[r, s, ls, ld, lh, y - 1]
                for ls in model.SEASON
                for ld in model.DAYTYPE
                for lh in model.DAILYTIMEBRACKET
            )
            == model.StorageLevelYearStart[r, s, y]
        )


model.StorageLevelYearStart_constraint = Constraint(
    model.REGION, model.STORAGE, model.YEAR, rule=StorageLevelYearStart_rule
)


def StorageLevelYearFinish_rule(model, r, s, y):
    if y < max(model.YEAR):
        return (
            model.StorageLevelYearStart[r, s, y + 1]
            == model.StorageLevelYearFinish[r, s, y]
        )
    else:
        return (
            model.StorageLevelYearStart[r, s, y]
            + sum(
                model.NetChargeWithinYear[r, s, ls, ld, lh, y - 1]
                for ls in model.SEASON
                for ld in model.DAYTYPE
                for lh in model.DAILYTIMEBRACKET
            )
            == model.StorageLevelYearFinish[r, s, y]
        )


model.StorageLevelYearFinish_constraint = Constraint(
    model.REGION, model.STORAGE, model.YEAR, rule=StorageLevelYearFinish_rule
)


def StorageLevelSeasonStart_rule(model, r, s, ls, y):
    if ls == min(model.SEASON):
        return (
            model.StorageLevelYearStart[r, s, y]
            == model.StorageLevelSeasonStart[r, s, ls, y]
        )
    else:
        return (
            model.StorageLevelSeasonStart[r, s, ls - 1, y]
            + sum(
                model.NetChargeWithinYear[r, s, ls - 1, ld, lh, y]
                for ld in model.DAYTYPE
                for lh in model.DAILYTIMEBRACKET
            )
            == model.StorageLevelSeasonStart[r, s, ls, y]
        )


model.StorageLevelSeasonStart_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.YEAR,
    rule=StorageLevelSeasonStart_rule,
)


def StorageLevelDayTypeStart_rule(model, r, s, ls, ld, y):
    if ld == min(model.DAYTYPE):
        return (
            model.StorageLevelSeasonStart[r, s, ls, y]
            == model.StorageLevelDayTypeStart[r, s, ls, ld, y]
        )
    else:
        return (
            model.StorageLevelDayTypeStart[r, s, ls, ld - 1, y]
            + sum(
                model.NetChargeWithinDay[r, s, ls, ld - 1, lh, y]
                for lh in model.DAILYTIMEBRACKET
            )
            == model.StorageLevelDayTypeStart[r, s, ls, ld, y]
        )


model.StorageLevelDayTypeStart_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.YEAR,
    rule=StorageLevelDayTypeStart_rule,
)


def StorageLevelDayTypeFinish_rule(model, r, s, ls, ld, y):
    if ld == max(model.DAYTYPE):
        if ls == max(model.SEASON):
            return (
                model.StorageLevelYearFinish[r, s, y]
                == model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
            )
        else:
            return (
                model.StorageLevelSeasonStart[r, s, ls + 1, y]
                == model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
            )
    else:
        return (
            model.StorageLevelDayTypeFinish[r, s, ls, ld + 1, y]
            - sum(
                model.NetChargeWithinDay[r, s, ls, ld + 1, lh, y]
                for lh in model.DAILYTIMEBRACKET
            )
            * model.DaysInDayType[ls, ld + 1, y]
            == model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
        )


model.StorageLevelDayTypeFinish_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.YEAR,
    rule=StorageLevelDayTypeFinish_rule,
)


#########			Storage constraints		(6)	#############


def LowerLimit_1TimeBracket1InstanceOfDayType1week_rule(model, r, s, ls, ld, lh, y):
    return (
        0
        <= (
            model.StorageLevelDayTypeStart[r, s, ls, ld, y]
            + sum(
                model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
                for lhlh in model.DAILYTIMEBRACKET
                if (lh - lhlh > 0)
            )
        )
        - model.StorageLowerLimit[r, s, y]
    )


model.LowerLimit_1TimeBracket1InstanceOfDayType1week_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=LowerLimit_1TimeBracket1InstanceOfDayType1week_rule,
)


def LowerLimit_EndDaylyTimeBracketLastInstanceOfDayType1Week_rule(
    model, r, s, ls, ld, lh, y
):
    if ld > min(model.DAYTYPE):
        return (
            0
            <= (
                model.StorageLevelDayTypeStart[r, s, ls, ld, y]
                - sum(
                    model.NetChargeWithinDay[r, s, ls, ld - 1, lhlh, y]
                    for lhlh in model.DAILYTIMEBRACKET
                    if (lh - lhlh < 0)
                )
            )
            - model.StorageLowerLimit[r, s, y]
        )
    else:
        return Constraint.Skip


model.LowerLimit_EndDaylyTimeBracketLastInstanceOfDayType1Week_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=LowerLimit_EndDaylyTimeBracketLastInstanceOfDayType1Week_rule,
)


def LowerLimit_EndDaylyTimeBracketLastInstanceOfDayTypeLastWeek_rule(
    model, r, s, ls, ld, lh, y
):
    return (
        0
        <= (
            model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
            - sum(
                model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
                for lhlh in model.DAILYTIMEBRACKET
                if (lh - lhlh < 0)
            )
        )
        - model.StorageLowerLimit[r, s, y]
    )


model.LowerLimit_EndDaylyTimeBracketLastInstanceOfDayTypeLastWeek_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=LowerLimit_EndDaylyTimeBracketLastInstanceOfDayTypeLastWeek_rule,
)


def LowerLimit_1TimeBracket1InstanceOfDayTypeLastweek_rule(model, r, s, ls, ld, lh, y):
    if ld > min(model.DAYTYPE):
        return (
            0
            <= (
                model.StorageLevelDayTypeFinish[r, s, ls, ld - 1, y]
                + sum(
                    model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
                    for lhlh in model.DAILYTIMEBRACKET
                    if (lh - lhlh > 0)
                )
            )
            - model.StorageLowerLimit[r, s, y]
        )
    else:
        return Constraint.Skip


model.LowerLimit_1TimeBracket1InstanceOfDayTypeLastweek_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=LowerLimit_1TimeBracket1InstanceOfDayTypeLastweek_rule,
)


def UpperLimit_1TimeBracket1InstanceOfDayType1week_rule(model, r, s, ls, ld, lh, y):
    return (
        model.StorageLevelDayTypeStart[r, s, ls, ld, y]
        + sum(
            model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
            for lhlh in model.DAILYTIMEBRACKET
            if (lh - lhlh > 0)
        )
    ) - model.StorageUpperLimit[r, s, y] <= 0


model.UpperLimit_1TimeBracket1InstanceOfDayType1week_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=UpperLimit_1TimeBracket1InstanceOfDayType1week_rule,
)


def UpperLimit_EndDaylyTimeBracketLastInstanceOfDayType1Week_rule(
    model, r, s, ls, ld, lh, y
):
    if ld > min(model.DAYTYPE):
        return (
            model.StorageLevelDayTypeStart[r, s, ls, ld, y]
            - sum(
                model.NetChargeWithinDay[r, s, ls, ld - 1, lhlh, y]
                for lhlh in model.DAILYTIMEBRACKET
                if (lh - lhlh < 0)
            )
        ) - model.StorageUpperLimit[r, s, y] <= 0
    else:
        return Constraint.Skip


model.UpperLimit_EndDaylyTimeBracketLastInstanceOfDayType1Week_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=UpperLimit_EndDaylyTimeBracketLastInstanceOfDayType1Week_rule,
)


def UpperLimit_EndDaylyTimeBracketLastInstanceOfDayTypeLastWeek_rule(
    model, r, s, ls, ld, lh, y
):
    return (
        model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
        - sum(
            model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
            for lhlh in model.DAILYTIMEBRACKET
            if (lh - lhlh < 0)
        )
    ) - model.StorageUpperLimit[r, s, y] <= 0


model.UpperLimit_EndDaylyTimeBracketLastInstanceOfDayTypeLastWeek_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=UpperLimit_EndDaylyTimeBracketLastInstanceOfDayTypeLastWeek_rule,
)


def UpperLimit_1TimeBracket1InstanceOfDayTypeLastweek_rule(model, r, s, ls, ld, lh, y):
    if ld > min(model.DAYTYPE):
        return (
            0
            >= (
                model.StorageLevelDayTypeFinish[r, s, ls, ld - 1, y]
                + sum(
                    model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
                    for lhlh in model.DAILYTIMEBRACKET
                    if (lh - lhlh > 0)
                )
            )
            - model.StorageUpperLimit[r, s, y]
        )
    else:
        return Constraint.Skip


model.UpperLimit_1TimeBracket1InstanceOfDayTypeLastweek_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=UpperLimit_1TimeBracket1InstanceOfDayTypeLastweek_rule,
)


def MaxChargeConstraint_rule(model, r, s, ls, ld, lh, y):
    return (
        model.RateOfStorageCharge[r, s, ls, ld, lh, y]
        <= model.StorageMaxChargeRate[r, s]
    )


model.MaxChargeConstraint_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=MaxChargeConstraint_rule,
)


def MaxDischargeConstraint_rule(model, r, s, ls, ld, lh, y):
    return (
        model.RateOfStorageDischarge[r, s, ls, ld, lh, y]
        <= model.StorageMaxDischargeRate[r, s]
    )


model.MaxDischargeConstraint_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.SEASON,
    model.DAYTYPE,
    model.DAILYTIMEBRACKET,
    model.YEAR,
    rule=MaxDischargeConstraint_rule,
)


#########			Storage investments		(10)	#############


def StorageUpperLimit_rule(model, r, s, y):
    return (
        model.AccumulatedNewStorageCapacity[r, s, y]
        + model.ResidualStorageCapacity[r, s, y]
        == model.StorageUpperLimit[r, s, y]
    )


model.StorageUpperLimit_constraint = Constraint(
    model.REGION, model.STORAGE, model.YEAR, rule=StorageUpperLimit_rule
)


def StorageLowerLimit_rule(model, r, s, y):
    return (
        model.MinStorageCharge[r, s, y] * model.StorageUpperLimit[r, s, y]
        == model.StorageLowerLimit[r, s, y]
    )


model.StorageLowerLimit_constraint = Constraint(
    model.REGION, model.STORAGE, model.YEAR, rule=StorageLowerLimit_rule
)


def TotalNewStorage_rule(model, r, s, y):
    return (
        sum(
            model.NewStorageCapacity[r, s, yy]
            for yy in model.YEAR
            if ((y - yy < model.OperationalLifeStorage[r, s]) and (y - yy >= 0))
        )
        == model.AccumulatedNewStorageCapacity[r, s, y]
    )


model.TotalNewStorage_constraint = Constraint(
    model.REGION, model.STORAGE, model.YEAR, rule=TotalNewStorage_rule
)


def UndiscountedCapitalInvestmentStorage_rule(model, r, s, y):
    return (
        model.CapitalCostStorage[r, s, y] * model.NewStorageCapacity[r, s, y]
        == model.CapitalInvestmentStorage[r, s, y]
    )


model.UndiscountedCapitalInvestmentStorage_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.YEAR,
    rule=UndiscountedCapitalInvestmentStorage_rule,
)


def DiscountingCapitalInvestmentStorage_rule(model, r, s, y):
    return (
        model.CapitalInvestmentStorage[r, s, y]
        / ((1 + model.DiscountRate[r]) ** (y - min(model.YEAR)))
        == model.DiscountedCapitalInvestmentStorage[r, s, y]
    )


model.DiscountingCapitalInvestmentStorage_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.YEAR,
    rule=DiscountingCapitalInvestmentStorage_rule,
)


def SalvageValueStorageAtEndOfPeriod_rule(model, r, s, y):
    if (
        model.DepreciationMethod[r] == 1
        and ((y + model.OperationalLifeStorage[r, s] - 1) > max(model.YEAR))
        and model.DiscountRate[r] > 0
    ):
        return model.SalvageValueStorage[r, s, y] == model.CapitalInvestmentStorage[
            r, s, y
        ] * (
            1
            - (
                ((1 + model.DiscountRate[r]) ** (max(model.YEAR) - y + 1) - 1)
                / (
                    (1 + model.DiscountRate[r]) ** model.OperationalLifeStorage[r, s]
                    - 1
                )
            )
        )
    elif (
        model.DepreciationMethod[r] == 1
        and ((y + model.OperationalLifeStorage[r, s] - 1) > max(model.YEAR))
        and model.DiscountRate[r] == 0
    ) or (
        model.DepreciationMethod[r] == 2
        and (y + model.OperationalLifeStorage[r, s] - 1) > (max(model.YEAR))
    ):
        return model.SalvageValueStorage[r, s, y] == model.CapitalInvestmentStorage[
            r, s, y
        ] * (1 - (max(model.YEAR) - y + 1) / model.OperationalLifeStorage[r, s])
    else:
        return model.SalvageValueStorage[r, s, y] == 0


model.SalvageValueStorageAtEndOfPeriod_constraint = Constraint(
    model.REGION, model.STORAGE, model.YEAR, rule=SalvageValueStorageAtEndOfPeriod_rule
)


def SalvageValueStorageDiscountedToStartYear_rule(model, r, s, y):
    return (
        model.SalvageValueStorage[r, s, y]
        / ((1 + model.DiscountRate[r]) ** (max(model.YEAR) - min(model.YEAR) + 1))
        == model.DiscountedSalvageValueStorage[r, s, y]
    )


model.SalvageValueDiscountedToStartYear_constraint = Constraint(
    model.REGION,
    model.STORAGE,
    model.YEAR,
    rule=SalvageValueStorageDiscountedToStartYear_rule,
)


def TotalDiscountedCostByStorage_rule(model, r, s, y):
    return (
        model.DiscountedCapitalInvestmentStorage[r, s, y]
        - model.DiscountedSalvageValueStorage[r, s, y]
        == model.TotalDiscountedStorageCost[r, s, y]
    )


model.TotalDiscountedCostByStorage_constraint = Constraint(
    model.REGION, model.STORAGE, model.YEAR, rule=TotalDiscountedCostByStorage_rule
)


#########       	Capital Costs 		     	#############


def UndiscountedCapitalInvestment_rule(model, r, t, y):
    return (
        model.CapitalCost[r, t, y] * model.NewCapacity[r, t, y]
        == model.CapitalInvestment[r, t, y]
    )


model.UndiscountedCapitalInvestment = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=UndiscountedCapitalInvestment_rule
)


def DiscountedCapitalInvestment_rule(model, r, t, y):
    return (
        model.CapitalInvestment[r, t, y]
        / ((1 + model.DiscountRate[r]) ** (y - min(model.YEAR)))
        == model.DiscountedCapitalInvestment[r, t, y]
    )


model.DiscountedCapitalInvestment_constraint = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=DiscountedCapitalInvestment_rule
)


#########        	Operating Costs 		 	#############


def OperatingCostsVariable_rule(model, r, t, l, y):
    return (
        sum(
            model.TotalAnnualTechnologyActivityByMode[r, t, m, y]
            * model.VariableCost[r, t, m, y]
            for m in model.MODE_OF_OPERATION
        )
        == model.AnnualVariableOperatingCost[r, t, y]
    )


model.OperatingCostsVariable = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.TIMESLICE,
    model.YEAR,
    rule=OperatingCostsVariable_rule,
)


def OperatingCostsFixedAnnual_rule(model, r, t, y):
    return (
        model.TotalCapacityAnnual[r, t, y] * model.FixedCost[r, t, y]
        == model.AnnualFixedOperatingCost[r, t, y]
    )


model.OperatingCostsFixedAnnual = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=OperatingCostsFixedAnnual_rule
)


def OperatingCostsTotalAnnual_rule(model, r, t, y):
    return (
        model.AnnualFixedOperatingCost[r, t, y]
        + model.AnnualVariableOperatingCost[r, t, y]
        == model.OperatingCost[r, t, y]
    )


model.OperatingCostsTotalAnnual = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=OperatingCostsTotalAnnual_rule
)


def DiscountedOperatingCostsTotalAnnual_rule(model, r, t, y):
    return (
        model.OperatingCost[r, t, y]
        / ((1 + model.DiscountRate[r]) ** (y - min(model.YEAR) + 0.5))
        == model.DiscountedOperatingCost[r, t, y]
    )


model.DiscountedOperatingCostsTotalAnnual = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=DiscountedOperatingCostsTotalAnnual_rule,
)


#########       	Total Discounted Costs	 	#############


def TotalDiscountedCostByTechnology_rule(model, r, t, y):
    return (
        model.DiscountedOperatingCost[r, t, y]
        + model.DiscountedCapitalInvestment[r, t, y]
        + model.DiscountedTechnologyEmissionsPenalty[r, t, y]
        - model.DiscountedSalvageValue[r, t, y]
        == model.TotalDiscountedCostByTechnology[r, t, y]
    )


model.TotalDiscountedCostByTechnology_constraint = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=TotalDiscountedCostByTechnology_rule,
)


def TotalDiscountedCost_rule(model, r, y):
    return (
        sum(model.TotalDiscountedCostByTechnology[r, t, y] for t in model.TECHNOLOGY)
        + sum(model.TotalDiscountedStorageCost[r, s, y] for s in model.STORAGE)
        == model.TotalDiscountedCost[r, y]
    )


model.TotalDiscountedCost_constraint = Constraint(
    model.REGION, model.YEAR, rule=TotalDiscountedCost_rule
)

#########      		Total Capacity Constraints 	##############


def TotalAnnualMaxCapacityConstraint_rule(model, r, t, y):
    return model.TotalCapacityAnnual[r, t, y] <= model.TotalAnnualMaxCapacity[r, t, y]


model.TotalAnnualMaxCapacityConstraint = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=TotalAnnualMaxCapacityConstraint_rule,
)


def TotalAnnualMinCapacityConstraint_rule(model, r, t, y):
    return model.TotalCapacityAnnual[r, t, y] >= model.TotalAnnualMinCapacity[r, t, y]


model.TotalAnnualMinCapacityConstraint = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=TotalAnnualMinCapacityConstraint_rule,
)

#########           Salvage Value            	#############


def SalvageValueAtEndOfPeriod1_rule(model, r, t, y):
    if (
        model.DepreciationMethod[r] == 1
        and ((y + model.OperationalLife[r, t] - 1) > max(model.YEAR))
        and model.DiscountRate[r] > 0
    ):
        return model.SalvageValue[r, t, y] == model.CapitalCost[
            r, t, y
        ] * model.NewCapacity[r, t, y] * (
            1
            - (
                ((1 + model.DiscountRate[r]) ** (max(model.YEAR) - y + 1) - 1)
                / ((1 + model.DiscountRate[r]) ** model.OperationalLife[r, t] - 1)
            )
        )
    elif (
        model.DepreciationMethod[r] == 1
        and ((y + model.OperationalLife[r, t] - 1) > max(model.YEAR))
        and model.DiscountRate[r] == 0
    ) or (
        model.DepreciationMethod[r] == 2
        and (y + model.OperationalLife[r, t] - 1) > (max(model.YEAR))
    ):
        return model.SalvageValue[r, t, y] == model.CapitalCost[
            r, t, y
        ] * model.NewCapacity[r, t, y] * (
            1 - (max(model.YEAR) - y + 1) / model.OperationalLife[r, t]
        )
    else:
        return model.SalvageValue[r, t, y] == 0


model.SalvageValueAtEndOfPeriod1 = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=SalvageValueAtEndOfPeriod1_rule
)


def SalvageValueDiscountedToStartYear_rule(model, r, t, y):
    return model.DiscountedSalvageValue[r, t, y] == model.SalvageValue[r, t, y] / (
        (1 + model.DiscountRate[r]) ** (1 + max(model.YEAR) - min(model.YEAR))
    )


model.SalvageValueDiscountedToStartYear = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=SalvageValueDiscountedToStartYear_rule,
)

#########    		New Capacity Constraints  	##############


def TotalAnnualMaxNewCapacityConstraint_rule(model, r, t, y):
    return model.NewCapacity[r, t, y] <= model.TotalAnnualMaxCapacityInvestment[r, t, y]


model.TotalAnnualMaxNewCapacityConstraint = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=TotalAnnualMaxNewCapacityConstraint_rule,
)


def TotalAnnualMinNewCapacityConstraint_rule(model, r, t, y):
    return model.NewCapacity[r, t, y] >= model.TotalAnnualMinCapacityInvestment[r, t, y]


model.TotalAnnualMinNewCapacityConstraint = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=TotalAnnualMinNewCapacityConstraint_rule,
)

#########   		Annual Activity Constraints	##############


def TotalAnnualTechnologyActivity_rule(model, r, t, y):
    return (
        sum(
            model.RateOfTotalActivity[r, t, l, y] * model.YearSplit[l, y]
            for l in model.TIMESLICE
        )
        == model.TotalTechnologyAnnualActivity[r, t, y]
    )


model.TotalAnnualTechnologyActivity = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=TotalAnnualTechnologyActivity_rule
)


def TotalAnnualTechnologyActivityUpperLimit_rule(model, r, t, y):
    return (
        model.TotalTechnologyAnnualActivity[r, t, y]
        <= model.TotalTechnologyAnnualActivityUpperLimit[r, t, y]
    )


model.TotalAnnualTechnologyActivityUpperlimit = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=TotalAnnualTechnologyActivityUpperLimit_rule,
)


def TotalAnnualTechnologyActivityLowerLimit_rule(model, r, t, y):
    return (
        model.TotalTechnologyAnnualActivity[r, t, y]
        >= model.TotalTechnologyAnnualActivityLowerLimit[r, t, y]
    )


model.TotalAnnualTechnologyActivityLowerlimit = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=TotalAnnualTechnologyActivityLowerLimit_rule,
)


#########    		Total Activity Constraints 	##############


def TotalModelHorizonTechnologyActivity_rule(model, r, t):
    return (
        sum(model.TotalTechnologyAnnualActivity[r, t, y] for y in model.YEAR)
        == model.TotalTechnologyModelPeriodActivity[r, t]
    )


model.TotalModelHorizonTechnologyActivity = Constraint(
    model.REGION, model.TECHNOLOGY, rule=TotalModelHorizonTechnologyActivity_rule
)


def TotalModelHorizonTechnologyActivityUpperLimit_rule(model, r, t):
    return (
        model.TotalTechnologyModelPeriodActivity[r, t]
        <= model.TotalTechnologyModelPeriodActivityUpperLimit[r, t]
    )


model.TotalModelHorizonTechnologyActivityUpperLimit = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    rule=TotalModelHorizonTechnologyActivityUpperLimit_rule,
)


def TotalModelHorizonTechnologyActivityLowerLimit_rule(model, r, t):
    return (
        model.TotalTechnologyModelPeriodActivity[r, t]
        >= model.TotalTechnologyModelPeriodActivityLowerLimit[r, t]
    )


model.TotalModelHorizonTechnologyActivityLowerLimit = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    rule=TotalModelHorizonTechnologyActivityLowerLimit_rule,
)


#########   		Emissions Accounting		##############


def AnnualEmissionProductionByMode_rule(model, r, t, e, m, y):
    if model.EmissionActivityRatio[r, t, e, m, y] != 0:
        return (
            model.EmissionActivityRatio[r, t, e, m, y]
            * model.TotalAnnualTechnologyActivityByMode[r, t, m, y]
            == model.AnnualTechnologyEmissionByMode[r, t, e, m, y]
        )
    else:
        return model.AnnualTechnologyEmissionByMode[r, t, e, m, y] == 0


model.AnnualEmissionProductionByMode = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.EMISSION,
    model.MODE_OF_OPERATION,
    model.YEAR,
    rule=AnnualEmissionProductionByMode_rule,
)


def AnnualEmissionProduction_rule(model, r, t, e, y):
    return (
        sum(
            model.AnnualTechnologyEmissionByMode[r, t, e, m, y]
            for m in model.MODE_OF_OPERATION
        )
        == model.AnnualTechnologyEmission[r, t, e, y]
    )


model.AnnualEmissionProduction = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.EMISSION,
    model.YEAR,
    rule=AnnualEmissionProduction_rule,
)


def EmissionPenaltyByTechAndEmission_rule(model, r, t, e, y):
    return (
        model.AnnualTechnologyEmission[r, t, e, y] * model.EmissionsPenalty[r, e, y]
        == model.AnnualTechnologyEmissionPenaltyByEmission[r, t, e, y]
    )


model.EmissionPenaltyByTechAndEmission = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.EMISSION,
    model.YEAR,
    rule=EmissionPenaltyByTechAndEmission_rule,
)


def EmissionsPenaltyByTechnology_rule(model, r, t, y):
    return (
        sum(
            model.AnnualTechnologyEmissionPenaltyByEmission[r, t, e, y]
            for e in model.EMISSION
        )
        == model.AnnualTechnologyEmissionsPenalty[r, t, y]
    )


model.EmissionsPenaltyByTechnology = Constraint(
    model.REGION, model.TECHNOLOGY, model.YEAR, rule=EmissionsPenaltyByTechnology_rule
)


def DiscountedEmissionsPenaltyByTechnology_rule(model, r, t, y):
    return (
        model.AnnualTechnologyEmissionsPenalty[r, t, y]
        / ((1 + model.DiscountRate[r]) ** (y - min(model.YEAR) + 0.5))
        == model.DiscountedTechnologyEmissionsPenalty[r, t, y]
    )


model.DiscountedEmissionsPenaltyByTechnology = Constraint(
    model.REGION,
    model.TECHNOLOGY,
    model.YEAR,
    rule=DiscountedEmissionsPenaltyByTechnology_rule,
)


def EmissionsAccounting1_rule(model, r, e, y):
    return (
        sum(model.AnnualTechnologyEmission[r, t, e, y] for t in model.TECHNOLOGY)
        == model.AnnualEmissions[r, e, y]
    )


model.EmissionsAccounting1 = Constraint(
    model.REGION, model.EMISSION, model.YEAR, rule=EmissionsAccounting1_rule
)


def EmissionsAccounting2_rule(model, r, e):
    return (
        sum(model.AnnualEmissions[r, e, y] for y in model.YEAR)
        == model.ModelPeriodEmissions[r, e] - model.ModelPeriodExogenousEmission[r, e]
    )


model.EmissionsAccounting2 = Constraint(
    model.REGION, model.EMISSION, rule=EmissionsAccounting2_rule
)


def AnnualEmissionsLimit_rule(model, r, e, y):
    return (
        model.AnnualEmissions[r, e, y] + model.AnnualExogenousEmission[r, e, y]
        <= model.AnnualEmissionLimit[r, e, y]
    )


model.AnnualEmissionsLimit = Constraint(
    model.REGION, model.EMISSION, model.YEAR, rule=AnnualEmissionsLimit_rule
)


def ModelPeriodEmissionsLimit_rule(model, r, e):
    return model.ModelPeriodEmissions[r, e] <= model.ModelPeriodEmissionLimit[r, e]


model.ModelPeriodEmissionsLimit = Constraint(
    model.REGION, model.EMISSION, rule=ModelPeriodEmissionsLimit_rule
)


#########   		Reserve Margin Constraint	############## NTS: Should change demand for production


def ReserveMargin_TechnologiesIncluded_rule(model, r, l, y):
    return (
        sum(
            (
                model.TotalCapacityAnnual[r, t, y]
                * model.ReserveMarginTagTechnology[r, t, y]
                * model.CapacityToActivityUnit[r, t]
            )
            for t in model.TECHNOLOGY
        )
        == model.TotalCapacityInReserveMargin[r, y]
    )


model.ReserveMargin_TechnologiesIncluded = Constraint(
    model.REGION,
    model.TIMESLICE,
    model.YEAR,
    rule=ReserveMargin_TechnologiesIncluded_rule,
)


def ReserveMargin_FuelsIncluded_rule(model, r, l, y):
    return (
        sum(
            (model.RateOfProduction[r, l, f, y] * model.ReserveMarginTagFuel[r, f, y])
            for f in model.FUEL
        )
        == model.DemandNeedingReserveMargin[r, l, y]
    )


model.ReserveMargin_FuelsIncluded = Constraint(
    model.REGION, model.TIMESLICE, model.YEAR, rule=ReserveMargin_FuelsIncluded_rule
)


def ReserveMarginConstraint_rule(model, r, l, y):
    return (
        model.DemandNeedingReserveMargin[r, l, y] * model.ReserveMargin[r, y]
        <= model.TotalCapacityInReserveMargin[r, y]
    )


model.ReserveMarginConstraint = Constraint(
    model.REGION, model.TIMESLICE, model.YEAR, rule=ReserveMarginConstraint_rule
)
