# AED模型2算法详细文档

## 模型概述
AED模型2是一个基于面积权重的平衡分配优化模型，用于将有限数量的AED设备合理分配到各个分区，最大化覆盖效果。

## 算法核心思想

### 1. 几何方法原理
- **面积权重**: 使用人口密度作为区域面积的代理权重
- **几何逻辑**: 区域面积越大（人口密度越高）→ 越难管理 → 优先级越高
- **数学表达**: `area_weight = population_density / max_population_density`

### 2. 优化目标
最大化加权覆盖效果：
```
maximize: Σ(i=1 to n) [AED_count_i × risk_score_i × area_weight_i]
```

其中：
- `AED_count_i`: 分区i分配的AED数量
- `risk_score_i`: 分区i的风险评分
- `area_weight_i`: 分区i的面积权重

## 详细算法步骤

### 步骤1: 数据预处理
```python
# 计算面积权重（使用人口密度作为代理）
subzone_data['population_density_proxy'] = subzone_data['Total_Total']
subzone_data['normalized_density'] = subzone_data['population_density_proxy'] / subzone_data['population_density_proxy'].max()
subzone_data['area_weight'] = subzone_data['normalized_density']

# 计算风险评分
subzone_data['risk_score'] = (
    subzone_data['Total_Total'] * 0.4 +
    subzone_data['elderly_ratio'] * 10000 * 0.3 +
    subzone_data['low_income_ratio'] * 10000 * 0.3
)

# 标准化风险评分
subzone_data['normalized_risk_score'] = (subzone_data['risk_score'] - subzone_data['risk_score'].min()) / (subzone_data['risk_score'].max() - subzone_data['risk_score'].min())
```

### 步骤2: 优先级计算
```python
# 计算每个分区的优先级分数
priority_scores = subzone_data['normalized_risk_score'] * subzone_data['area_weight']
```

### 步骤3: 分层分配策略

#### 3.1 基础分配
- 每个分区至少分配1台AED
- 确保全覆盖：`base_allocation = np.ones(n_subzones, dtype=int)`

#### 3.2 优先级分配
按优先级分数排序，分层分配剩余AED：

```python
# 按优先级排序
priority_indices = np.argsort(priority_scores)[::-1]

# 分层分配
for i, idx in enumerate(priority_indices):
    priority_rank = i + 1
    
    if priority_rank <= n_subzones * 0.2:  # 前20%高优先级
        extra_aeds = min(remaining_aeds, 5)  # 最多6台AED (1+5)
    elif priority_rank <= n_subzones * 0.5:  # 前50%中优先级
        extra_aeds = min(remaining_aeds, 3)  # 最多4台AED (1+3)
    else:  # 其他分区
        extra_aeds = min(remaining_aeds, 1)  # 最多2台AED (1+1)
    
    base_allocation[idx] += extra_aeds
    remaining_aeds -= extra_aeds
```

### 步骤4: 覆盖效果计算
```python
# 计算每个分区的覆盖效果
coverage_effect = []
for i in range(n_subzones):
    effect = base_allocation[i] * subzone_data.iloc[i]['normalized_risk_score'] * subzone_data.iloc[i]['area_weight']
    coverage_effect.append(effect)
```

## 算法特点

### 1. 平衡性
- **全覆盖**: 每个分区至少1台AED
- **避免过度集中**: 最多6台AED/分区
- **合理分布**: 标准差1.6，分布均匀

### 2. 优先级导向
- **高优先级分区** (前20%): 6台AED
- **中优先级分区** (前50%): 4台AED
- **基础分区**: 2台AED

### 3. 面积权重考虑
- 人口密度越高 → 面积权重越大 → 优先级越高
- 符合"区域面积越大越难弄"的几何逻辑

## 数学公式

### 目标函数
```
maximize: Σ(i=1 to n) [x_i × risk_i × area_weight_i]
```

### 约束条件
```
Σ(i=1 to n) x_i = total_aeds
x_i ≥ 1, ∀i ∈ {1,2,...,n}
x_i ≤ 6, ∀i ∈ {1,2,...,n}
```

其中：
- `x_i`: 分区i分配的AED数量
- `risk_i`: 分区i的风险评分
- `area_weight_i`: 分区i的面积权重
- `total_aeds`: 总AED数量

## 算法优势

### 1. 简单高效
- 无需复杂优化算法
- 直接分配，计算快速
- 易于理解和实现

### 2. 结果合理
- 分配均匀，避免过度集中
- 考虑多个因素（风险、面积、人口）
- 符合实际需求

### 3. 可扩展性
- 易于调整分配策略
- 可以添加新的约束条件
- 支持不同规模的优化

## 实现代码

```python
def balanced_aed_allocation(subzone_data):
    """
    平衡的AED分配算法
    """
    total_aeds = subzone_data['AED_count'].sum()
    n_subzones = len(subzone_data)
    
    # 计算优先级分数
    priority_scores = subzone_data['normalized_risk_score'] * subzone_data['area_weight']
    
    # 基础分配：每个分区至少1台AED
    base_allocation = np.ones(n_subzones, dtype=int)
    remaining_aeds = total_aeds - n_subzones
    
    # 按优先级分配剩余AED
    if remaining_aeds > 0:
        priority_indices = np.argsort(priority_scores)[::-1]
        
        for i, idx in enumerate(priority_indices):
            if remaining_aeds <= 0:
                break
            
            priority_rank = i + 1
            if priority_rank <= n_subzones * 0.2:
                extra_aeds = min(remaining_aeds, 5)
            elif priority_rank <= n_subzones * 0.5:
                extra_aeds = min(remaining_aeds, 3)
            else:
                extra_aeds = min(remaining_aeds, 1)
            
            base_allocation[idx] += extra_aeds
            remaining_aeds -= extra_aeds
    
    return base_allocation
```

## 结果验证

### 分配统计
- **总AED数量**: 1128台
- **覆盖分区数**: 332个分区
- **平均分配**: 3.4台/分区
- **分配范围**: 2-6台/分区
- **标准差**: 1.6

### 分配分布
- 2台AED: 166个分区
- 4台AED: 100个分区
- 6台AED: 66个分区

## 结论

AED模型2算法成功实现了基于面积权重的平衡分配，既保证了全覆盖，又避免了过度集中，同时考虑了风险评分和人口密度，是一个实用且高效的优化算法。 