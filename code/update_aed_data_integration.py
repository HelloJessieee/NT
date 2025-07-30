import pandas as pd
import numpy as np
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

def integrate_aed_data():
    """
    整合正确的AED数据到现有的数据集中
    """
    print("🔄 开始整合AED数据...")
    
    # 读取现有数据
    try:
        subzone_data = pd.read_csv("sg_subzone_all_features.csv")
        aed_data = pd.read_csv("data/AEDLocations_with_coords.csv")
        print(f"✅ 加载数据成功")
        print(f"   分区数据: {len(subzone_data)} 个分区")
        print(f"   AED数据: {len(aed_data)} 个AED位置")
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return False
    
    # 按邮政编码分组AED数据，计算每个分区的AED数量
    aed_counts = aed_data.groupby('Postal_Code').size().reset_index(name='aed_count')
    
    # 由于我们没有邮政编码到分区的映射，我们需要基于地理坐标来分配AED
    # 使用现有的分区坐标来计算每个AED属于哪个分区
    
    # 计算每个AED到每个分区的距离，分配到最近的分区
    aed_assignments = []
    
    for _, aed in aed_data.iterrows():
        min_distance = float('inf')
        closest_subzone = None
        
        for _, subzone in subzone_data.iterrows():
            # 计算距离（使用Haversine公式）
            distance = geodesic(
                (aed['latitude'], aed['longitude']),
                (subzone['latitude'], subzone['longitude'])
            ).meters
            
            if distance < min_distance:
                min_distance = distance
                closest_subzone = subzone['subzone_code']
        
        aed_assignments.append({
            'aed_id': len(aed_assignments),
            'postal_code': aed['Postal_Code'],
            'building_name': aed['Building_Name'],
            'latitude': aed['latitude'],
            'longitude': aed['longitude'],
            'assigned_subzone': closest_subzone,
            'distance_to_centroid': min_distance
        })
    
    # 创建AED分配DataFrame
    aed_assignments_df = pd.DataFrame(aed_assignments)
    
    # 计算每个分区的AED数量
    subzone_aed_counts = aed_assignments_df.groupby('assigned_subzone').size().reset_index(name='actual_aed_count')
    subzone_aed_counts.columns = ['subzone_code', 'actual_aed_count']
    
    # 合并到现有数据
    updated_data = subzone_data.merge(subzone_aed_counts, on='subzone_code', how='left').fillna(0)
    
    # 更新AED_count列
    updated_data['AED_count'] = updated_data['actual_aed_count'].astype(int)
    
    # 删除临时列
    updated_data = updated_data.drop('actual_aed_count', axis=1)
    
    # 保存更新后的数据
    updated_data.to_csv("sg_subzone_all_features_updated.csv", index=False)
    
    # 保存AED分配数据
    aed_assignments_df.to_csv("outputs/aed_subzone_assignments.csv", index=False)
    
    # 生成统计报告
    total_aeds = len(aed_data)
    assigned_aeds = len(aed_assignments_df)
    covered_subzones = len(subzone_aed_counts[subzone_aed_counts['actual_aed_count'] > 0])
    
    print(f"\n📊 AED数据整合完成:")
    print(f"   总AED数量: {total_aeds}")
    print(f"   已分配AED: {assigned_aeds}")
    print(f"   覆盖分区数: {covered_subzones}")
    print(f"   平均每个分区AED数: {assigned_aeds/len(subzone_data):.2f}")
    
    # 显示AED数量最多的前10个分区
    top_aed_subzones = subzone_aed_counts.nlargest(10, 'actual_aed_count')
    print(f"\n🏆 AED数量最多的分区:")
    for _, row in top_aed_subzones.iterrows():
        subzone_name = updated_data[updated_data['subzone_code'] == row['subzone_code']]['subzone_name'].iloc[0]
        print(f"   {row['subzone_code']} ({subzone_name}): {row['actual_aed_count']} 个AED")
    
    # 显示没有AED的分区数量
    no_aed_subzones = len(subzone_aed_counts[subzone_aed_counts['actual_aed_count'] == 0])
    print(f"\n⚠️  没有AED的分区: {no_aed_subzones} 个")
    
    return True

def create_aed_optimization_data():
    """
    为AED优化创建专门的数据集
    """
    print("\n🔄 创建AED优化数据集...")
    
    # 读取更新后的数据
    data = pd.read_csv("sg_subzone_all_features_updated.csv")
    
    # 创建AED优化所需的数据结构
    aed_optimization_data = {
        'subzones': data[['subzone_code', 'subzone_name', 'latitude', 'longitude', 'Total_Total', 'AED_count']].copy(),
        'risk_scores': data[['subzone_code', 'subzone_name', 'Total_Total', 'volunteers_count', 'hdb_ratio', 'elderly_ratio', 'low_income_ratio']].copy()
    }
    
    # 计算风险评分（简化版）
    aed_optimization_data['risk_scores']['risk_score'] = (
        aed_optimization_data['risk_scores']['Total_Total'] * 0.4 +
        aed_optimization_data['risk_scores']['elderly_ratio'] * 0.3 +
        aed_optimization_data['risk_scores']['low_income_ratio'] * 0.2 +
        (1 - aed_optimization_data['risk_scores']['volunteers_count']) * 0.1
    )
    
    # 标准化风险评分
    aed_optimization_data['risk_scores']['risk_score'] = (
        aed_optimization_data['risk_scores']['risk_score'] - 
        aed_optimization_data['risk_scores']['risk_score'].min()
    ) / (
        aed_optimization_data['risk_scores']['risk_score'].max() - 
        aed_optimization_data['risk_scores']['risk_score'].min()
    )
    
    # 保存优化数据
    aed_optimization_data['subzones'].to_csv("outputs/aed_optimization_subzones.csv", index=False)
    aed_optimization_data['risk_scores'].to_csv("outputs/aed_optimization_risk_scores.csv", index=False)
    
    print("✅ AED优化数据集创建完成")
    print(f"   分区数据: outputs/aed_optimization_subzones.csv")
    print(f"   风险评分: outputs/aed_optimization_risk_scores.csv")
    
    return aed_optimization_data

if __name__ == "__main__":
    # 创建输出目录
    import os
    os.makedirs("outputs", exist_ok=True)
    
    # 整合AED数据
    success = integrate_aed_data()
    
    if success:
        # 创建优化数据集
        create_aed_optimization_data()
        print("\n🎉 AED数据整合完成！")
        print("📁 请查看以下文件:")
        print("   - sg_subzone_all_features_updated.csv (更新后的主数据集)")
        print("   - outputs/aed_subzone_assignments.csv (AED分配结果)")
        print("   - outputs/aed_optimization_subzones.csv (优化用分区数据)")
        print("   - outputs/aed_optimization_risk_scores.csv (优化用风险评分)")
    else:
        print("\n❌ AED数据整合失败") 