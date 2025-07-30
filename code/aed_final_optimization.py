#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AED Final Optimization - Guaranteed 6613 AEDs
最终的AED优化算法，确保分配所有6613台AED
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# Set English font
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """Load and prepare data"""
    print("🔄 Loading data...")
    
    # Load subzone data
    subzone_data = pd.read_csv('sg_subzone_all_features.csv')
    print(f"✅ Loaded subzone data: {len(subzone_data)} subzones")
    
    # Load latest risk model results
    try:
        risk_data = pd.read_csv('outputs/risk_analysis_paper_aligned.csv')
        print(f"✅ Loaded latest risk data: {len(risk_data)} subzones")
        
        # Merge risk data with subzone data
        subzone_data = subzone_data.merge(risk_data[['subzone_code', 'risk_score', 'risk_score_normalized']], 
                                         on='subzone_code', how='left')
        
        # Use normalized risk score from the latest model
        subzone_data['normalized_risk_score'] = subzone_data['risk_score_normalized']
        
    except FileNotFoundError:
        print("⚠️  Latest risk data not found, using fallback calculation")
        # Fallback: Calculate risk scores
        subzone_data['risk_score'] = (
            subzone_data['Total_Total'] * 0.4 +
            subzone_data['elderly_ratio'] * 10000 * 0.3 +
            subzone_data['low_income_ratio'] * 10000 * 0.3
        )
        subzone_data['normalized_risk_score'] = (subzone_data['risk_score'] - subzone_data['risk_score'].min()) / (subzone_data['risk_score'].max() - subzone_data['risk_score'].min())
    
    # Calculate area weights (using population density as proxy)
    subzone_data['population_density_proxy'] = subzone_data['Total_Total']
    subzone_data['normalized_density'] = subzone_data['population_density_proxy'] / subzone_data['population_density_proxy'].max()
    subzone_data['area_weight'] = subzone_data['normalized_density']
    
    print("✅ Data preparation completed")
    return subzone_data

def final_aed_allocation(subzone_data):
    """Final AED allocation guaranteeing all 6613 AEDs"""
    print("\n🎯 AED Final Optimization - Guaranteed 6613 AEDs")
    print("=" * 60)
    
    total_aeds = 6613  # Target total
    n_subzones = len(subzone_data)
    current_aeds = subzone_data['AED_count'].sum()
    
    print(f"📊 Optimization Parameters:")
    print(f"   Total AEDs to deploy: {total_aeds}")
    print(f"   Current AEDs in data: {current_aeds}")
    print(f"   Total subzones: {n_subzones}")
    
    # Calculate priority scores
    priority_scores = subzone_data['normalized_risk_score'] * subzone_data['area_weight']
    
    # Strategy: Ensure exactly 6613 AEDs are distributed
    # 1. Every subzone gets at least 1 AED
    # 2. Distribute remaining AEDs based on priority
    # 3. Use all 6613 AEDs
    
    base_allocation = np.ones(n_subzones, dtype=int)  # Every subzone gets at least 1 AED
    remaining_aeds = total_aeds - n_subzones  # 6613 - 332 = 6281
    
    print(f"   Base allocation: {n_subzones} AEDs (1 per subzone)")
    print(f"   Remaining AEDs to distribute: {remaining_aeds}")
    
    # Sort subzones by priority
    priority_indices = np.argsort(priority_scores)[::-1]
    
    # Simple distribution: allocate remaining AEDs proportionally based on priority
    priority_sum = priority_scores.sum()
    
    # Calculate proportional allocation
    proportional_allocation = []
    for i in range(n_subzones):
        if priority_sum > 0:
            proportion = priority_scores[i] / priority_sum
            extra_aeds = int(remaining_aeds * proportion)
            proportional_allocation.append(extra_aeds)
        else:
            proportional_allocation.append(0)
    
    # Add proportional allocation to base allocation
    for i in range(n_subzones):
        base_allocation[i] += proportional_allocation[i]
    
    # Distribute any remaining AEDs (due to integer division) to highest priority subzones
    actual_total = base_allocation.sum()
    remaining_after_proportional = total_aeds - actual_total
    
    print(f"   After proportional allocation: {actual_total} AEDs")
    print(f"   Remaining to distribute: {remaining_after_proportional} AEDs")
    
    if remaining_after_proportional > 0:
        for i in range(remaining_after_proportional):
            idx = priority_indices[i % len(priority_indices)]
            base_allocation[idx] += 1
    
    # Calculate coverage effects
    current_coverage_effect = []
    new_coverage_effect = []
    
    for i in range(n_subzones):
        current_effect = subzone_data.iloc[i]['AED_count'] * subzone_data.iloc[i]['normalized_risk_score'] * subzone_data.iloc[i]['area_weight']
        new_effect = base_allocation[i] * subzone_data.iloc[i]['normalized_risk_score'] * subzone_data.iloc[i]['area_weight']
        current_coverage_effect.append(current_effect)
        new_coverage_effect.append(new_effect)
    
    # Create results dataframe
    results = subzone_data.copy()
    results['current_aeds'] = subzone_data['AED_count']
    results['optimized_aeds'] = base_allocation
    results['current_coverage_effect'] = current_coverage_effect
    results['optimized_coverage_effect'] = new_coverage_effect
    results['coverage_improvement'] = np.array(new_coverage_effect) - np.array(current_coverage_effect)
    
    print(f"\n📈 Optimization Results:")
    print(f"   Total AEDs deployed: {base_allocation.sum()}")
    print(f"   Target AEDs: {total_aeds}")
    print(f"   Difference: {base_allocation.sum() - total_aeds}")
    print(f"   Subzones with AEDs: {(base_allocation > 0).sum()}")
    print(f"   Average AEDs per subzone: {base_allocation.mean():.1f}")
    print(f"   Max AEDs in a subzone: {base_allocation.max()}")
    print(f"   Min AEDs in a subzone: {base_allocation.min()}")
    print(f"   Standard deviation: {base_allocation.std():.1f}")
    
    # Distribution analysis
    unique_counts, counts = np.unique(base_allocation, return_counts=True)
    print(f"\n📊 AED Distribution:")
    for count, freq in zip(unique_counts, counts):
        print(f"   {count} AEDs: {freq} subzones")
    
    return results

def create_final_geographic_heatmap(results):
    """Create final geographic heatmap comparison"""
    print("\n🗺️ Creating Final Geographic Heatmap Comparison...")
    
    # Prepare data
    comparison_data = pd.DataFrame({
        'subzone_name': results['subzone_name'],
        'latitude': results['latitude'],
        'longitude': results['longitude'],
        'before_aeds': results['current_aeds'],
        'after_aeds': results['optimized_aeds']
    })
    
    # Calculate improvement
    comparison_data['improvement'] = comparison_data['after_aeds'] - comparison_data['before_aeds']
    
    # Create figure with subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 8))
    
    # Custom colormap for AED counts
    colors = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c', '#08306b']
    cmap = LinearSegmentedColormap.from_list('custom_blue', colors, N=8)
    
    # Before optimization heatmap
    scatter1 = ax1.scatter(comparison_data['longitude'], comparison_data['latitude'], 
                          c=comparison_data['before_aeds'], cmap=cmap, s=100, alpha=0.8)
    ax1.set_title('Before Optimization\nOriginal AED Distribution', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Longitude', fontsize=14)
    ax1.set_ylabel('Latitude', fontsize=14)
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=ax1, label='AED Count')
    
    # After optimization heatmap
    scatter2 = ax2.scatter(comparison_data['longitude'], comparison_data['latitude'], 
                          c=comparison_data['after_aeds'], cmap=cmap, s=100, alpha=0.8)
    ax2.set_title('After Optimization\nFinal AED Distribution (6613)', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Longitude', fontsize=14)
    ax2.set_ylabel('Latitude', fontsize=14)
    ax2.grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=ax2, label='AED Count')
    
    # Improvement heatmap
    # Custom colormap for improvements (red for negative, green for positive)
    colors_improvement = ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#e6f598', '#abdda4', '#66c2a5', '#3288bd']
    cmap_improvement = LinearSegmentedColormap.from_list('custom_improvement', colors_improvement, N=8)
    
    scatter3 = ax3.scatter(comparison_data['longitude'], comparison_data['latitude'], 
                          c=comparison_data['improvement'], cmap=cmap_improvement, s=100, alpha=0.8)
    ax3.set_title('Improvement\n(Optimized - Original)', fontsize=16, fontweight='bold')
    ax3.set_xlabel('Longitude', fontsize=14)
    ax3.set_ylabel('Latitude', fontsize=14)
    ax3.grid(True, alpha=0.3)
    plt.colorbar(scatter3, ax=ax3, label='Improvement (AEDs)')
    
    # Set consistent axis limits for all subplots
    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(comparison_data['longitude'].min() - 0.01, comparison_data['longitude'].max() + 0.01)
        ax.set_ylim(comparison_data['latitude'].min() - 0.01, comparison_data['latitude'].max() + 0.01)
    
    plt.tight_layout()
    plt.savefig('outputs/aed_final_geographic_heatmap.png', dpi=300, bbox_inches='tight')
    print("✅ Final geographic heatmap saved: outputs/aed_final_geographic_heatmap.png")
    
    return fig

def create_statistical_summary(results):
    """Create statistical summary"""
    print("\n📊 Generating Statistical Summary...")
    
    # Calculate statistics
    total_improvement = results['coverage_improvement'].sum()
    avg_improvement = results['coverage_improvement'].mean()
    improved_subzones = (results['coverage_improvement'] > 0).sum()
    worsened_subzones = (results['coverage_improvement'] < 0).sum()
    unchanged_subzones = (results['coverage_improvement'] == 0).sum()
    
    # Top improvements
    top_improvements = results.nlargest(10, 'coverage_improvement')[['subzone_name', 'current_aeds', 'optimized_aeds', 'coverage_improvement']]
    
    # Top optimized subzones
    top_optimized = results.nlargest(10, 'optimized_aeds')[['subzone_name', 'optimized_aeds', 'normalized_risk_score', 'area_weight']]
    
    summary = f"""# AED Final Optimization Summary

## Overall Statistics

### AED Deployment
- **Before Optimization**: {results['current_aeds'].sum():,} AEDs
- **After Optimization**: {results['optimized_aeds'].sum():,} AEDs
- **Difference**: {results['optimized_aeds'].sum() - results['current_aeds'].sum():,} AEDs

### Distribution Statistics
- **Before Average**: {results['current_aeds'].mean():.1f} AEDs per subzone
- **After Average**: {results['optimized_aeds'].mean():.1f} AEDs per subzone
- **Before Std Dev**: {results['current_aeds'].std():.1f}
- **After Std Dev**: {results['optimized_aeds'].std():.1f}

### Coverage Improvement
- **Total Coverage Improvement**: {total_improvement:.3f}
- **Average Improvement per Subzone**: {avg_improvement:.3f}
- **Subzones with Improved Coverage**: {improved_subzones} ({improved_subzones/len(results)*100:.1f}%)
- **Subzones with Reduced Coverage**: {worsened_subzones} ({worsened_subzones/len(results)*100:.1f}%)
- **Unchanged Subzones**: {unchanged_subzones} ({unchanged_subzones/len(results)*100:.1f}%)

### AED Distribution
"""
    
    # Add distribution details
    unique_counts, counts = np.unique(results['optimized_aeds'], return_counts=True)
    for count, freq in zip(unique_counts, counts):
        summary += f"- {count} AEDs: {freq} subzones ({freq/len(results)*100:.1f}%)\n"
    
    summary += f"""

## Top 10 Coverage Improvements

| Subzone | Before | After | Improvement |
|---------|--------|-------|-------------|
"""
    
    for _, row in top_improvements.iterrows():
        summary += f"| {row['subzone_name']} | {row['current_aeds']} | {row['optimized_aeds']} | {row['coverage_improvement']:.3f} |\n"
    
    summary += f"""

## Top 10 Optimized Subzones

| Subzone | Optimized AEDs | Risk Score | Area Weight |
|---------|----------------|------------|-------------|
"""
    
    for _, row in top_optimized.iterrows():
        summary += f"| {row['subzone_name']} | {row['optimized_aeds']} | {row['normalized_risk_score']:.3f} | {row['area_weight']:.3f} |\n"
    
    summary += f"""

## Algorithm Features

### Final Strategy
- **Total AEDs**: Guaranteed 6613 AEDs deployment
- **Base Allocation**: Every subzone gets at least 1 AED
- **Proportional Distribution**: Remaining AEDs distributed proportionally based on priority
- **Priority Formula**: risk_score × area_weight

### Distribution Method
- **Proportional Allocation**: Each subzone gets AEDs proportional to its priority score
- **Integer Handling**: Any remaining AEDs distributed to highest priority subzones
- **Full Utilization**: All 6613 AEDs are deployed

## Conclusion
This final optimization successfully redistributes all 6613 AEDs using area-weighted proportional distribution, ensuring complete deployment while maximizing effectiveness in high-risk, high-population density areas.
"""
    
    with open('outputs/aed_final_optimization_summary.md', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("✅ Final optimization summary saved: outputs/aed_final_optimization_summary.md")
    return summary

def main():
    """Main execution function"""
    print("🚀 AED Final Optimization - Guaranteed 6613 AEDs")
    print("=" * 60)
    
    # Load data
    subzone_data = load_data()
    
    # Run optimization
    results = final_aed_allocation(subzone_data)
    
    # Save results
    results.to_csv('outputs/aed_final_optimization.csv', index=False)
    print(f"\n📁 Results saved: outputs/aed_final_optimization.csv")
    
    # Create visualizations
    create_final_geographic_heatmap(results)
    
    # Generate report
    create_statistical_summary(results)
    
    print("\n🎉 AED final optimization completed!")
    print("📊 Generated files:")
    print("   - outputs/aed_final_optimization.csv")
    print("   - outputs/aed_final_geographic_heatmap.png")
    print("   - outputs/aed_final_optimization_summary.md")

if __name__ == "__main__":
    main() 