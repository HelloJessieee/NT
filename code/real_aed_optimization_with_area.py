import pandas as pd
import numpy as np
from geopy.distance import geodesic
from pulp import *
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """
    加载数据并计算人口密度
    """
    print("🔄 加载数据...")
    
    # 读取现有数据
    subzone_data = pd.read_csv("sg_subzone_all_features.csv")
    print(f"✅ 加载分区数据: {len(subzone_data)} 个分区")
    
    # 计算人口密度（使用人口总数作为代理，因为没有准确面积）
    # 这里我们使用人口密度的倒数作为"面积"的代理
    # 人口密度越高，说明区域越小或人口越密集，AED效果越好
    subzone_data['population_density_proxy'] = subzone_data['Total_Total']
    
    # 标准化人口密度
    subzone_data['normalized_density'] = subzone_data['population_density_proxy'] / subzone_data['population_density_proxy'].max()
    
    # 计算"面积权重" - 人口密度越高，权重越大（表示区域越重要）
    subzone_data['area_weight'] = subzone_data['normalized_density']
    
    print(f"✅ 数据加载完成")
    print(f"   总人口: {subzone_data['Total_Total'].sum():,.0f}")
    print(f"   平均人口密度: {subzone_data['population_density_proxy'].mean():.0f}")
    print(f"   最高人口密度: {subzone_data['population_density_proxy'].max():.0f}")
    
    return subzone_data

def create_coverage_matrix(subzone_data, coverage_radius=200):
    """
    创建覆盖矩阵，考虑人口密度权重
    """
    print(f"🔄 创建覆盖矩阵 (半径: {coverage_radius}m)...")
    
    n = len(subzone_data)
    matrix = np.zeros((n, n), dtype=int)
    
    for i in range(n):
        for j in range(n):
            if i != j:
                # 计算两个分区中心点之间的距离
                point1 = (subzone_data.iloc[i]['latitude'], subzone_data.iloc[i]['longitude'])
                point2 = (subzone_data.iloc[j]['latitude'], subzone_data.iloc[j]['longitude'])
                distance = geodesic(point1, point2).meters
                
                # 如果在覆盖半径内，标记为可覆盖
                if distance <= coverage_radius:
                    matrix[i, j] = 1
    
    print(f"✅ 覆盖矩阵创建完成: {matrix.shape}")
    print(f"   平均每个分区可覆盖其他分区数: {matrix.sum(axis=1).mean():.1f}")
    
    return matrix

def area_weighted_multi_cover_deployment(subzone_data, coverage_matrix, total_aeds):
    """
    基于面积权重的多重覆盖最大化部署
    目标：最大化 sum(覆盖次数 * 风险评分 * 面积权重)
    """
    print("🚩 基于面积权重的多重覆盖最大化部署...")
    
    n = len(subzone_data)
    risk_scores = subzone_data['normalized_density'].values  # 使用人口密度作为风险评分
    area_weights = subzone_data['area_weight'].values  # 面积权重
    
    # 创建优化问题
    prob = LpProblem("Area_Weighted_Multi_Covering_AED_Deployment", LpMaximize)
    
    # 决策变量：每个分区部署的AED数量
    x = LpVariable.dicts("deploy", range(n), lowBound=0, cat=LpInteger)
    
    # 目标函数：最大化加权覆盖效果
    # 对于每个分区i，计算被覆盖的次数 * 风险评分 * 面积权重
    prob += lpSum([
        lpSum([x[j] for j in range(n) if coverage_matrix[i, j] == 1]) * risk_scores[i] * area_weights[i]
        for i in range(n)
    ])
    
    # 约束：总部署数量等于现有总数
    prob += lpSum([x[j] for j in range(n)]) == total_aeds
    
    # 求解
    print("🔄 求解优化问题...")
    prob.solve()
    
    if prob.status == 1:  # 最优解
        print("✅ 优化求解成功")
        
        # 提取结果
        deployment = [int(x[j].value()) for j in range(n)]
        
        # 计算覆盖效果
        coverage_effect = []
        for i in range(n):
            covered_times = sum([deployment[j] for j in range(n) if coverage_matrix[i, j] == 1])
            effect = covered_times * risk_scores[i] * area_weights[i]
            coverage_effect.append(effect)
        
        # 统计结果
        deployed_count = sum(deployment)
        deployed_subzones = sum([1 for d in deployment if d > 0])
        total_effect = sum(coverage_effect)
        
        print(f"✅ 基于面积权重的多重覆盖最大化部署完成")
        print(f"   实际部署AED数量: {deployed_count} (分区数: {deployed_subzones})")
        print(f"   总加权覆盖效果: {total_effect:.2f}")
        
        return deployment, coverage_effect
        
    else:
        print(f"❌ 优化求解失败: {prob.status}")
        return None, None

def analyze_results(subzone_data, deployment, coverage_effect):
    """
    分析优化结果
    """
    print("\n📊 结果分析:")
    
    # 添加结果到数据框
    subzone_data['deployed_aeds'] = deployment
    subzone_data['coverage_effect'] = coverage_effect
    
    # 找出部署AED最多的分区
    top_deployed = subzone_data.nlargest(5, 'deployed_aeds')
    print(f"\n🏆 部署AED最多的分区:")
    for _, row in top_deployed.iterrows():
        print(f"   {row['subzone_name']}: {row['deployed_aeds']} 台AED")
        print(f"     人口密度: {row['population_density_proxy']:.0f}")
        print(f"     覆盖效果: {row['coverage_effect']:.2f}")
    
    # 找出覆盖效果最好的分区
    top_effect = subzone_data.nlargest(5, 'coverage_effect')
    print(f"\n🏆 覆盖效果最好的分区:")
    for _, row in top_effect.iterrows():
        print(f"   {row['subzone_name']}: 效果 {row['coverage_effect']:.2f}")
        print(f"     部署AED: {row['deployed_aeds']} 台")
        print(f"     人口密度: {row['population_density_proxy']:.0f}")
    
    # 保存结果
    result_file = "outputs/aed_optimization_with_area_weights.csv"
    subzone_data.to_csv(result_file, index=False)
    print(f"\n📁 结果已保存: {result_file}")
    
    return subzone_data

def generate_area_optimization_report(subzone_data, deployment, coverage_effect):
    """
    生成基于面积权重的优化报告
    """
    print("\n📝 生成优化报告...")
    
    report = f"""# AED部署优化报告 - 基于面积权重

## 优化目标
最大化加权覆盖效果：sum(覆盖次数 × 风险评分 × 面积权重)

## 数学模型

### 决策变量
- x_j: 在分区j部署的AED数量 (j = 1, 2, ..., n)

### 目标函数
maximize: Σ(i=1 to n) [Σ(j=1 to n) (cover_ij × x_j)] × risk_i × area_weight_i

其中：
- cover_ij: 分区j的AED是否能覆盖分区i (0或1)
- risk_i: 分区i的风险评分
- area_weight_i: 分区i的面积权重

### 约束条件
- Σ(j=1 to n) x_j = 总AED数量
- x_j ≥ 0 且为整数

## 优化结果

### 部署统计
- 总部署AED数量: {sum(deployment)}
- 有部署的分区数量: {sum([1 for d in deployment if d > 0])}
- 总加权覆盖效果: {sum(coverage_effect):.2f}

### 面积权重说明
- 使用人口密度作为面积代理
- 人口密度越高，表示区域越重要（面积小或人口密集）
- 高密度区域获得更高的优化权重

### 几何考虑
- 覆盖半径: 200米
- 距离计算: 使用Haversine公式
- 权重计算: 基于人口密度的标准化权重

## 结论
基于面积权重的优化模型能够：
1. 优先考虑人口密集区域
2. 平衡覆盖范围和部署密度
3. 最大化整体AED覆盖效果
"""
    
    # 保存报告
    with open("outputs/aed_optimization_with_area_weights_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ 优化报告已生成: outputs/aed_optimization_with_area_weights_report.md")

def main():
    """
    主函数
    """
    print("🎯 AED部署优化 - 基于面积权重")
    print("=" * 50)
    
    # 加载数据
    subzone_data = load_data()
    
    # 创建覆盖矩阵
    coverage_matrix = create_coverage_matrix(subzone_data, coverage_radius=200)
    
    # 执行基于面积权重的优化
    total_aeds = subzone_data['AED_count'].sum()
    deployment, coverage_effect = area_weighted_multi_cover_deployment(
        subzone_data, coverage_matrix, total_aeds
    )
    
    if deployment is not None:
        # 分析结果
        result_data = analyze_results(subzone_data, deployment, coverage_effect)
        
        # 生成报告
        generate_area_optimization_report(subzone_data, deployment, coverage_effect)
        
        print("\n🎉 基于面积权重的AED优化完成！")
    else:
        print("\n❌ 优化失败")

if __name__ == "__main__":
    main() 