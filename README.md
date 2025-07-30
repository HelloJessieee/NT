# Singapore AED Deployment Optimization and Volunteer Assignment Research Package

## Project Overview

This project provides a comprehensive study on risk modeling, AED (Automated External Defibrillator) deployment optimization, and volunteer assignment for Out-of-Hospital Cardiac Arrest (OHCA) events in Singapore. The research is based on real geographical data, demographic statistics, and historical OHCA event data, providing scientific evidence for government decision-making.

## Folder Structure

```
government_research_package/
├── code/                    # Core code files
├── data/                    # Data files
├── results/                 # Research results
├── documentation/           # Documentation
├── requirements/            # Environment configuration
└── README.md               # This file
```

## Core Function Modules

### 1. Risk Modeling
- **File**: `code/optimized_risk_model_with_area.py`
- **Function**: Cardiac arrest risk prediction model based on geographical, demographic, and socioeconomic factors
- **Output**: Risk scores and geographical heatmaps

### 2. AED Deployment Optimization
- **File**: `code/aed_final_optimization.py`
- **Function**: Integer linear programming optimization for AED deployment locations
- **Output**: Optimal AED deployment plan and coverage analysis

### 3. Volunteer Assignment
- **File**: `code/optimized_volunteer_assignment_simple.py`
- **Function**: Optimal volunteer assignment based on risk scores and geographical distance
- **Output**: Volunteer assignment plan and coverage maps

### 4. Data Visualization
- **File**: `code/plot_aed_final_analysis.py`, `code/create_geographic_heatmaps.py`
- **Function**: Generate geographical heatmaps, deployment maps, and analysis charts
- **Output**: PNG format visualization results

## Data File Description

### Input Data
- `data/sg_subzone_all_features_with_area.csv`: Singapore subzone feature data (including area weights)
- `data/AEDLocations_with_coords.csv`: Existing AED location data
- `data/volunteers.csv`: Volunteer location data
- `data/ResidentPopulationbyPlanningAreaSubzoneofResidenceEthnicGroupandSexCensusofPopulation2020.csv`: 2020 population census data

### Output Results
- `results/aed_final_optimization.csv`: AED optimization deployment results
- `results/risk_analysis_paper_aligned.csv`: Risk analysis results
- `results/volunteer_assignment_simple.csv`: Volunteer assignment results

## Environment Configuration

### Python Version Requirements
- Python 3.8+

### Install Dependencies
```bash
pip install -r requirements/requirements.txt
```

### Main Dependencies
- pandas: Data processing
- numpy: Numerical computation
- scikit-learn: Machine learning
- geopandas: Geographical data processing
- matplotlib/seaborn: Data visualization
- folium: Interactive maps

## Usage Instructions

### 1. Run Risk Modeling
```bash
python code/optimized_risk_model_with_area.py
```

### 2. Run AED Deployment Optimization
```bash
python code/aed_final_optimization.py
```

### 3. Run Volunteer Assignment
```bash
python code/optimized_volunteer_assignment_simple.py
```

### 4. Generate Visualization Results
```bash
python code/plot_aed_final_analysis.py
```

### 5. Run Complete Analysis Pipeline
```bash
python run_complete_analysis.py
```

## Research Results Summary

### Risk Modeling Results
- Identified high-risk areas for cardiac arrest in Singapore
- Established prediction models based on multiple factors
- Generated detailed risk heatmaps

### AED Deployment Optimization Results
- Optimized AED deployment locations to maximize coverage effectiveness
- Considered population density, risk scores, and geographical factors
- Provided detailed deployment recommendations

### Volunteer Assignment Results
- Assigned volunteers based on risk scores
- Optimized response time and coverage range
- Provided volunteer management recommendations

## Technical Features

1. **Scientific**: Based on real data and statistical modeling
2. **Practical**: Can be directly used for government decision-making
3. **Scalable**: Modular design, easy to extend
4. **Visualization**: Rich charts and map outputs
5. **Reproducible**: Complete code and data

## Key Research Contributions

### Methodological Innovations
- Integration of geographical, demographic, and health data
- Multi-objective optimization for resource allocation
- Risk-based approach for emergency response planning

### Practical Applications
- Evidence-based AED deployment strategy
- Data-driven volunteer management system
- Comprehensive emergency response optimization

### Policy Implications
- Support for evidence-based public health policy
- Resource allocation optimization for emergency services
- Framework for similar studies in other regions

## File Descriptions

### Core Analysis Scripts
- `aed_final_optimization.py`: Main AED optimization algorithm
- `optimized_risk_model_with_area.py`: Risk modeling with area weighting
- `optimized_volunteer_assignment_simple.py`: Volunteer assignment optimization
- `plot_aed_final_analysis.py`: Comprehensive visualization and analysis

### Data Processing Scripts
- `data_analysis_comprehensive.py`: Comprehensive data analysis
- `comprehensive_model_analysis_fixed.py`: Model performance analysis
- `calculate_subzone_areas.py`: Geographical area calculations

### Visualization Scripts
- `create_geographic_heatmaps.py`: Geographical heatmap generation
- `simple_clean_plots.py`: Clean visualization outputs
- `plot_risk_heatmap_latest.py`: Risk visualization

## Contact Information

For technical questions or further clarification, please contact the research team.

## License

This project is for academic research and government decision-making use only. 
