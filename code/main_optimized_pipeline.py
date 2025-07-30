import pandas as pd
import numpy as np
import os
import time
from optimized_risk_model import OptimizedRiskModel
from optimized_aed_placement import OptimizedAEDPlacement
from optimized_volunteer_assignment import OptimizedVolunteerAssignment

def main_optimized_pipeline():
    """
    主优化流水线 - 按顺序运行所有优化模型
    """
    print("🚀 开始AED-OHCA优化系统完整流水线...")
    start_time = time.time()
    
    # 创建输出目录
    os.makedirs("outputs", exist_ok=True)
    
    # 阶段1: 风险预测模型
    print("\n" + "="*60)
    print("阶段1: 优化风险预测模型")
    print("="*60)
    
    risk_model = OptimizedRiskModel()
    risk_results = risk_model.run_complete_analysis()
    
    if risk_results is None:
        print("❌ 风险预测失败，终止流水线")
        return False
    
    # 阶段2: AED部署优化
    print("\n" + "="*60)
    print("阶段2: AED部署优化")
    print("="*60)
    
    aed_optimizer = OptimizedAEDPlacement(max_coverage_distance=200)
    aed_results = aed_optimizer.run_optimization(n_candidates=30, budget=20)
    
    if aed_results is None:
        print("❌ AED部署优化失败，终止流水线")
        return False
    
    # 阶段3: 志愿者分配优化
    print("\n" + "="*60)
    print("阶段3: 志愿者分配优化")
    print("="*60)
    
    volunteer_optimizer = OptimizedVolunteerAssignment()
    volunteer_results = volunteer_optimizer.run_optimization(top_n_zones=10)
    
    if volunteer_results is None:
        print("❌ 志愿者分配优化失败，终止流水线")
        return False
    
    # 生成综合报告
    print("\n" + "="*60)
    print("生成综合报告")
    print("="*60)
    
    generate_comprehensive_report(risk_results, aed_results, volunteer_results)
    
    # 计算总运行时间
    total_time = time.time() - start_time
    print(f"\n🎉 完整流水线运行完成！总耗时: {total_time:.2f}秒")
    
    return True

def generate_comprehensive_report(risk_results, aed_results, volunteer_results):
    """生成综合报告"""
    print("🔄 生成综合报告...")
    
    # 读取所有结果文件
    risk_scores = pd.read_csv("outputs/optimized_risk_scores.csv")
    aed_placement = pd.read_csv("outputs/aed_placement_results.csv")
    volunteer_assignments = pd.read_csv("outputs/volunteer_assignments_optimized.csv")
    optimization_stats = pd.read_csv("outputs/optimization_stats.csv")
    assignment_stats = pd.read_csv("outputs/assignment_stats.csv")
    
    # 生成报告
    report = f"""
# AED-OHCA 优化系统综合报告

## 系统概览
本系统采用三阶段优化方法，实现OHCA风险预测、AED部署优化和志愿者分配优化。

## 阶段1: 风险预测模型
- **模型类型**: XGBoost机器学习模型
- **特征数量**: {len(risk_scores.columns) - 3} 个特征
- **分区数量**: {len(risk_scores)} 个分区
- **最高风险分区**: {risk_scores.loc[risk_scores['risk_score'].idxmax(), 'subzone_code']}
- **平均风险评分**: {risk_scores['risk_score'].mean():.4f}

### 特征重要性 (前5名)
"""
    
    # 添加特征重要性
    feature_importance = pd.read_csv("outputs/feature_importance.csv")
    for _, row in feature_importance.head(5).iterrows():
        report += f"- {row['feature']}: {row['importance']:.4f}\n"
    
    report += f"""
## 阶段2: AED部署优化
- **候选位置数**: {optimization_stats.iloc[0]['total_candidates']}
- **部署AED数**: {optimization_stats.iloc[0]['selected_aeds']}
- **覆盖分区数**: {optimization_stats.iloc[0]['covered_subzones']}
- **覆盖率**: {optimization_stats.iloc[0]['coverage_rate']:.1%}
- **总成本**: ${optimization_stats.iloc[0]['total_cost']:,}

### 部署的AED位置 (前5个)
"""
    
    # 添加AED部署位置
    deployed_aeds = aed_placement[aed_placement['deployed'] == 1]
    for _, row in deployed_aeds.head(5).iterrows():
        report += f"- 分区 {row['subzone_code']}: 风险评分 {row['risk_score']:.4f}\n"
    
    report += f"""
## 阶段3: 志愿者分配优化
- **分配数量**: {assignment_stats.iloc[0]['total_assignments']}
- **平均距离**: {assignment_stats.iloc[0]['avg_distance_km']:.1f}km
- **平均风险评分**: {assignment_stats.iloc[0]['avg_risk_score']:.4f}
- **总风险覆盖**: {assignment_stats.iloc[0]['total_risk_coverage']:.4f}

### 志愿者分配结果 (前5个)
"""
    
    # 添加志愿者分配结果
    for _, row in volunteer_assignments.head(5).iterrows():
        report += f"- 志愿者 {row['volunteer_id']} → 分区 {row['assigned_zone']}\n"
        report += f"  距离: {row['distance_km']:.1f}km, 风险评分: {row['zone_risk_score']:.4f}\n"
    
    report += f"""
## 系统性能指标
- **风险预测准确性**: 基于XGBoost模型的特征重要性分析
- **AED覆盖效率**: {optimization_stats.iloc[0]['coverage_rate']:.1%} 的分区覆盖率
- **志愿者分配效率**: 平均 {assignment_stats.iloc[0]['avg_distance_km']:.1f}km 响应距离

## 输出文件
- 风险评分: outputs/optimized_risk_scores.csv
- AED部署: outputs/aed_placement_results.csv
- 志愿者分配: outputs/volunteer_assignments_optimized.csv
- 特征重要性: outputs/feature_importance.csv
- 优化统计: outputs/optimization_stats.csv
- 分配统计: outputs/assignment_stats.csv

## 技术特点
1. **数据驱动**: 充分利用OD通勤数据、人口密度等特征
2. **算法优化**: 使用XGBoost、线性规划、匈牙利算法
3. **多目标优化**: 平衡风险覆盖、成本控制和响应时间
4. **可扩展性**: 模块化设计，易于扩展和维护

## 下一步建议
1. 集成真实地理坐标数据
2. 添加时间窗口约束
3. 实现动态调度算法
4. 开发可视化界面
"""
    
    # 保存报告
    with open("outputs/comprehensive_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ 综合报告已生成: outputs/comprehensive_report.md")
    
    # 显示关键指标
    print("\n📊 关键性能指标:")
    print(f"   风险预测: {len(risk_scores)} 个分区")
    print(f"   AED部署: {optimization_stats.iloc[0]['selected_aeds']} 个位置")
    print(f"   志愿者分配: {assignment_stats.iloc[0]['total_assignments']} 个分配")
    print(f"   总覆盖率: {optimization_stats.iloc[0]['coverage_rate']:.1%}")

if __name__ == "__main__":
    # 运行完整流水线
    success = main_optimized_pipeline()
    
    if success:
        print("\n🎉 优化系统运行成功！")
        print("📁 请查看 outputs/ 目录中的结果文件")
        print("📋 详细报告: outputs/comprehensive_report.md")
    else:
        print("\n❌ 优化系统运行失败，请检查错误信息") 