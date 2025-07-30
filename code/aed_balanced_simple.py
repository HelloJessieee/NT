import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """
    加载数据并准备AED优化
    """
    print("🔄 加载数据...")
    
    # 读取分区数据
    subzone_data = pd.read_csv("sg_subzone_all_features.csv")
    print(f"✅ 加载分区数据: {len(subzone_data)} 个分区")
    
    # 计算面积权重（使用人口密度作为代理）
    subzone_data['population_density_proxy'] = subzone_data['Total_Total']
    subzone_data['normalized_density'] = subzone_data['population_density_proxy'] / subzone_data['population_density_proxy'].max()
    subzone_data['area_weight'] = subzone_data['normalized_density']
    
    # 计算风险评分（如果没有，使用人口密度作为代理）
    if 'risk_score' not in subzone_data.columns:
        subzone_data['risk_score'] = (
            subzone_data['Total_Total'] * 0.4 +
            subzone_data['elderly_ratio'] * 10000 * 0.3 +
            subzone_data['low_income_ratio'] * 10000 * 0.3
        )
    
    # 标准化风险评分
    subzone_data['normalized_risk_score'] = (subzone_data['risk_score'] - subzone_data['risk_score'].min()) / (subzone_data['risk_score'].max() - subzone_data['risk_score'].min())
    
    print(f"✅ 数据加载完成")
    print(f"   总AED数量: {subzone_data['AED_count'].sum()}")
    
    return subzone_data

def balanced_aed_allocation(subzone_data):
    """
    平衡的AED分配算法
    """
    print("🚩 基于面积权重的平衡AED分配...")
    
    total_aeds = subzone_data['AED_count'].sum()
    n_subzones = len(subzone_data)
    
    print(f"   总AED数量: {total_aeds}")
    print(f"   分区数量: {n_subzones}")
    
    # 计算每个分区的优先级分数
    priority_scores = subzone_data['normalized_risk_score'] * subzone_data['area_weight']
    
    # 基础分配：每个分区至少1台AED
    base_allocation = np.ones(n_subzones, dtype=int)
    remaining_aeds = total_aeds - n_subzones
    
    print(f"   基础分配: {n_subzones} 台AED (每个分区1台)")
    print(f"   剩余AED: {remaining_aeds} 台")
    
    # 按优先级分配剩余AED
    if remaining_aeds > 0:
        # 按优先级排序
        priority_indices = np.argsort(priority_scores)[::-1]
        
        # 计算每个分区的额外分配
        for i, idx in enumerate(priority_indices):
            if remaining_aeds <= 0:
                break
            
            # 计算这个分区应该获得的额外AED数量
            # 高优先级分区获得更多
            priority_rank = i + 1
            if priority_rank <= n_subzones * 0.2:  # 前20%高优先级
                extra_aeds = min(remaining_aeds, 5)
            elif priority_rank <= n_subzones * 0.5:  # 前50%中优先级
                extra_aeds = min(remaining_aeds, 3)
            else:  # 其他分区
                extra_aeds = min(remaining_aeds, 1)
            
            base_allocation[idx] += extra_aeds
            remaining_aeds -= extra_aeds
    
    # 计算覆盖效果
    coverage_effect = []
    for i in range(n_subzones):
        effect = base_allocation[i] * subzone_data.iloc[i]['normalized_risk_score'] * subzone_data.iloc[i]['area_weight']
        coverage_effect.append(effect)
    
    print(f"✅ 平衡AED分配完成")
    print(f"   实际分配AED数量: {sum(base_allocation)}")
    print(f"   平均每个分区AED数: {np.mean(base_allocation):.1f}")
    print(f"   最多AED分区: {max(base_allocation)} 台")
    print(f"   最少AED分区: {min(base_allocation)} 台")
    
    return base_allocation, coverage_effect

def analyze_balanced_results(subzone_data, deployment, coverage_effect):
    """
    分析平衡分配结果
    """
    print("\n📊 结果分析:")
    
    # 添加结果到数据框
    subzone_data['deployed_aeds'] = deployment
    subzone_data['coverage_effect'] = coverage_effect
    
    # 统计分配情况
    print(f"\n📈 分配统计:")
    print(f"   总AED数量: {sum(deployment)}")
    print(f"   有AED的分区数: {sum([1 for d in deployment if d > 0])}")
    print(f"   平均每个分区AED数: {np.mean(deployment):.1f}")
    print(f"   最多AED分区: {max(deployment)} 台")
    print(f"   最少AED分区: {min(deployment)} 台")
    print(f"   标准差: {np.std(deployment):.1f}")
    
    # 分配分布分析
    aed_distribution = pd.Series(deployment).value_counts().sort_index()
    print(f"\n📊 AED分配分布:")
    for aed_count, subzone_count in aed_distribution.items():
        print(f"   {aed_count} 台AED: {subzone_count} 个分区")
    
    # 找出部署AED最多的分区
    top_deployed = subzone_data.nlargest(10, 'deployed_aeds')
    print(f"\n🏆 部署AED最多的分区:")
    for _, row in top_deployed.iterrows():
        print(f"   {row['subzone_name']}: {row['deployed_aeds']} 台AED")
        print(f"     人口密度: {row['population_density_proxy']:.0f}")
        print(f"     覆盖效果: {row['coverage_effect']:.2f}")
    
    # 找出覆盖效果最好的分区
    top_effect = subzone_data.nlargest(10, 'coverage_effect')
    print(f"\n🏆 覆盖效果最好的分区:")
    for _, row in top_effect.iterrows():
        print(f"   {row['subzone_name']}: 效果 {row['coverage_effect']:.2f}")
        print(f"     部署AED: {row['deployed_aeds']} 台")
        print(f"     人口密度: {row['population_density_proxy']:.0f}")
    
    # 保存结果
    result_file = "outputs/aed_optimization_balanced_simple.csv"
    subzone_data.to_csv(result_file, index=False)
    print(f"\n📁 结果已保存: {result_file}")
    
    return subzone_data

def generate_balanced_simple_report(subzone_data, deployment, coverage_effect):
    """
    生成平衡分配报告
    """
    print("\n📝 生成优化报告...")
    
    report = f"""# AED部署优化报告 - 平衡简单版本

## 优化概述
- **优化目标**: 平衡分配AED，确保每个分区都有覆盖
- **总AED数量**: {sum(deployment)}
- **覆盖分区数**: {sum([1 for d in deployment if d > 0])}
- **总加权效果**: {sum(coverage_effect):.2f}

## 分配策略
1. **基础分配**: 每个分区至少1台AED
2. **优先级分配**: 按风险评分×面积权重排序
3. **分层分配**: 
   - 前20%高优先级分区: 最多6台AED (1+5)
   - 前50%中优先级分区: 最多4台AED (1+3)
   - 其他分区: 最多2台AED (1+1)

## 分配特点
- **平均每个分区**: {np.mean(deployment):.1f} 台AED
- **最少分配**: {min(deployment)} 台AED
- **最多分配**: {max(deployment)} 台AED
- **分配标准差**: {np.std(deployment):.1f}

## 前10个高优先级分区
"""
    
    # 添加前10个高优先级分区
    top_10 = subzone_data.nlargest(10, 'coverage_effect')
    for i, (_, row) in enumerate(top_10.iterrows(), 1):
        report += f"{i}. **{row['subzone_name']}** - AED: {int(row['deployed_aeds'])}, 效果: {row['coverage_effect']:.2f}\n"
    
    report += f"""
## 优化特点
1. **全覆盖**: 每个分区至少分配1台AED
2. **平衡分配**: 避免过度集中，最多6台AED
3. **面积权重考虑**: 使用人口密度作为区域面积的代理权重
4. **风险导向**: 高风险区域获得更多AED分配
5. **简单高效**: 无需复杂优化算法，直接分配

## 输出文件
- `aed_optimization_balanced_simple.csv`: 详细优化结果
"""
    
    with open("outputs/aed_optimization_balanced_simple_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ 优化报告生成完成")

def main():
    """
    主函数
    """
    print("🎯 AED部署优化 - 平衡简单版本")
    print("=" * 50)
    
    # 加载数据
    subzone_data = load_data()
    
    # 平衡AED分配
    deployment, coverage_effect = balanced_aed_allocation(subzone_data)
    
    if deployment is not None:
        # 分析结果
        subzone_data = analyze_balanced_results(subzone_data, deployment, coverage_effect)
        
        # 生成报告
        generate_balanced_simple_report(subzone_data, deployment, coverage_effect)
        
        print("\n🎉 基于面积权重的平衡AED部署优化完成！")
    else:
        print("\n❌ 优化失败")

if __name__ == "__main__":
    main() 