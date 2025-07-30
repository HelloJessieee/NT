#!/usr/bin/env python3
"""
新加坡AED部署优化与志愿者分配研究 - 完整分析运行脚本
Complete Analysis Runner for Singapore AED Deployment and Volunteer Assignment Research

作者: Research Team
日期: 2024年7月30日
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step_num, description):
    """打印步骤信息"""
    print(f"\n步骤 {step_num}: {description}")
    print("-" * 40)

def run_script(script_path, description):
    """运行Python脚本"""
    print(f"正在运行: {description}")
    print(f"脚本路径: {script_path}")
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✓ 成功完成")
            if result.stdout:
                print("输出信息:")
                print(result.stdout)
        else:
            print("✗ 运行失败")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ 运行异常: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print_header("新加坡AED部署优化与志愿者分配研究")
    print("完整分析运行脚本")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查当前目录
    current_dir = Path.cwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查必要的文件夹
    required_dirs = ['code', 'data', 'results']
    for dir_name in required_dirs:
        if not (current_dir / dir_name).exists():
            print(f"错误: 缺少必要的文件夹 '{dir_name}'")
            return
    
    # 检查数据文件
    required_data_files = [
        'data/sg_subzone_all_features_with_area.csv',
        'data/AEDLocations_with_coords.csv',
        'data/volunteers.csv'
    ]
    
    for data_file in required_data_files:
        if not (current_dir / data_file).exists():
            print(f"警告: 缺少数据文件 '{data_file}'")
    
    print("\n开始执行分析流程...")
    
    # 步骤1: 风险建模
    print_step(1, "风险建模分析")
    risk_model_script = "code/optimized_risk_model_with_area.py"
    if not run_script(risk_model_script, "风险建模"):
        print("风险建模失败，但继续执行后续步骤...")
    
    # 步骤2: AED部署优化
    print_step(2, "AED部署优化")
    aed_optimization_script = "code/aed_final_optimization.py"
    if not run_script(aed_optimization_script, "AED部署优化"):
        print("AED部署优化失败，但继续执行后续步骤...")
    
    # 步骤3: 志愿者分配
    print_step(3, "志愿者分配优化")
    volunteer_script = "code/optimized_volunteer_assignment_simple.py"
    if not run_script(volunteer_script, "志愿者分配"):
        print("志愿者分配失败，但继续执行后续步骤...")
    
    # 步骤4: 数据可视化
    print_step(4, "生成可视化结果")
    visualization_script = "code/plot_aed_final_analysis.py"
    if not run_script(visualization_script, "AED分析可视化"):
        print("AED可视化失败，但继续执行后续步骤...")
    
    # 步骤5: 地理热力图
    print_step(5, "生成地理热力图")
    heatmap_script = "code/create_geographic_heatmaps.py"
    if not run_script(heatmap_script, "地理热力图生成"):
        print("地理热力图生成失败，但继续执行后续步骤...")
    
    # 完成总结
    print_header("分析完成")
    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n结果文件位置:")
    print("- AED优化结果: results/aed_final_optimization.csv")
    print("- 风险分析结果: results/risk_analysis_paper_aligned.csv")
    print("- 志愿者分配结果: results/volunteer_assignment_simple.csv")
    print("- 可视化图表: 查看code文件夹中的输出")
    
    print("\n注意事项:")
    print("1. 如果某些步骤失败，请检查错误信息")
    print("2. 确保所有数据文件都在data文件夹中")
    print("3. 确保已安装所有必要的Python包")
    print("4. 查看documentation文件夹中的详细说明")

if __name__ == "__main__":
    main() 