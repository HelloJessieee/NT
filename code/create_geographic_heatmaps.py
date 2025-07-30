import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 设置英文字体
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_singapore_geographic_heatmaps():
    """创建基于新加坡地图的地理热力图"""
    print("Creating Singapore geographic heatmaps...")
    
    # 读取最新数据
    aed_data = pd.read_csv("latest_results/aed_final_optimization.csv")
    volunteer_assignments = pd.read_csv("latest_results/volunteer_assignments_latest.csv")
    
    # 计算优先级评分
    aed_data['priority_score'] = aed_data['normalized_risk_score'] * aed_data['area_weight']
    
    # 准备志愿者数据
    assignment_counts = volunteer_assignments['subzone_code'].value_counts()
    aed_data['volunteer_count'] = aed_data['subzone_code'].map(assignment_counts).fillna(0)
    
    # 新加坡地理边界（简化）
    singapore_bounds = {
        'min_lat': 1.2, 'max_lat': 1.5,
        'min_lon': 103.6, 'max_lon': 104.1
    }
    
    # 创建2x2子图
    fig, axes = plt.subplots(2, 2, figsize=(24, 20))
    fig.suptitle('Singapore Geographic Analysis Heatmaps', fontsize=24, fontweight='bold')
    
    # 1. 风险评分地理分布
    ax1 = axes[0, 0]
    scatter1 = ax1.scatter(aed_data['longitude'], aed_data['latitude'], 
                          c=aed_data['risk_score'], s=100, cmap='Reds', alpha=0.8, edgecolors='white', linewidth=0.5)
    ax1.set_xlim(singapore_bounds['min_lon'], singapore_bounds['max_lon'])
    ax1.set_ylim(singapore_bounds['min_lat'], singapore_bounds['max_lat'])
    ax1.set_title('Risk Score Geographic Distribution', fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('Longitude', fontsize=12)
    ax1.set_ylabel('Latitude', fontsize=12)
    ax1.grid(True, alpha=0.3)
    cbar1 = plt.colorbar(scatter1, ax=ax1, shrink=0.8)
    cbar1.set_label('Risk Score', fontsize=12)
    
    # 添加主要区域标签
    for _, row in aed_data.nlargest(10, 'risk_score').iterrows():
        ax1.annotate(row['subzone_name'], 
                    (row['longitude'], row['latitude']), 
                    xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, alpha=0.8)
    
    # 2. 志愿者分配地理分布
    ax2 = axes[0, 1]
    scatter2 = ax2.scatter(aed_data['longitude'], aed_data['latitude'], 
                          c=aed_data['volunteer_count'], s=100, cmap='Blues', alpha=0.8, edgecolors='white', linewidth=0.5)
    ax2.set_xlim(singapore_bounds['min_lon'], singapore_bounds['max_lon'])
    ax2.set_ylim(singapore_bounds['min_lat'], singapore_bounds['max_lat'])
    ax2.set_title('Volunteer Assignment Geographic Distribution', fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlabel('Longitude', fontsize=12)
    ax2.set_ylabel('Latitude', fontsize=12)
    ax2.grid(True, alpha=0.3)
    cbar2 = plt.colorbar(scatter2, ax=ax2, shrink=0.8)
    cbar2.set_label('Volunteer Count', fontsize=12)
    
    # 添加主要区域标签
    for _, row in aed_data.nlargest(10, 'volunteer_count').iterrows():
        ax2.annotate(row['subzone_name'], 
                    (row['longitude'], row['latitude']), 
                    xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, alpha=0.8)
    
    # 3. AED分配地理分布
    ax3 = axes[1, 0]
    scatter3 = ax3.scatter(aed_data['longitude'], aed_data['latitude'], 
                          c=aed_data['optimized_aeds'], s=100, cmap='Greens', alpha=0.8, edgecolors='white', linewidth=0.5)
    ax3.set_xlim(singapore_bounds['min_lon'], singapore_bounds['max_lon'])
    ax3.set_ylim(singapore_bounds['min_lat'], singapore_bounds['max_lat'])
    ax3.set_title('AED Allocation Geographic Distribution', fontsize=16, fontweight='bold', pad=20)
    ax3.set_xlabel('Longitude', fontsize=12)
    ax3.set_ylabel('Latitude', fontsize=12)
    ax3.grid(True, alpha=0.3)
    cbar3 = plt.colorbar(scatter3, ax=ax3, shrink=0.8)
    cbar3.set_label('Optimized AEDs', fontsize=12)
    
    # 添加主要区域标签
    for _, row in aed_data.nlargest(10, 'optimized_aeds').iterrows():
        ax3.annotate(row['subzone_name'], 
                    (row['longitude'], row['latitude']), 
                    xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, alpha=0.8)
    
    # 4. 优先级评分地理分布
    ax4 = axes[1, 1]
    scatter4 = ax4.scatter(aed_data['longitude'], aed_data['latitude'], 
                          c=aed_data['priority_score'], s=100, cmap='YlOrRd', alpha=0.8, edgecolors='white', linewidth=0.5)
    ax4.set_xlim(singapore_bounds['min_lon'], singapore_bounds['max_lon'])
    ax4.set_ylim(singapore_bounds['min_lat'], singapore_bounds['max_lat'])
    ax4.set_title('Priority Score Geographic Distribution', fontsize=16, fontweight='bold', pad=20)
    ax4.set_xlabel('Longitude', fontsize=12)
    ax4.set_ylabel('Latitude', fontsize=12)
    ax4.grid(True, alpha=0.3)
    cbar4 = plt.colorbar(scatter4, ax=ax4, shrink=0.8)
    cbar4.set_label('Priority Score', fontsize=12)
    
    # 添加主要区域标签
    for _, row in aed_data.nlargest(10, 'priority_score').iterrows():
        ax4.annotate(row['subzone_name'], 
                    (row['longitude'], row['latitude']), 
                    xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, alpha=0.8)
    
    plt.tight_layout()
    plt.savefig('latest_results/singapore_geographic_heatmaps.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Singapore geographic heatmaps saved: latest_results/singapore_geographic_heatmaps.png")

def create_singapore_volunteer_coverage_map():
    """创建新加坡志愿者覆盖地图"""
    print("Creating Singapore volunteer coverage map...")
    
    # 读取数据
    aed_data = pd.read_csv("latest_results/aed_final_optimization.csv")
    volunteer_assignments = pd.read_csv("latest_results/volunteer_assignments_latest.csv")
    
    # 计算优先级评分
    aed_data['priority_score'] = aed_data['normalized_risk_score'] * aed_data['area_weight']
    
    # 准备数据
    assignment_counts = volunteer_assignments['subzone_code'].value_counts()
    aed_data['volunteer_count'] = aed_data['subzone_code'].map(assignment_counts).fillna(0)
    
    # 新加坡地理边界
    singapore_bounds = {
        'min_lat': 1.2, 'max_lat': 1.5,
        'min_lon': 103.6, 'max_lon': 104.1
    }
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 12))
    fig.suptitle('Singapore Volunteer Coverage Analysis', fontsize=20, fontweight='bold')
    
    # 1. 志愿者覆盖热力图
    scatter1 = ax1.scatter(aed_data['longitude'], aed_data['latitude'], 
                          c=aed_data['volunteer_count'], s=150, cmap='viridis', alpha=0.8, edgecolors='white', linewidth=0.5)
    ax1.set_xlim(singapore_bounds['min_lon'], singapore_bounds['max_lon'])
    ax1.set_ylim(singapore_bounds['min_lat'], singapore_bounds['max_lat'])
    ax1.set_title('Volunteer Coverage Heatmap', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Longitude', fontsize=12)
    ax1.set_ylabel('Latitude', fontsize=12)
    ax1.grid(True, alpha=0.3)
    cbar1 = plt.colorbar(scatter1, ax=ax1, shrink=0.8)
    cbar1.set_label('Volunteer Count', fontsize=12)
    
    # 添加覆盖统计
    covered_subzones = len(aed_data[aed_data['volunteer_count'] > 0])
    total_subzones = len(aed_data)
    coverage_rate = covered_subzones / total_subzones * 100
    ax1.text(0.02, 0.98, f'Coverage: {covered_subzones}/{total_subzones} ({coverage_rate:.1f}%)', 
             transform=ax1.transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 2. 风险vs志愿者分配散点图
    scatter2 = ax2.scatter(aed_data['risk_score'], aed_data['volunteer_count'], 
                          c=aed_data['priority_score'], s=100, cmap='YlOrRd', alpha=0.7)
    ax2.set_title('Risk Score vs Volunteer Assignment', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Risk Score', fontsize=12)
    ax2.set_ylabel('Volunteer Count', fontsize=12)
    ax2.grid(True, alpha=0.3)
    cbar2 = plt.colorbar(scatter2, ax=ax2, shrink=0.8)
    cbar2.set_label('Priority Score', fontsize=12)
    
    # 添加趋势线
    z = np.polyfit(aed_data['risk_score'], aed_data['volunteer_count'], 1)
    p = np.poly1d(z)
    ax2.plot(aed_data['risk_score'], p(aed_data['risk_score']), "r--", alpha=0.8, linewidth=2)
    
    # 添加相关系数
    correlation = aed_data['risk_score'].corr(aed_data['volunteer_count'])
    ax2.text(0.02, 0.98, f'Correlation: {correlation:.3f}', 
             transform=ax2.transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('latest_results/singapore_volunteer_coverage_map.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Singapore volunteer coverage map saved: latest_results/singapore_volunteer_coverage_map.png")

def create_singapore_aed_deployment_map():
    """创建新加坡AED部署地图"""
    print("Creating Singapore AED deployment map...")
    
    # 读取数据
    aed_data = pd.read_csv("latest_results/aed_final_optimization.csv")
    
    # 新加坡地理边界
    singapore_bounds = {
        'min_lat': 1.2, 'max_lat': 1.5,
        'min_lon': 103.6, 'max_lon': 104.1
    }
    
    # 创建图形
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(24, 20))
    fig.suptitle('Singapore AED Deployment Analysis', fontsize=24, fontweight='bold')
    
    # 1. 当前AED分布
    scatter1 = ax1.scatter(aed_data['longitude'], aed_data['latitude'], 
                          c=aed_data['current_aeds'], s=100, cmap='Blues', alpha=0.8, edgecolors='white', linewidth=0.5)
    ax1.set_xlim(singapore_bounds['min_lon'], singapore_bounds['max_lon'])
    ax1.set_ylim(singapore_bounds['min_lat'], singapore_bounds['max_lat'])
    ax1.set_title('Current AED Distribution', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Longitude', fontsize=12)
    ax1.set_ylabel('Latitude', fontsize=12)
    ax1.grid(True, alpha=0.3)
    cbar1 = plt.colorbar(scatter1, ax=ax1, shrink=0.8)
    cbar1.set_label('Current AEDs', fontsize=12)
    
    # 2. 优化后AED分布
    scatter2 = ax2.scatter(aed_data['longitude'], aed_data['latitude'], 
                          c=aed_data['optimized_aeds'], s=100, cmap='Greens', alpha=0.8, edgecolors='white', linewidth=0.5)
    ax2.set_xlim(singapore_bounds['min_lon'], singapore_bounds['max_lon'])
    ax2.set_ylim(singapore_bounds['min_lat'], singapore_bounds['max_lat'])
    ax2.set_title('Optimized AED Distribution', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Longitude', fontsize=12)
    ax2.set_ylabel('Latitude', fontsize=12)
    ax2.grid(True, alpha=0.3)
    cbar2 = plt.colorbar(scatter2, ax=ax2, shrink=0.8)
    cbar2.set_label('Optimized AEDs', fontsize=12)
    
    # 3. AED改进分布
    aed_data['aed_improvement'] = aed_data['optimized_aeds'] - aed_data['current_aeds']
    scatter3 = ax3.scatter(aed_data['longitude'], aed_data['latitude'], 
                          c=aed_data['aed_improvement'], s=100, cmap='RdYlBu', alpha=0.8, edgecolors='white', linewidth=0.5)
    ax3.set_xlim(singapore_bounds['min_lon'], singapore_bounds['max_lon'])
    ax3.set_ylim(singapore_bounds['min_lat'], singapore_bounds['max_lat'])
    ax3.set_title('AED Improvement Distribution', fontsize=16, fontweight='bold')
    ax3.set_xlabel('Longitude', fontsize=12)
    ax3.set_ylabel('Latitude', fontsize=12)
    ax3.grid(True, alpha=0.3)
    cbar3 = plt.colorbar(scatter3, ax=ax3, shrink=0.8)
    cbar3.set_label('AED Improvement', fontsize=12)
    
    # 4. 覆盖率改进
    scatter4 = ax4.scatter(aed_data['longitude'], aed_data['latitude'], 
                          c=aed_data['coverage_improvement'], s=100, cmap='RdYlGn', alpha=0.8, edgecolors='white', linewidth=0.5)
    ax4.set_xlim(singapore_bounds['min_lon'], singapore_bounds['max_lon'])
    ax4.set_ylim(singapore_bounds['min_lat'], singapore_bounds['max_lat'])
    ax4.set_title('Coverage Improvement Distribution', fontsize=16, fontweight='bold')
    ax4.set_xlabel('Longitude', fontsize=12)
    ax4.set_ylabel('Latitude', fontsize=12)
    ax4.grid(True, alpha=0.3)
    cbar4 = plt.colorbar(scatter4, ax=ax4, shrink=0.8)
    cbar4.set_label('Coverage Improvement', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('latest_results/singapore_aed_deployment_map.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Singapore AED deployment map saved: latest_results/singapore_aed_deployment_map.png")

if __name__ == "__main__":
    print("Creating Singapore geographic analysis maps...")
    create_singapore_geographic_heatmaps()
    create_singapore_volunteer_coverage_map()
    create_singapore_aed_deployment_map()
    print("All Singapore geographic maps generated!") 