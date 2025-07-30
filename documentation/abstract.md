# Abstract

Along with the fixed network of AED infrastructure, we also designed an active volunteer dispatch system that optimally matches trained responders with high-risk cardiac arrest zones. This optimization system addresses three crucial components of emergency response: spatial justice in the deployment of resources, response time operational effectiveness, and epidemiological prioritization among community risk profiles. The system is formulated as a constrained bipartite matching problem that maximizes coverage efficiency while respecting practical operational constraints.

The mathematical formulation begins with defining the decision variables. Let x_{ij}∈{0,1} represent the binary assignment decision, where x_{ij}=1 indicates volunteer j is dispatched to subzone i, and x_{ij}=0 otherwise. The optimization objective maximizes the risk-adjusted coverage efficiency through the following function:

max ∑(i=1 to n) ∑(j=1 to m) [x_{ij} × RiskScore_i × AreaWeight_i × (1/ResponseTime_j)]

where RiskScore_i ∈ [0,1] represents the composite cardiac risk metric for subzone i, derived from our XGBoost-based risk assessment model (Section 3.2). The AreaWeight_i ∈ (0,1] term provides geometric normalization based on population density, calculated as:

AreaWeight_i = PopDensity_i / max(PopDensity)

This normalization ensures that densely populated subzones—where emergency response is both more urgent and complex—are prioritized in volunteer assignments. The ResponseTime_j parameter represents the estimated response time for volunteer j, which is modeled as a uniform distribution between 2-15 minutes based on operational experience.

The optimization is subject to fundamental constraints that ensure operational feasibility. First, the volunteer capacity constraint:

∑(i=1 to n) x_{ij} ≤ 1 ∀j ∈ {1,…,m}

guarantees that each volunteer is assigned to at most one subzone, preventing over-commitment during emergency events. Second, the binary assignment constraint:

x_{ij} ∈ {0,1} ∀i,j

maintains the discrete nature of the dispatch problem, where partial assignments are operationally impractical.

Beyond the core mathematical formulation, several real-world operational constraints are incorporated to ensure practical feasibility. Geographic reachability is enforced by setting x_{ij} = 0 if the distance between volunteer j and subzone i exceeds a predefined threshold D_max, typically set at 1000 meters. This ensures that only volunteers within a feasible response range are considered for deployment.

Volunteer availability is another critical constraint, where x_{ij} = 0 if volunteer j is unavailable during the target response window. This accounts for real-world scheduling conflicts, mobility limitations, or other logistical barriers that may prevent participation.

For enhanced priority in critical zones, subzones with risk scores above the 80th percentile receive amplified weighting to prioritize resource allocation. The priority score for subzone i is computed as:

PriorityScore_i = RiskScore_i × AreaWeight_i

This ensures that areas with the highest risk and population density receive proportionally greater attention in volunteer deployment.

Implementation Strategy

A distance-based assignment matrix is constructed prior to optimization to streamline computations. This matrix D(i,j) defines the feasible volunteer-subzone pairs:

- D(i,j) represents the geodesic distance between volunteer j and subzone i centroid.
- D(i,j) = ∞ if the distance exceeds D_max, effectively excluding impractical assignments.

This filtering step reduces computational overhead while ensuring only logistically viable connections are evaluated.

Additionally, response efficiency weighting is introduced to optimize assignments beyond simple proximity. Unlike random or purely distance-based approaches, this model incorporates the reciprocal of response time as a weighting factor, ensuring that volunteers are allocated not just based on availability but also on their ability to reach high-risk zones quickly. This refinement enhances overall system responsiveness and maximizes the impact of limited volunteer resources.

The optimization is solved using linear programming techniques with binary variables, specifically employing the PuLP library for Python. The solution algorithm efficiently handles the bipartite matching problem while respecting all operational constraints.

This approach demonstrates significant improvements in emergency response efficiency through the optimized allocation of volunteer resources across high-risk subzones. The model successfully balances coverage requirements with operational constraints, ensuring that limited volunteer resources are deployed where they can have the greatest impact on cardiac arrest survival rates.


