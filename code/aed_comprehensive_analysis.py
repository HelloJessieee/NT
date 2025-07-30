#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AED Comprehensive Analysis - Beautiful Visualizations
AED综合分析 - 美观的可视化图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# Set style for beautiful plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

def load_data():
    """Load optimization results"""
    print("🔄 Loading data...")
    
    # Load final optimization results
    results = pd.read_csv('outputs/aed_final_optimization.csv')
    print(f"✅ Loaded optimization data: {len(results)} subzones")
    
    return results

def create_distribution_comparison(results):
    """Create beautiful distribution comparison charts"""
    print("\n📊 Creating Distribution Comparison Charts...")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Before vs After Distribution
    before_data = results['current_aeds']
    after_data = results['optimized_aeds']
    
    # Create histogram comparison
    ax1.hist(before_data, bins=30, alpha=0.7, label='Before Optimization', color='skyblue', edgecolor='black')
    ax1.hist(after_data, bins=30, alpha=0.7, label='After Optimization', color='orange', edgecolor='black')
    ax1.set_xlabel('AED Count per Subzone', fontsize=12)
    ax1.set_ylabel('Number of Subzones', fontsize=12)
    ax1.set_title('AED Distribution Comparison\nBefore vs After Optimization', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Box Plot Comparison
    data_for_box = [before_data, after_data]
    labels = ['Before', 'After']
    colors = ['skyblue', 'orange']
    
    bp = ax2.boxplot(data_for_box, labels=labels, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax2.set_ylabel('AED Count per Subzone', fontsize=12)
    ax2.set_title('AED Distribution Statistics\nBox Plot Comparison', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Cumulative Distribution
    before_sorted = np.sort(before_data)
    after_sorted = np.sort(after_data)
    y_before = np.arange(1, len(before_sorted) + 1) / len(before_sorted)
    y_after = np.arange(1, len(after_sorted) + 1) / len(after_sorted)
    
    ax3.plot(before_sorted, y_before, label='Before Optimization', linewidth=3, color='skyblue')
    ax3.plot(after_sorted, y_after, label='After Optimization', linewidth=3, color='orange')
    ax3.set_xlabel('AED Count per Subzone', fontsize=12)
    ax3.set_ylabel('Cumulative Probability', fontsize=12)
    ax3.set_title('Cumulative Distribution Function\nAED Allocation', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Improvement Analysis
    improvement = after_data - before_data
    positive_improvement = improvement[improvement > 0]
    negative_improvement = improvement[improvement < 0]
    
    ax4.hist(positive_improvement, bins=20, alpha=0.7, label='Positive Improvement', color='green', edgecolor='black')
    ax4.hist(negative_improvement, bins=20, alpha=0.7, label='Negative Improvement', color='red', edgecolor='black')
    ax4.set_xlabel('Improvement in AED Count', fontsize=12)
    ax4.set_ylabel('Number of Subzones', fontsize=12)
    ax4.set_title('Improvement Distribution\nPositive vs Negative Changes', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/aed_distribution_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Distribution analysis saved: outputs/aed_distribution_analysis.png")
    
    return fig

def create_priority_analysis(results):
    """Create priority-based analysis charts"""
    print("\n🎯 Creating Priority Analysis Charts...")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Priority Score vs AED Allocation
    ax1.scatter(results['normalized_risk_score'] * results['area_weight'], 
                results['optimized_aeds'], alpha=0.6, s=50, c='purple')
    ax1.set_xlabel('Priority Score (Risk × Area Weight)', fontsize=12)
    ax1.set_ylabel('Optimized AED Count', fontsize=12)
    ax1.set_title('Priority Score vs AED Allocation\nCorrelation Analysis', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(results['normalized_risk_score'] * results['area_weight'], results['optimized_aeds'], 1)
    p = np.poly1d(z)
    ax1.plot(results['normalized_risk_score'] * results['area_weight'], 
             p(results['normalized_risk_score'] * results['area_weight']), "r--", alpha=0.8)
    
    # 2. Risk Score Distribution
    ax2.hist(results['normalized_risk_score'], bins=30, alpha=0.7, color='coral', edgecolor='black')
    ax2.set_xlabel('Normalized Risk Score', fontsize=12)
    ax2.set_ylabel('Number of Subzones', fontsize=12)
    ax2.set_title('Risk Score Distribution\nAcross All Subzones', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Area Weight vs Population
    ax3.scatter(results['Total_Total'], results['area_weight'], alpha=0.6, s=50, c='teal')
    ax3.set_xlabel('Population', fontsize=12)
    ax3.set_ylabel('Area Weight', fontsize=12)
    ax3.set_title('Population vs Area Weight\nRelationship Analysis', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Top 20 Priority Subzones
    top_20 = results.nlargest(20, 'optimized_aeds')
    colors = plt.cm.viridis(np.linspace(0, 1, len(top_20)))
    
    bars = ax4.barh(range(len(top_20)), top_20['optimized_aeds'], color=colors)
    ax4.set_yticks(range(len(top_20)))
    ax4.set_yticklabels(top_20['subzone_name'], fontsize=10)
    ax4.set_xlabel('Optimized AED Count', fontsize=12)
    ax4.set_title('Top 20 Subzones by AED Allocation', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax4.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('outputs/aed_priority_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Priority analysis saved: outputs/aed_priority_analysis.png")
    
    return fig

def create_regional_analysis(results):
    """Create regional analysis charts"""
    print("\n🗺️ Creating Regional Analysis Charts...")
    
    # Group by planning area
    regional_data = results.groupby('planning_area').agg({
        'current_aeds': 'sum',
        'optimized_aeds': 'sum',
        'Total_Total': 'sum',
        'normalized_risk_score': 'mean',
        'area_weight': 'mean'
    }).reset_index()
    
    regional_data['improvement'] = regional_data['optimized_aeds'] - regional_data['current_aeds']
    regional_data['improvement_ratio'] = regional_data['improvement'] / regional_data['current_aeds'].replace(0, 1)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Regional AED Distribution
    top_regions = regional_data.nlargest(15, 'optimized_aeds')
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_regions)))
    
    bars = ax1.bar(range(len(top_regions)), top_regions['optimized_aeds'], color=colors)
    ax1.set_xticks(range(len(top_regions)))
    ax1.set_xticklabels(top_regions['planning_area'], rotation=45, ha='right', fontsize=10)
    ax1.set_ylabel('Total AEDs', fontsize=12)
    ax1.set_title('Top 15 Planning Areas by AED Allocation', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    # 2. Regional Improvement
    improvement_colors = ['red' if x < 0 else 'green' for x in regional_data['improvement']]
    ax2.bar(range(len(regional_data)), regional_data['improvement'], color=improvement_colors, alpha=0.7)
    ax2.set_xticks(range(len(regional_data)))
    ax2.set_xticklabels(regional_data['planning_area'], rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Improvement in AED Count', fontsize=12)
    ax2.set_title('Regional Improvement Analysis\nPositive vs Negative Changes', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Population vs AED Allocation
    ax3.scatter(regional_data['Total_Total'], regional_data['optimized_aeds'], 
                s=regional_data['improvement_ratio']*100, alpha=0.7, c='purple')
    ax3.set_xlabel('Total Population', fontsize=12)
    ax3.set_ylabel('Total AEDs', fontsize=12)
    ax3.set_title('Population vs AED Allocation\nBubble Size = Improvement Ratio', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Regional Risk vs Area Weight
    ax4.scatter(regional_data['normalized_risk_score'], regional_data['area_weight'], 
                s=regional_data['optimized_aeds']/10, alpha=0.7, c='orange')
    ax4.set_xlabel('Average Risk Score', fontsize=12)
    ax4.set_ylabel('Average Area Weight', fontsize=12)
    ax4.set_title('Regional Risk vs Area Weight\nBubble Size = AED Count', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/aed_regional_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Regional analysis saved: outputs/aed_regional_analysis.png")
    
    return fig

def create_performance_metrics(results):
    """Create performance metrics visualization"""
    print("\n📈 Creating Performance Metrics...")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Coverage Effect Improvement
    coverage_improvement = results['coverage_improvement']
    
    ax1.hist(coverage_improvement, bins=30, alpha=0.7, color='gold', edgecolor='black')
    ax1.axvline(coverage_improvement.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {coverage_improvement.mean():.3f}')
    ax1.axvline(coverage_improvement.median(), color='blue', linestyle='--', linewidth=2, label=f'Median: {coverage_improvement.median():.3f}')
    ax1.set_xlabel('Coverage Effect Improvement', fontsize=12)
    ax1.set_ylabel('Number of Subzones', fontsize=12)
    ax1.set_title('Coverage Effect Improvement Distribution', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Efficiency Analysis
    efficiency = results['optimized_aeds'] / results['Total_Total'].replace(0, 1)
    
    ax2.scatter(results['Total_Total'], efficiency, alpha=0.6, s=50, c='green')
    ax2.set_xlabel('Population', fontsize=12)
    ax2.set_ylabel('AEDs per Capita', fontsize=12)
    ax2.set_title('Population vs AED Efficiency\nAEDs per Capita', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Optimization Quality
    before_coverage = results['current_coverage_effect'].sum()
    after_coverage = results['optimized_coverage_effect'].sum()
    improvement_percentage = ((after_coverage - before_coverage) / before_coverage) * 100
    
    labels = ['Before Optimization', 'After Optimization']
    values = [before_coverage, after_coverage]
    colors = ['lightcoral', 'lightgreen']
    
    bars = ax3.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_ylabel('Total Coverage Effect', fontsize=12)
    ax3.set_title(f'Overall Coverage Effect Comparison\nImprovement: {improvement_percentage:.1f}%', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.1f}', ha='center', va='bottom', fontsize=12)
    
    # 4. Subzone Performance Ranking
    top_performers = results.nlargest(15, 'coverage_improvement')
    
    bars = ax4.barh(range(len(top_performers)), top_performers['coverage_improvement'], 
                    color=plt.cm.RdYlBu_r(np.linspace(0, 1, len(top_performers))))
    ax4.set_yticks(range(len(top_performers)))
    ax4.set_yticklabels(top_performers['subzone_name'], fontsize=9)
    ax4.set_xlabel('Coverage Effect Improvement', fontsize=12)
    ax4.set_title('Top 15 Subzones by Coverage Improvement', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/aed_performance_metrics.png', dpi=300, bbox_inches='tight')
    print("✅ Performance metrics saved: outputs/aed_performance_metrics.png")
    
    return fig

def create_summary_dashboard(results):
    """Create a comprehensive summary dashboard"""
    print("\n📊 Creating Summary Dashboard...")
    
    fig = plt.figure(figsize=(24, 16))
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    # 1. Key Statistics
    ax1 = fig.add_subplot(gs[0, 0])
    stats_data = {
        'Total AEDs': results['optimized_aeds'].sum(),
        'Avg per Subzone': results['optimized_aeds'].mean(),
        'Max Allocation': results['optimized_aeds'].max(),
        'Min Allocation': results['optimized_aeds'].min()
    }
    
    bars = ax1.bar(stats_data.keys(), stats_data.values(), color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax1.set_title('Key Statistics', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.1f}', ha='center', va='bottom', fontsize=10)
    
    # 2. Distribution Pie Chart
    ax2 = fig.add_subplot(gs[0, 1])
    distribution = results['optimized_aeds'].value_counts().head(5)
    colors = plt.cm.Set3(np.linspace(0, 1, len(distribution)))
    ax2.pie(distribution.values, labels=distribution.index, autopct='%1.1f%%', colors=colors)
    ax2.set_title('Top 5 AED Distribution', fontsize=12, fontweight='bold')
    
    # 3. Improvement Analysis
    ax3 = fig.add_subplot(gs[0, 2])
    improvement = results['optimized_aeds'] - results['current_aeds']
    positive = (improvement > 0).sum()
    negative = (improvement < 0).sum()
    neutral = (improvement == 0).sum()
    
    ax3.pie([positive, negative, neutral], labels=['Improved', 'Reduced', 'No Change'], 
            autopct='%1.1f%%', colors=['#2ECC71', '#E74C3C', '#95A5A6'])
    ax3.set_title('Improvement Analysis', fontsize=12, fontweight='bold')
    
    # 4. Coverage Effect
    ax4 = fig.add_subplot(gs[0, 3])
    before_effect = results['current_coverage_effect'].sum()
    after_effect = results['optimized_coverage_effect'].sum()
    
    ax4.bar(['Before', 'After'], [before_effect, after_effect], 
            color=['#E67E22', '#9B59B6'], alpha=0.7)
    ax4.set_title('Coverage Effect Comparison', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Total Coverage Effect')
    
    # 5. Priority Score Distribution
    ax5 = fig.add_subplot(gs[1, :2])
    priority_scores = results['normalized_risk_score'] * results['area_weight']
    ax5.hist(priority_scores, bins=30, alpha=0.7, color='#3498DB', edgecolor='black')
    ax5.set_xlabel('Priority Score')
    ax5.set_ylabel('Number of Subzones')
    ax5.set_title('Priority Score Distribution', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. AED vs Population Scatter
    ax6 = fig.add_subplot(gs[1, 2:])
    scatter = ax6.scatter(results['Total_Total'], results['optimized_aeds'], 
                         c=priority_scores, cmap='viridis', alpha=0.6, s=50)
    ax6.set_xlabel('Population')
    ax6.set_ylabel('Optimized AEDs')
    ax6.set_title('Population vs AED Allocation\nColored by Priority Score', fontsize=12, fontweight='bold')
    plt.colorbar(scatter, ax=ax6, label='Priority Score')
    ax6.grid(True, alpha=0.3)
    
    # 7. Regional Performance
    ax7 = fig.add_subplot(gs[2, :])
    regional_performance = results.groupby('planning_area')['coverage_improvement'].sum().sort_values(ascending=False).head(10)
    
    bars = ax7.bar(range(len(regional_performance)), regional_performance.values, 
                   color=plt.cm.coolwarm(np.linspace(0, 1, len(regional_performance))))
    ax7.set_xticks(range(len(regional_performance)))
    ax7.set_xticklabels(regional_performance.index, rotation=45, ha='right')
    ax7.set_ylabel('Total Coverage Improvement')
    ax7.set_title('Top 10 Planning Areas by Coverage Improvement', fontsize=12, fontweight='bold')
    ax7.grid(True, alpha=0.3)
    
    plt.suptitle('AED Optimization - Comprehensive Analysis Dashboard', fontsize=16, fontweight='bold')
    plt.savefig('outputs/aed_comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
    print("✅ Comprehensive dashboard saved: outputs/aed_comprehensive_dashboard.png")
    
    return fig

def main():
    """Main execution function"""
    print("🎨 AED Comprehensive Analysis - Beautiful Visualizations")
    print("=" * 60)
    
    # Load data
    results = load_data()
    
    # Create all analysis charts
    create_distribution_comparison(results)
    create_priority_analysis(results)
    create_regional_analysis(results)
    create_performance_metrics(results)
    create_summary_dashboard(results)
    
    print("\n🎉 AED comprehensive analysis completed!")
    print("📊 Generated beautiful analysis files:")
    print("   - outputs/aed_distribution_analysis.png")
    print("   - outputs/aed_priority_analysis.png")
    print("   - outputs/aed_regional_analysis.png")
    print("   - outputs/aed_performance_metrics.png")
    print("   - outputs/aed_comprehensive_dashboard.png")

if __name__ == "__main__":
    main() 