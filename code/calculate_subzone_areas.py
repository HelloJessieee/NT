import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import re
import warnings
warnings.filterwarnings('ignore')

def extract_subzone_name_from_html(html_content):
    """
    从HTML格式的Description中提取分区名称
    """
    # 使用正则表达式提取SUBZONE_N的值
    pattern = r'<th>SUBZONE_N</th>\s*<td>([^<]+)</td>'
    match = re.search(pattern, html_content)
    if match:
        return match.group(1).strip()
    return None

def calculate_subzone_areas():
    """
    计算每个分区的面积，并更新数据集
    """
    print("🔄 计算分区面积...")
    
    try:
        # 读取地理边界数据
        gdf = gpd.read_file("MasterPlan2019SubzoneBoundaryNoSea/Master Plan 2019 Subzone Boundary (No Sea) (GEOJSON).geojson")
        print(f"✅ 加载地理边界数据: {len(gdf)} 个分区")
        
        # 从Description中提取分区名称
        gdf['subzone_name'] = gdf['Description'].apply(extract_subzone_name_from_html)
        
        # 检查提取结果
        missing_names = gdf[gdf['subzone_name'].isna()]
        if len(missing_names) > 0:
            print(f"⚠️  警告: {len(missing_names)} 个分区无法提取名称")
        else:
            print(f"✅ 成功提取所有分区名称")
        
        # 设置正确的坐标参考系统 (EPSG:3414 - Singapore TM)
        # 新加坡使用EPSG:3414作为本地投影坐标系
        gdf = gdf.set_crs(epsg=4326)  # 先设置为WGS84
        gdf_projected = gdf.to_crs(epsg=3414)  # 转换为新加坡TM投影
        
        # 计算面积（平方米）
        gdf_projected['area_sq_m'] = gdf_projected.geometry.area
        gdf_projected['area_sq_km'] = gdf_projected['area_sq_m'] / 1000000
        
        # 读取现有数据
        subzone_data = pd.read_csv("sg_subzone_all_features.csv")
        print(f"✅ 加载现有数据: {len(subzone_data)} 个分区")
        
        # 合并面积数据
        area_data = gdf_projected[['subzone_name', 'area_sq_km', 'area_sq_m']].copy()
        
        # 合并数据
        updated_data = subzone_data.merge(area_data, on='subzone_name', how='left')
        
        # 检查合并结果
        missing_areas = updated_data[updated_data['area_sq_km'].isna()]
        if len(missing_areas) > 0:
            print(f"⚠️  警告: {len(missing_areas)} 个分区缺少面积数据")
            print("   缺少面积的分区:")
            for _, row in missing_areas.head(5).iterrows():
                print(f"     {row['subzone_name']}")
        
        # 计算人口密度
        updated_data['population_density'] = updated_data['Total_Total'] / updated_data['area_sq_km']
        
        # 保存更新后的数据
        updated_data.to_csv("sg_subzone_all_features_with_area.csv", index=False)
        
        # 生成统计报告
        print(f"\n📊 面积统计:")
        print(f"   总面积: {updated_data['area_sq_km'].sum():.2f} 平方公里")
        print(f"   平均分区面积: {updated_data['area_sq_km'].mean():.2f} 平方公里")
        print(f"   最大分区面积: {updated_data['area_sq_km'].max():.2f} 平方公里")
        print(f"   最小分区面积: {updated_data['area_sq_km'].min():.2f} 平方公里")
        
        print(f"\n📊 人口密度统计:")
        print(f"   平均人口密度: {updated_data['population_density'].mean():.0f} 人/平方公里")
        print(f"   最高人口密度: {updated_data['population_density'].max():.0f} 人/平方公里")
        print(f"   最低人口密度: {updated_data['population_density'].min():.0f} 人/平方公里")
        
        # 显示面积最大的前5个分区
        print(f"\n🏆 面积最大的分区:")
        largest_areas = updated_data.nlargest(5, 'area_sq_km')
        for _, row in largest_areas.iterrows():
            print(f"   {row['subzone_name']}: {row['area_sq_km']:.2f} 平方公里")
        
        # 显示人口密度最高的前5个分区
        print(f"\n🏆 人口密度最高的分区:")
        highest_density = updated_data.nlargest(5, 'population_density')
        for _, row in highest_density.iterrows():
            print(f"   {row['subzone_name']}: {row['population_density']:.0f} 人/平方公里")
        
        return updated_data
        
    except Exception as e:
        print(f"❌ 计算面积失败: {e}")
        return None

if __name__ == "__main__":
    result = calculate_subzone_areas()
    if result is not None:
        print("\n✅ 分区面积计算完成！")
        print("📁 更新后的数据文件: sg_subzone_all_features_with_area.csv")
    else:
        print("\n❌ 分区面积计算失败") 