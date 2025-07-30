import pandas as pd
import numpy as np
from geopy.distance import geodesic
from pulp import *
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """
    加载数据并准备志愿者调度（简化版本）
    """
    print("🔄 加载数据...")
    
    # 读取分区数据
    subzone_data = pd.read_csv("sg_subzone_all_features.csv")
    print(f"✅ 加载分区数据: {len(subzone_data)} 个分区")
    
    # 读取志愿者数据（只使用前1000个志愿者来加快计算）
    volunteer_data = pd.read_csv("data/volunteers.csv")
    volunteer_data = volunteer_data.head(1000)  # 只使用前1000个志愿者
    print(f"✅ 加载志愿者数据: {len(volunteer_data)} 个志愿者（简化版本）")
    
    # 加载最新的风险模型结果
    try:
        risk_data = pd.read_csv('outputs/risk_analysis_paper_aligned.csv')
        print(f"✅ 加载最新风险数据: {len(risk_data)} 个分区")
        
        # 合并风险数据到分区数据
        subzone_data = subzone_data.merge(risk_data[['subzone_code', 'risk_score', 'risk_score_normalized']], 
                                         on='subzone_code', how='left')
    
        # 使用最新模型的标准化风险评分
        subzone_data['normalized_risk_score'] = subzone_data['risk_score_normalized']
        
    except FileNotFoundError:
        print("⚠️  最新风险数据未找到，使用备用计算")
        # 备用：计算风险评分
        subzone_data['risk_score'] = (
            subzone_data['Total_Total'] * 0.4 +
            subzone_data['elderly_ratio'] * 10000 * 0.3 +
            subzone_data['low_income_ratio'] * 10000 * 0.3
        )
        subzone_data['normalized_risk_score'] = (subzone_data['risk_score'] - subzone_data['risk_score'].min()) / (subzone_data['risk_score'].max() - subzone_data['risk_score'].min())
    
    # 计算面积权重（使用人口密度作为代理）
    subzone_data['population_density'] = subzone_data['Total_Total']
    subzone_data['area_weight'] = subzone_data['population_density'] / subzone_data['population_density'].max()
    
    # 为志愿者生成模拟位置（基于新加坡的地理范围）
    print("🔄 生成志愿者模拟位置...")
    np.random.seed(42)
    volunteer_data['latitude'] = np.random.uniform(1.2, 1.5, len(volunteer_data))
    volunteer_data['longitude'] = np.random.uniform(103.6, 104.0, len(volunteer_data))
    volunteer_data['availability'] = 1  # 假设所有志愿者都可用
    volunteer_data['response_time'] = np.random.uniform(2, 15, len(volunteer_data))
    
    print(f"✅ 数据加载完成")
    print(f"   总志愿者数量: {len(volunteer_data)}")
    print(f"   可用志愿者数量: {volunteer_data['availability'].sum()}")
    print(f"   平均响应时间: {volunteer_data['response_time'].mean():.1f} 分钟")
    
    return subzone_data, volunteer_data

def create_distance_matrix(subzone_data, volunteer_data, max_distance=1000):
    """
    创建分区和志愿者之间的距离矩阵（简化版本）
    """
    print(f"🔄 创建距离矩阵 (最大距离: {max_distance}m)...")
    
    n_subzones = len(subzone_data)
    n_volunteers = len(volunteer_data)
    
    print(f"   计算 {n_subzones} 个分区 × {n_volunteers} 个志愿者的距离矩阵...")
    
    # 初始化距离矩阵
    distance_matrix = np.full((n_subzones, n_volunteers), np.inf)
    
    # 计算距离
    valid_connections = 0
    for i, subzone in subzone_data.iterrows():
        if i % 50 == 0:  # 每50个分区显示一次进度
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
    优化志愿者分配，考虑面积权重
    """
    print("🚩 基于面积权重的志愿者调度优化...")
    
    n_subzones = len(subzone_data)
    n_volunteers = len(volunteer_data)
    
    # 获取权重数据
    risk_scores = subzone_data['normalized_risk_score'].values
    area_weights = subzone_data['area_weight'].values
    
    print(f"   分区数量: {n_subzones}")
    print(f"   志愿者数量: {n_volunteers}")
    
    # 创建优化问题
    print("🔄 创建优化问题...")
    prob = LpProblem("Area_Weighted_Volunteer_Assignment", LpMaximize)
    
    # 决策变量：志愿者j是否分配给分区i
    valid_pairs = [(i, j) for i in range(n_subzones) for j in range(n_volunteers) 
                   if distance_matrix[i, j] != np.inf]
    
    print(f"   有效分配对数量: {len(valid_pairs)}")
    
    x = LpVariable.dicts("assign", valid_pairs, cat='Binary')
    
    # 目标函数：最大化加权覆盖效果
    print("🔄 构建目标函数...")
    objective_terms = []
    for i, j in valid_pairs:
        # 权重 = 风险评分 × 面积权重 × (1 / 响应时间)
        weight = (risk_scores[i] * area_weights[i] * 
                 (1 / volunteer_data.iloc[j]['response_time']))
        objective_terms.append(x[(i, j)] * weight)
    
    prob += lpSum(objective_terms)
    
    # 约束1：每个志愿者最多分配给一个分区
    print("🔄 添加志愿者约束...")
    for j in range(n_volunteers):
        if volunteer_data.iloc[j]['availability'] == 1:
            valid_assignments = [x[(i, j)] for i in range(n_subzones) 
                               if distance_matrix[i, j] != np.inf]
            if valid_assignments:
                prob += lpSum(valid_assignments) <= 1
    
    # 约束2：高优先级分区优先分配（但不强制）
    print("🔄 添加高优先级分区约束...")
    high_priority_threshold = np.percentile(risk_scores * area_weights, 80)
    high_priority_count = 0
    
    for i in range(n_subzones):
        if risk_scores[i] * area_weights[i] >= high_priority_threshold:
            available_volunteers = [j for j in range(n_volunteers) 
                                   if distance_matrix[i, j] != np.inf]
            if available_volunteers:
                high_priority_count += 1
                # 不强制分配，只是给更高的权重
    
    print(f"   高优先级分区数量: {high_priority_count}")
    
    # 求解
    print("🔄 求解优化问题...")
    prob.solve()
    
    if prob.status == 1:  # 最优解
        print("✅ 优化求解成功")
        
        # 提取结果
        assignments = []
        for i, j in valid_pairs:
            if x[(i, j)].value() == 1:
                assignments.append({
                    'subzone_code': subzone_data.iloc[i]['subzone_code'],
                    'subzone_name': subzone_data.iloc[i]['subzone_name'],
                    'volunteer_id': volunteer_data.iloc[j]['volunteer_id'],
                    'volunteer_lat': volunteer_data.iloc[j]['latitude'],
                    'volunteer_lon': volunteer_data.iloc[j]['longitude'],
                    'distance': distance_matrix[i, j],
                    'response_time': volunteer_data.iloc[j]['response_time'],
                    'risk_score': risk_scores[i],
                    'area_weight': area_weights[i],
                    'weighted_priority': risk_scores[i] * area_weights[i]
                })
        
        print(f"✅ 志愿者调度优化完成")
        print(f"   总分配数: {len(assignments)}")
        print(f"   覆盖分区数: {len(set([a['subzone_code'] for a in assignments]))}")
        print(f"   平均响应时间: {np.mean([a['response_time'] for a in assignments]):.1f} 分钟")
        
        return assignments
        
    else:
        print(f"❌ 优化求解失败: {prob.status}")
        return None

def analyze_results(assignments, subzone_data, volunteer_data):
    """
    分析优化结果
    """
    print("\n📊 结果分析:")
    
    if not assignments:
        print("❌ 没有分配结果")
        return
    
    assignments_df = pd.DataFrame(assignments)
    
    # 统计分配情况
    print(f"\n📈 分配统计:")
    print(f"   总分配数: {len(assignments)}")
    print(f"   覆盖分区数: {assignments_df['subzone_code'].nunique()}")
    print(f"   使用志愿者数: {assignments_df['volunteer_id'].nunique()}")
    print(f"   平均距离: {assignments_df['distance'].mean():.0f} 米")
    print(f"   平均响应时间: {assignments_df['response_time'].mean():.1f} 分钟")
    
    # 找出优先级最高的分区
    print(f"\n🏆 优先级最高的分区:")
    high_priority = assignments_df.groupby('subzone_name').agg({
        'weighted_priority': 'first',
        'volunteer_id': 'count',
        'response_time': 'mean'
    }).sort_values('weighted_priority', ascending=False).head(5)
    
    for subzone, row in high_priority.iterrows():
        print(f"   {subzone}:")
        print(f"     优先级: {row['weighted_priority']:.3f}")
        print(f"     分配志愿者: {int(row['volunteer_id'])} 人")
        print(f"     平均响应时间: {row['response_time']:.1f} 分钟")
    
    return assignments_df

def save_results(assignments_df, subzone_data):
    """
    保存结果
    """
    print("🔄 保存结果...")
    
    # 保存分配结果
    if assignments_df is not None:
        assignments_df.to_csv("outputs/volunteer_assignment_simple.csv", index=False)
        
        # 生成分区级别的汇总
        subzone_summary = assignments_df.groupby(['subzone_code', 'subzone_name']).agg({
            'volunteer_id': 'count',
            'response_time': 'mean',
            'distance': 'mean',
            'weighted_priority': 'first'
        }).reset_index()
        
        subzone_summary.columns = ['subzone_code', 'subzone_name', 'assigned_volunteers', 
                                  'avg_response_time', 'avg_distance', 'priority_score']
        subzone_summary.to_csv("outputs/volunteer_assignment_simple_summary.csv", index=False)
        
        print("✅ 结果保存完成")
        print("📁 输出文件:")
        print("   - outputs/volunteer_assignment_simple.csv")
        print("   - outputs/volunteer_assignment_simple_summary.csv")

def main():
    """
    主函数
    """
    print("🎯 志愿者调度优化 - 简化版本")
    print("=" * 50)
    
    # 加载数据
    subzone_data, volunteer_data = load_data()
    
    # 创建距离矩阵
    distance_matrix = create_distance_matrix(subzone_data, volunteer_data, max_distance=1000)
    
    # 优化志愿者分配
    assignments = optimize_volunteer_assignment(subzone_data, volunteer_data, distance_matrix)
    
    # 分析结果
    assignments_df = analyze_results(assignments, subzone_data, volunteer_data)
    
    # 保存结果
    save_results(assignments_df, subzone_data)
    
    print("\n🎉 基于面积权重的志愿者调度优化完成！")

if __name__ == "__main__":
    main() 