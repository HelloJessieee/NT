# 新加坡AED部署优化与志愿者分配研究包

## 项目概述

本项目为新加坡心脏骤停（OHCA）事件的风险建模、AED（自动体外除颤器）部署优化和志愿者分配的综合研究。研究基于真实的地理数据、人口统计数据和历史OHCA事件数据，为政府决策提供科学依据。

## 文件夹结构

```
government_research_package/
├── code/                    # 核心代码文件
├── data/                    # 数据文件
├── results/                 # 研究结果
├── documentation/           # 文档说明
├── requirements/            # 环境配置
└── README.md               # 本文件
```

## 核心功能模块

### 1. 风险建模 (Risk Modeling)
- **文件**: `code/optimized_risk_model_with_area.py`
- **功能**: 基于地理、人口、社会经济因素的心脏骤停风险预测模型
- **输出**: 风险评分和地理热力图

### 2. AED部署优化 (AED Deployment Optimization)
- **文件**: `code/aed_final_optimization.py`
- **功能**: 使用整数线性规划优化AED部署位置
- **输出**: 最优AED部署方案和覆盖分析

### 3. 志愿者分配 (Volunteer Assignment)
- **文件**: `code/optimized_volunteer_assignment_simple.py`
- **功能**: 基于风险评分和地理距离的志愿者最优分配
- **输出**: 志愿者分配方案和覆盖地图

### 4. 数据可视化 (Data Visualization)
- **文件**: `code/plot_aed_final_analysis.py`, `code/create_geographic_heatmaps.py`
- **功能**: 生成地理热力图、部署地图和分析图表
- **输出**: PNG格式的可视化结果

## 数据文件说明

### 输入数据
- `data/sg_subzone_all_features_with_area.csv`: 新加坡子区域特征数据（包含面积权重）
- `data/AEDLocations_with_coords.csv`: 现有AED位置数据
- `data/volunteers.csv`: 志愿者位置数据
- `data/ResidentPopulationbyPlanningAreaSubzoneofResidenceEthnicGroupandSexCensusofPopulation2020.csv`: 2020年人口普查数据

### 输出结果
- `results/aed_final_optimization.csv`: AED优化部署结果
- `results/risk_analysis_paper_aligned.csv`: 风险分析结果
- `results/volunteer_assignment_simple.csv`: 志愿者分配结果

## 环境配置

### Python版本要求
- Python 3.8+

### 安装依赖
```bash
pip install -r requirements/requirements.txt
```

### 主要依赖包
- pandas: 数据处理
- numpy: 数值计算
- scikit-learn: 机器学习
- geopandas: 地理数据处理
- matplotlib/seaborn: 数据可视化
- folium: 交互式地图

## 使用方法

### 1. 运行风险建模
```bash
python code/optimized_risk_model_with_area.py
```

### 2. 运行AED部署优化
```bash
python code/aed_final_optimization.py
```

### 3. 运行志愿者分配
```bash
python code/optimized_volunteer_assignment_simple.py
```

### 4. 生成可视化结果
```bash
python code/plot_aed_final_analysis.py
```

## 研究结果摘要

### 风险建模结果
- 识别了新加坡心脏骤停高风险区域
- 建立了基于多因素的预测模型
- 生成了详细的风险热力图

### AED部署优化结果
- 优化了AED部署位置，最大化覆盖效果
- 考虑了人口密度、风险评分和地理因素
- 提供了详细的部署建议

### 志愿者分配结果
- 基于风险评分分配志愿者
- 优化了响应时间和覆盖范围
- 提供了志愿者管理建议

## 技术特点

1. **科学性**: 基于真实数据和统计建模
2. **实用性**: 可直接用于政府决策
3. **可扩展性**: 模块化设计，易于扩展
4. **可视化**: 丰富的图表和地图输出
5. **可重现性**: 完整的代码和数据

## 联系信息

如有技术问题或需要进一步说明，请联系研究团队。

## 许可证

本项目仅供学术研究和政府决策使用。 "# NT" 
