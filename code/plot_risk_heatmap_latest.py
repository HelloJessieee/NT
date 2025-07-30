#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于最新数据生成风险热力图散点图
使用最新的 risk_analysis_paper_aligned.csv 数据
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_latest_data():
    """加载最新的风险数据"""
    print('【日志】读取最新风险预测结果...')
    try:
        # 加载最新的风险数据
        risk_df = pd.read_csv('outputs/risk_analysis_paper_aligned.csv')
        print(f'【日志】读取到{len(risk_df)}条最新风险记录')
        
        # 加载分区地理信息
        subzone_info = pd.read_csv('sg_subzone_all_features.csv')
        print(f'【日志】读取到{len(subzone_info)}条分区地理信息')
        
        # 合并数据
        risk_df = risk_df.merge(subzone_info[['subzone_code', 'latitude', 'longitude', 'Total_Total']], 
                               on='subzone_code', how='left')
        
        # 使用人口密度作为大小指标
        risk_df['population_density'] = risk_df['Total_Total']
        
        return risk_df
        
    except Exception as e:
        print(f'【错误】读取数据失败: {e}')
        return None

def create_risk_heatmap(risk_df):
    """创建风险热力图散点图"""
    print('【日志】绘制最新风险热力图...')
    
    plt.figure(figsize=(12, 10))
    
    # 获取风险评分的统计信息
    risk_values = risk_df['risk_score_normalized'].values
    print(f"【日志】风险评分统计:")
    print(f"   - 最小值: {risk_values.min():.6f}")
    print(f"   - 最大值: {risk_values.max():.6f}")
    print(f"   - 平均值: {risk_values.mean():.6f}")
    print(f"   - 中位数: {np.median(risk_values):.6f}")
    print(f"   - 95%分位数: {np.percentile(risk_values, 95):.6f}")
    
    # 创建散点图，颜色表示风险分数，大小表示人口密度
    # 使用对数刻度或调整颜色映射范围
    scatter = plt.scatter(risk_df['longitude'], risk_df['latitude'], 
                         c=risk_df['risk_score_normalized'], 
                         s=risk_df['population_density']/100, 
                         cmap='Reds', alpha=0.7, edgecolors='black', linewidth=0.5,
                         vmin=0, vmax=np.percentile(risk_values, 95))  # 使用95%分位数作为上限
    
    # 添加颜色条
    cbar = plt.colorbar(scatter)
    cbar.set_label('Normalized Risk Score', fontsize=12)
    
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    plt.title('OHCA Risk Heatmap by Subzone (Latest Data)\n(Color: Risk Score, Size: Population Density)', fontsize=14)
    
    # 添加图例说明点的大小
    legend_elements = [
        plt.scatter([], [], c='red', s=100, alpha=0.7, label='Low Density'),
        plt.scatter([], [], c='red', s=300, alpha=0.7, label='Medium Density'),
        plt.scatter([], [], c='red', s=500, alpha=0.7, label='High Density')
    ]
    plt.legend(handles=legend_elements, title='Population Density', loc='upper right')
    
    plt.tight_layout()
    plt.savefig('outputs/risk_heatmap_latest_scatter.png', dpi=300, bbox_inches='tight')
    print('【日志】已保存最新风险热力图: outputs/risk_heatmap_latest_scatter.png')
    plt.close()
    
    print('【日志】最新风险热力图已完成。')

def create_risk_heatmap_alternative(risk_df):
    """创建改进版风险热力图散点图（使用对数刻度）"""
    print('【日志】绘制改进版风险热力图...')
    
    plt.figure(figsize=(12, 10))
    
    # 对风险评分进行对数变换以改善颜色分布
    risk_values = risk_df['risk_score_normalized'].values
    # 添加小常数避免log(0)
    log_risk = np.log(risk_values + 1e-6)
    
    print(f"【日志】对数变换后风险评分统计:")
    print(f"   - 最小值: {log_risk.min():.6f}")
    print(f"   - 最大值: {log_risk.max():.6f}")
    print(f"   - 平均值: {log_risk.mean():.6f}")
    
    # 创建散点图，使用对数变换的风险评分
    scatter = plt.scatter(risk_df['longitude'], risk_df['latitude'], 
                         c=log_risk, 
                         s=risk_df['population_density']/100, 
                         cmap='Reds', alpha=0.7, edgecolors='black', linewidth=0.5)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter)
    cbar.set_label('Log(Normalized Risk Score + 1e-6)', fontsize=12)
    
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    plt.title('OHCA Risk Heatmap by Subzone (Latest Data - Log Scale)\n(Color: Log Risk Score, Size: Population Density)', fontsize=14)
    
    # 添加图例说明点的大小
    legend_elements = [
        plt.scatter([], [], c='red', s=100, alpha=0.7, label='Low Density'),
        plt.scatter([], [], c='red', s=300, alpha=0.7, label='Medium Density'),
        plt.scatter([], [], c='red', s=500, alpha=0.7, label='High Density')
    ]
    plt.legend(handles=legend_elements, title='Population Density', loc='upper right')
    
    plt.tight_layout()
    plt.savefig('outputs/risk_heatmap_latest_scatter_log.png', dpi=300, bbox_inches='tight')
    print('【日志】已保存改进版风险热力图: outputs/risk_heatmap_latest_scatter_log.png')
    plt.close()
    
    print('【日志】改进版风险热力图已完成。')

def main():
    """主函数"""
    print("🎯 基于最新数据生成风险热力图")
    print("=" * 50)
    
    # 加载最新数据
    risk_df = load_latest_data()
    
    if risk_df is None:
        print("❌ 数据加载失败，程序退出")
        return
    
    # 创建原始风险热力图
    create_risk_heatmap(risk_df)
    
    # 创建改进版风险热力图（对数刻度）
    create_risk_heatmap_alternative(risk_df)
    
    # 显示数据统计
    print("\n📊 数据统计:")
    print(f"   - 总分区数: {len(risk_df)}")
    print(f"   - 最高风险评分: {risk_df['risk_score_normalized'].max():.4f}")
    print(f"   - 平均风险评分: {risk_df['risk_score_normalized'].mean():.4f}")
    print(f"   - 最高风险分区: {risk_df.loc[risk_df['risk_score_normalized'].idxmax(), 'subzone_code']}")
    
    print("\n🎉 风险热力图生成完成！")
    print("📁 输出文件:")
    print("   - outputs/risk_heatmap_latest_scatter.png (原始版本)")
    print("   - outputs/risk_heatmap_latest_scatter_log.png (对数刻度版本)")

if __name__ == "__main__":
    main() 