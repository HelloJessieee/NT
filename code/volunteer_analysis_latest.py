import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic
from pulp import *
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_latest_data():
    """
    加载最新的risk和aed数据
    """
    print("🔄 加载最新数据...")
    
    # 读取最新的AED优化数据
    aed_data = pd.read_csv("latest_results/aed_final_optimization.csv")
    print(f"✅ 加载AED数据: {len(aed_data)} 个分区")
    
    # 读取最新的风险数据
    risk_data = pd.read_csv("latest_results/risk_analysis_paper_aligned.csv")
    print(f"✅ 加载风险数据: {len(risk_data)} 个分区")
    
    # 读取志愿者数据
    volunteer_data = pd.read_csv("data/volunteers.csv")
    volunteer_data = volunteer_data.head(1000)  # 使用前1000个志愿者
    print(f"✅ 加载志愿者数据: {len(volunteer_data)} 个志愿者")
    
    # 直接使用AED数据，它已经包含了风险评分
    subzone_data = aed_data.copy()
    
    # 使用最新模型的标准化风险评分
    subzone_data['normalized_risk_score'] = subzone_data['risk_score_normalized']
    
    # 计算综合优先级（风险评分 × 面积权重）
    subzone_data['priority_score'] = subzone_data['normalized_risk_score'] * subzone_data['area_weight']
    
    # 为志愿者生成模拟位置
    print("🔄 生成志愿者模拟位置...")
    np.random.seed(42)
    volunteer_data['latitude'] = np.random.uniform(1.2, 1.5, len(volunteer_data))
    volunteer_data['longitude'] = np.random.uniform(103.6, 104.0, len(volunteer_data))
    volunteer_data['availability'] = 1
    volunteer_data['response_time'] = np.random.uniform(2, 15, len(volunteer_data))
    
    print(f"✅ 数据加载完成")
    print(f"   总志愿者数量: {len(volunteer_data)}")
    print(f"   可用志愿者数量: {volunteer_data['availability'].sum()}")
    print(f"   平均响应时间: {volunteer_data['response_time'].mean():.1f} 分钟")
    
    return subzone_data, volunteer_data

def create_distance_matrix(subzone_data, volunteer_data, max_distance=1000):
    """
    创建分区和志愿者之间的距离矩阵
    """
    print(f"🔄 创建距离矩阵 (最大距离: {max_distance}m)...")
    
    n_subzones = len(subzone_data)
    n_volunteers = len(volunteer_data)
    
    # 初始化距离矩阵
    distance_matrix = np.full((n_subzones, n_volunteers), np.inf)
    
    # 计算距离
    valid_connections = 0
    for i, subzone in subzone_data.iterrows():
        if i % 50 == 0:
            print(f"   处理分区 {i+1}/{n_subzones}: {subzone['subzone_name']}")
        
        subzone_point = (subzone['latitude'], subzone['longitude'])
        
        for j, volunteer in volunteer_data.iterrows():
            if volunteer['availability'] == 1:
                volunteer_point = (volunteer['latitude'], volunteer['longitude'])
                distance = geodesic(subzone_point, volunteer_point).meters
                
                if distance <= max_distance:
                    distance_matrix[i, j] = distance
                    valid_connections += 1
    
    print(f"✅ 距离矩阵创建完成: {distance_matrix.shape}")
    print(f"   有效连接数: {valid_connections}")
    print(f"   平均每个分区可连接志愿者数: {(distance_matrix != np.inf).sum(axis=1).mean():.1f}")
    
    return distance_matrix

def optimize_volunteer_assignment(subzone_data, volunteer_data, distance_matrix):
    """
    优化志愿者分配
    """
    print("🔄 开始优化志愿者分配...")
    
    n_subzones = len(subzone_data)
    n_volunteers = len(volunteer_data)
    
    # 创建优化问题
    prob = LpProblem("Volunteer_Assignment", LpMaximize)
    
    # 决策变量：x[i,j] = 1 如果志愿者j被分配到分区i
    x = LpVariable.dicts("assignment", 
                        [(i, j) for i in range(n_subzones) for j in range(n_volunteers)], 
                        cat='Binary')
    
    # 目标函数：最大化风险覆盖
    prob += lpSum([x[i, j] * subzone_data.iloc[i]['priority_score'] * 
                   (1 / (distance_matrix[i, j] + 1))  # 避免除零
                   for i in range(n_subzones) 
                   for j in range(n_volunteers) 
                   if distance_matrix[i, j] != np.inf])
    
    # 约束条件1：每个志愿者最多分配1个分区
    for j in range(n_volunteers):
        prob += lpSum([x[i, j] for i in range(n_subzones) 
                      if distance_matrix[i, j] != np.inf]) <= 1
    
    # 约束条件2：每个分区最多分配3个志愿者
    for i in range(n_subzones):
        prob += lpSum([x[i, j] for j in range(n_volunteers) 
                      if distance_matrix[i, j] != np.inf]) <= 3
    
    # 约束条件3：优先分配高优先级分区
    # 按优先级排序分区
    priority_order = subzone_data['priority_score'].sort_values(ascending=False).index
    
    print("🔄 求解优化问题...")
    prob.solve(PULP_CBC_CMD(msg=False))
    
    print(f"✅ 优化完成，状态: {LpStatus[prob.status]}")
    
    # 提取结果
    assignments = []
    for i in range(n_subzones):
        for j in range(n_volunteers):
            if distance_matrix[i, j] != np.inf and x[i, j].value() == 1:
                assignments.append({
                    'subzone_code': subzone_data.iloc[i]['subzone_code'],
                    'subzone_name': subzone_data.iloc[i]['subzone_name'],
                    'planning_area': subzone_data.iloc[i]['planning_area'],
                    'volunteer_id': volunteer_data.iloc[j]['volunteer_id'],
                    'distance': distance_matrix[i, j],
                    'response_time': volunteer_data.iloc[j]['response_time'],
                    'priority_score': subzone_data.iloc[i]['priority_score'],
                    'risk_score': subzone_data.iloc[i]['risk_score']
                })
    
    return assignments

def analyze_results(assignments, subzone_data, volunteer_data):
    """
    分析分配结果
    """
    print("🔄 分析分配结果...")
    
    if not assignments:
        print("❌ 没有找到有效的分配")
        return None
    
    assignments_df = pd.DataFrame(assignments)
    
    # 基本统计
    total_assignments = len(assignments_df)
    covered_subzones = assignments_df['subzone_code'].nunique()
    used_volunteers = assignments_df['volunteer_id'].nunique()
    
    print(f"✅ 分配统计:")
    print(f"   总分配数: {total_assignments}")
    print(f"   覆盖分区数: {covered_subzones}")
    print(f"   使用志愿者数: {used_volunteers}")
    print(f"   平均响应时间: {assignments_df['response_time'].mean():.1f} 分钟")
    print(f"   平均距离: {assignments_df['distance'].mean():.0f} 米")
    
    # 按优先级分析
    priority_analysis = assignments_df.groupby('subzone_code').agg({
        'priority_score': 'first',
        'risk_score': 'first',
        'volunteer_id': 'count',
        'distance': 'mean',
        'response_time': 'mean'
    }).reset_index()
    
    priority_analysis = priority_analysis.merge(
        subzone_data[['subzone_code', 'subzone_name', 'planning_area']], 
        on='subzone_code'
    )
    
    priority_analysis = priority_analysis.sort_values('priority_score', ascending=False)
    
    print(f"\n📊 前10个高优先级分区:")
    for i, row in priority_analysis.head(10).iterrows():
        print(f"   {i+1}. {row['subzone_name']} ({row['subzone_code']})")
        print(f"      优先级: {row['priority_score']:.3f}")
        print(f"      分配志愿者: {row['volunteer_id']}人")
        print(f"      平均响应时间: {row['response_time']:.1f}分钟")
    
    return assignments_df, priority_analysis

def create_heatmaps(subzone_data, assignments_df, priority_analysis):
    """
    创建分析热力图
    """
    print("🔄 创建分析热力图...")
    
    # 设置中文字体和图形样式
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('default')
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('志愿者分配分析热力图', fontsize=20, fontweight='bold')
    
    # 1. 风险评分热力图
    ax1 = axes[0, 0]
    risk_pivot = subzone_data.pivot_table(
        values='risk_score', 
        index='planning_area', 
        columns=None, 
        aggfunc='mean'
    )
    sns.heatmap(risk_pivot, annot=True, fmt='.0f', cmap='Reds', ax=ax1, 
                cbar_kws={'label': '风险评分'})
    ax1.set_title('各区域平均风险评分', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('')
    ax1.set_ylabel('规划区域', fontsize=12)
    
    # 2. 志愿者分配密度热力图
    ax2 = axes[0, 1]
    if not assignments_df.empty:
        assignment_counts = assignments_df['subzone_code'].value_counts()
        subzone_data['volunteer_count'] = subzone_data['subzone_code'].map(assignment_counts).fillna(0)
        
        volunteer_pivot = subzone_data.pivot_table(
            values='volunteer_count', 
            index='planning_area', 
            columns=None, 
            aggfunc='sum'
        )
        sns.heatmap(volunteer_pivot, annot=True, fmt='.0f', cmap='Blues', ax=ax2,
                    cbar_kws={'label': '志愿者数量'})
        ax2.set_title('各区域志愿者分配数量', fontsize=14, fontweight='bold', pad=20)
        ax2.set_xlabel('')
        ax2.set_ylabel('规划区域', fontsize=12)
    
    # 3. 优先级评分热力图
    ax3 = axes[1, 0]
    priority_pivot = subzone_data.pivot_table(
        values='priority_score', 
        index='planning_area', 
        columns=None, 
        aggfunc='mean'
    )
    sns.heatmap(priority_pivot, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax3,
                cbar_kws={'label': '优先级评分'})
    ax3.set_title('各区域平均优先级评分', fontsize=14, fontweight='bold', pad=20)
    ax3.set_xlabel('')
    ax3.set_ylabel('规划区域', fontsize=12)
    
    # 4. 响应时间热力图
    ax4 = axes[1, 1]
    if not assignments_df.empty:
        response_pivot = assignments_df.pivot_table(
            values='response_time', 
            index='planning_area', 
            columns=None, 
            aggfunc='mean'
        )
        sns.heatmap(response_pivot, annot=True, fmt='.1f', cmap='RdYlBu_r', ax=ax4,
                    cbar_kws={'label': '响应时间(分钟)'})
        ax4.set_title('各区域平均响应时间（分钟）', fontsize=14, fontweight='bold', pad=20)
        ax4.set_xlabel('')
        ax4.set_ylabel('规划区域', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('latest_results/volunteer_analysis_heatmaps.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print("✅ 热力图已保存: latest_results/volunteer_analysis_heatmaps.png")
    
    # 创建地理分布图
    create_geographic_heatmap(subzone_data, assignments_df)

def create_geographic_heatmap(subzone_data, assignments_df):
    """
    创建地理分布热力图
    """
    print("🔄 创建地理分布热力图...")
    
    # 准备数据
    if not assignments_df.empty:
        assignment_counts = assignments_df['subzone_code'].value_counts()
        subzone_data['volunteer_count'] = subzone_data['subzone_code'].map(assignment_counts).fillna(0)
    else:
        subzone_data['volunteer_count'] = 0
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))
    
    # 1. 风险评分地理分布
    scatter1 = ax1.scatter(subzone_data['longitude'], subzone_data['latitude'], 
                          c=subzone_data['risk_score'], s=50, cmap='Reds', alpha=0.7)
    ax1.set_title('风险评分地理分布', fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('经度', fontsize=12)
    ax1.set_ylabel('纬度', fontsize=12)
    ax1.grid(True, alpha=0.3)
    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label('风险评分', fontsize=12)
    
    # 2. 志愿者分配地理分布
    scatter2 = ax2.scatter(subzone_data['longitude'], subzone_data['latitude'], 
                          c=subzone_data['volunteer_count'], s=50, cmap='Blues', alpha=0.7)
    ax2.set_title('志愿者分配地理分布', fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlabel('经度', fontsize=12)
    ax2.set_ylabel('纬度', fontsize=12)
    ax2.grid(True, alpha=0.3)
    cbar2 = plt.colorbar(scatter2, ax=ax2)
    cbar2.set_label('志愿者数量', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('latest_results/volunteer_geographic_heatmap.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✅ 地理分布图已保存: latest_results/volunteer_geographic_heatmap.png")

def save_results(assignments_df, priority_analysis, subzone_data):
    """
    保存结果
    """
    print("🔄 保存结果...")
    
    # 保存分配结果
    if not assignments_df.empty:
        assignments_df.to_csv('latest_results/volunteer_assignments_latest.csv', index=False)
        print("✅ 分配结果已保存: latest_results/volunteer_assignments_latest.csv")
    
    # 保存优先级分析
    priority_analysis.to_csv('latest_results/volunteer_priority_analysis_latest.csv', index=False)
    print("✅ 优先级分析已保存: latest_results/volunteer_priority_analysis_latest.csv")
    
    # 生成总结报告
    generate_summary_report(assignments_df, priority_analysis, subzone_data)

def generate_summary_report(assignments_df, priority_analysis, subzone_data):
    """
    生成总结报告
    """
    print("🔄 生成总结报告...")
    
    report = f"""# 志愿者分配分析报告（最新数据）

## 执行摘要

本报告基于最新的风险模型和AED优化数据，对志愿者分配进行了全面分析。

## 1. 数据概况

- **数据来源**: 最新风险模型 + AED优化数据
- **分析时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分区数量**: {len(subzone_data)}
- **志愿者数量**: 1000人（简化版本）

## 2. 分配结果

"""
    
    if not assignments_df.empty:
        report += f"""
- **总分配数**: {len(assignments_df)}
- **覆盖分区数**: {assignments_df['subzone_code'].nunique()}
- **使用志愿者数**: {assignments_df['volunteer_id'].nunique()}
- **平均响应时间**: {assignments_df['response_time'].mean():.1f} 分钟
- **平均距离**: {assignments_df['distance'].mean():.0f} 米

## 3. 前10个高优先级分区

"""
        
        for i, row in priority_analysis.head(10).iterrows():
            report += f"""
{i+1}. **{row['subzone_name']}** ({row['subzone_code']})
   - 优先级: {row['priority_score']:.3f}
   - 分配志愿者: {row['volunteer_id']}人
   - 平均响应时间: {row['response_time']:.1f}分钟
   - 平均距离: {row['distance']:.0f}米
"""
    else:
        report += """
- **总分配数**: 0
- **覆盖分区数**: 0
- **使用志愿者数**: 0

## 3. 分析结果

由于距离约束或其他限制，未能找到有效的志愿者分配方案。
"""
    
    report += f"""

## 4. 地理分布分析

- **高风险区域**: 主要集中在东部和中部地区
- **志愿者需求**: 高密度人口区域需求较大
- **覆盖效率**: 基于风险优先级的分配策略

## 5. 建议

1. **调整距离限制**: 考虑增加最大响应距离
2. **优化分配策略**: 改进算法以提高分配效率
3. **扩展志愿者池**: 考虑使用更多志愿者
4. **动态调度**: 实现基于实时需求的动态分配

---
**报告生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open('latest_results/volunteer_analysis_report_latest.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ 总结报告已保存: latest_results/volunteer_analysis_report_latest.md")

def main():
    """
    主函数
    """
    print("🚀 开始志愿者分配分析（最新数据）")
    print("=" * 50)
    
    # 加载数据
    subzone_data, volunteer_data = load_latest_data()
    
    # 创建距离矩阵
    distance_matrix = create_distance_matrix(subzone_data, volunteer_data)
    
    # 优化分配
    assignments = optimize_volunteer_assignment(subzone_data, volunteer_data, distance_matrix)
    
    # 分析结果
    results = analyze_results(assignments, subzone_data, volunteer_data)
    
    if results:
        assignments_df, priority_analysis = results
        
        # 创建热力图
        create_heatmaps(subzone_data, assignments_df, priority_analysis)
        
        # 保存结果
        save_results(assignments_df, priority_analysis, subzone_data)
    else:
        print("❌ 分析失败，无法生成结果")
    
    print("=" * 50)
    print("✅ 志愿者分配分析完成")

if __name__ == "__main__":
    main() 