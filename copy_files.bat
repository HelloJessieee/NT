@echo off
echo Copying important files to government research package...

REM Copy core AED optimization code
copy "..\aed_final_optimization.py" "code\"
copy "..\optimized_risk_model_with_area.py" "code\"
copy "..\optimized_volunteer_assignment_simple.py" "code\"
copy "..\real_aed_optimization_with_area.py" "code\"
copy "..\aed_balanced_simple.py" "code\"
copy "..\aed_comprehensive_analysis.py" "code\"

REM Copy plotting and visualization code
copy "..\plot_aed_final_analysis.py" "code\"
copy "..\plot_aed_balanced_simple.py" "code\"
copy "..\plot_volunteer_assignment_simple.py" "code\"
copy "..\plot_risk_heatmap_latest.py" "code\"
copy "..\create_geographic_heatmaps.py" "code\"
copy "..\simple_clean_plots.py" "code\"

REM Copy data analysis code
copy "..\data_analysis_comprehensive.py" "code\"
copy "..\comprehensive_model_analysis_fixed.py" "code\"
copy "..\volunteer_analysis_latest.py" "code\"
copy "..\risk_model_paper_aligned.py" "code\"

REM Copy utility code
copy "..\calculate_subzone_areas.py" "code\"
copy "..\update_aed_data_integration.py" "code\"
copy "..\main_optimized_pipeline.py" "code\"

REM Copy data files
copy "..\sg_subzone_all_features_with_area.csv" "data\"
copy "..\sg_subzone_all_features_updated.csv" "data\"
copy "..\sg_subzone_centroid_population.csv" "data\"
copy "..\data\AEDLocations_with_coords.csv" "data\"
copy "..\data\volunteers.csv" "data\"
copy "..\data\ResidentPopulationbyPlanningAreaSubzoneofResidenceEthnicGroupandSexCensusofPopulation2020.csv" "data\"

REM Copy latest results
copy "..\latest_results\aed_final_optimization.csv" "results\"
copy "..\latest_results\aed_final_optimization_summary.md" "results\"
copy "..\latest_results\risk_analysis_paper_aligned.csv" "results\"
copy "..\latest_results\volunteer_assignment_simple.csv" "results\"
copy "..\latest_results\volunteer_assignment_simple_summary.csv" "results\"
copy "..\latest_results\volunteer_priority_analysis_latest.csv" "results\"
copy "..\latest_results\volunteer_assignments_latest.csv" "results\"

REM Copy documentation
copy "..\final_results\README.md" "documentation\"
copy "..\final_results\FINAL_SUMMARY.md" "documentation\"
copy "..\AED_Model_2_Algorithm.md" "documentation\"
copy "..\abstract.md" "documentation\"
copy "..\input_data_source_report.md" "documentation\"
copy "..\risk_model_final_analysis.md" "documentation\"
copy "..\volunteer_data_summary.md" "documentation\"
copy "..\data_quality_assessment.md" "documentation\"

REM Copy requirements
copy "..\main_and_requirements.py" "requirements\"

echo File copying completed!
pause 