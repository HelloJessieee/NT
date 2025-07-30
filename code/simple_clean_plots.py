import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 设置英文字体避免中文问题
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_clean_volunteer_heatmaps():
    """创建干净的志愿者分析热力图"""
    print("Creating clean volunteer analysis heatmaps...")
    
    # 读取最新数据
    aed_data = pd.read_csv("latest_results/aed_final_optimization.csv")
    volunteer_assignments = pd.read_csv("latest_results/volunteer_assignments_latest.csv")
    
    # 设置图形样式
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Volunteer Assignment Analysis Heatmaps', fontsize=20, fontweight='bold')
    
    # 1. 风险评分热力图
    ax1 = axes[0, 0]
    risk_pivot = aed_data.pivot_table(
        values='risk_score', 
        index='planning_area', 
        columns=None, 
        aggfunc='mean'
    )
    sns.heatmap(risk_pivot, annot=True, fmt='.0f', cmap='Reds', ax=ax1, 
                cbar_kws={'label': 'Risk Score'})
    ax1.set_title('Average Risk Score by Region', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('')
    ax1.set_ylabel('Planning Area', fontsize=12)
    
    # 2. 志愿者分配密度热力图
    ax2 = axes[0, 1]
    assignment_counts = volunteer_assignments['subzone_code'].value_counts()
    aed_data['volunteer_count'] = aed_data['subzone_code'].map(assignment_counts).fillna(0)
    
    volunteer_pivot = aed_data.pivot_table(
        values='volunteer_count', 
        index='planning_area', 
        columns=None, 
        aggfunc='sum'
    )
    sns.heatmap(volunteer_pivot, annot=True, fmt='.0f', cmap='Blues', ax=ax2,
                cbar_kws={'label': 'Volunteer Count'})
    ax2.set_title('Volunteer Assignment by Region', fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlabel('')
    ax2.set_ylabel('Planning Area', fontsize=12)
    
    # 3. 优先级评分热力图
    ax3 = axes[1, 0]
    # 计算优先级评分
    aed_data['priority_score'] = aed_data['normalized_risk_score'] * aed_data['area_weight']
    priority_pivot = aed_data.pivot_table(
        values='priority_score', 
        index='planning_area', 
        columns=None, 
        aggfunc='mean'
    )
    sns.heatmap(priority_pivot, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax3,
                cbar_kws={'label': 'Priority Score'})
    ax3.set_title('Average Priority Score by Region', fontsize=14, fontweight='bold', pad=20)
    ax3.set_xlabel('')
    ax3.set_ylabel('Planning Area', fontsize=12)
    
    # 4. 响应时间热力图
    ax4 = axes[1, 1]
    response_pivot = volunteer_assignments.pivot_table(
        values='response_time', 
        index='planning_area', 
        columns=None, 
        aggfunc='mean'
    )
    sns.heatmap(response_pivot, annot=True, fmt='.1f', cmap='RdYlBu_r', ax=ax4,
                cbar_kws={'label': 'Response Time (min)'})
    ax4.set_title('Average Response Time by Region (minutes)', fontsize=14, fontweight='bold', pad=20)
    ax4.set_xlabel('')
    ax4.set_ylabel('Planning Area', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('latest_results/volunteer_analysis_heatmaps_clean.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print("Clean heatmaps saved: latest_results/volunteer_analysis_heatmaps_clean.png")

def create_clean_aed_priority_analysis():
    """创建干净的AED优先级分析图"""
    print("Creating clean AED priority analysis...")
    
    # 读取数据
    aed_data = pd.read_csv("latest_results/aed_final_optimization.csv")
    
    # 计算优先级评分
    if 'priority_score' not in aed_data.columns:
        aed_data['priority_score'] = aed_data['normalized_risk_score'] * aed_data['area_weight']
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Top 20 Subzones by AED Allocation
    top_20 = aed_data.nlargest(20, 'optimized_aeds')
    
    bars = ax1.barh(range(len(top_20)), top_20['optimized_aeds'], color='skyblue', alpha=0.7)
    ax1.set_yticks(range(len(top_20)))
    ax1.set_yticklabels(top_20['subzone_name'], fontsize=10)
    ax1.set_title('Top 20 Subzones by AED Allocation', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Number of AEDs', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax1.text(width + 1, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                ha='left', va='center', fontsize=9)
    
    # 2. Priority Score vs AED Allocation
    ax2.scatter(aed_data['priority_score'], aed_data['optimized_aeds'], alpha=0.6, color='orange')
    ax2.set_title('Priority Score vs AED Allocation', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Priority Score', fontsize=12)
    ax2.set_ylabel('Optimized AEDs', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(aed_data['priority_score'], aed_data['optimized_aeds'], 1)
    p = np.poly1d(z)
    ax2.plot(aed_data['priority_score'], p(aed_data['priority_score']), "r--", alpha=0.8)
    
    # 3. Risk Score vs Area Weight
    ax3.scatter(aed_data['normalized_risk_score'], aed_data['area_weight'], alpha=0.6, color='green')
    ax3.set_title('Risk Score vs Area Weight', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Normalized Risk Score', fontsize=12)
    ax3.set_ylabel('Area Weight', fontsize=12)
    ax3.grid(True, alpha=0.3)
    
    # 4. AED Allocation by Risk Level
    aed_data['risk_category'] = pd.cut(aed_data['normalized_risk_score'], 
                                      bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0], 
                                      labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    
    risk_stats = aed_data.groupby('risk_category')['optimized_aeds'].agg(['mean', 'count']).reset_index()
    
    bars = ax4.bar(range(len(risk_stats)), risk_stats['mean'], color='lightcoral', alpha=0.7)
    ax4.set_title('Average AEDs by Risk Level', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Risk Level', fontsize=12)
    ax4.set_ylabel('Average AEDs per Subzone', fontsize=12)
    ax4.set_xticks(range(len(risk_stats)))
    ax4.set_xticklabels(risk_stats['risk_category'], rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # Add count labels
    for i, bar in enumerate(bars):
        height = bar.get_height()
        count = risk_stats.iloc[i]['count']
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'n={count}', 
                ha='center', va='bottom', fontsize=10)
    
    # 添加标题而不是灰色框
    max_priority_subzone = aed_data.loc[aed_data["priority_score"].idxmax(), "subzone_name"]
    max_priority_score = aed_data["priority_score"].max()
    fig.suptitle(f'Priority Analysis - {max_priority_subzone} (Priority: {max_priority_score:.3f})', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig('latest_results/aed_priority_analysis_clean.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("Clean AED priority analysis saved: latest_results/aed_priority_analysis_clean.png")

if __name__ == "__main__":
    print("Creating clean analysis charts...")
    create_clean_volunteer_heatmaps()
    create_clean_aed_priority_analysis()
    print("All clean analysis charts generated!") 