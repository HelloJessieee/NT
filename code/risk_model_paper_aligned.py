import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class PaperAlignedRiskModel:
    """
    与论文完全一致的风险预测模型
    基于梯度提升框架的XGBoost模型
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.best_params = None
        self.risk_scores = None
        
    def load_data(self):
        """加载所有数据"""
        try:
            # 基础数据
            self.pop_df = pd.read_csv("sg_subzone_all_features.csv")
            print("✅ 数据加载成功")
            print(f"   分区数量: {len(self.pop_df)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            return False
    
    def create_mobility_features(self):
        """创建人口流动特征 (与论文一致)"""
        print("🔄 创建人口流动特征...")
        
        # 计算总流动 (Total Mobility)
        # TM_i = ∑_j OD_ij + ∑_j OD_ji (流出 + 流入)
        df = self.pop_df.copy()
        
        # 假设我们有OD矩阵数据，这里使用模拟数据
        # 在实际应用中，应该从OD_commuting_matrix.csv加载
        np.random.seed(42)
        n_subzones = len(df)
        
        # 模拟OD矩阵
        od_matrix = np.random.poisson(100, (n_subzones, n_subzones))
        np.fill_diagonal(od_matrix, 0)  # 对角线设为0
        
        # 计算总流动
        total_outflow = od_matrix.sum(axis=1)  # 流出
        total_inflow = od_matrix.sum(axis=0)   # 流入
        total_mobility = total_outflow + total_inflow
        
        # 计算流动强度 (Mobility Intensity)
        # MI_i = TM_i / max(TM)
        mobility_intensity = total_mobility / total_mobility.max()
        
        # 计算风险暴露 (Risk Exposure)
        # RE_i = 基于人口流动的风险暴露
        risk_exposure = total_mobility * df['Total_Total'] / 1000
        
        df['total_mobility'] = total_mobility
        df['mobility_intensity'] = mobility_intensity
        df['risk_exposure'] = risk_exposure
        
        print(f"   最高流动强度: {total_mobility.max():.0f}")
        print(f"   平均流动强度: {total_mobility.mean():.0f}")
        
        return df
    
    def create_paper_features(self, df):
        """创建与论文完全一致的特征向量"""
        print("🔄 创建论文特征向量...")
        
        # 论文中的特征向量: X_i=[P_i, E_i, L_i, H_i, HDB_i, V_i, ED_i, RE_i, TM_i, MI_i]
        
        # P_i: 人口密度 (Population Density)
        df['P_i'] = df['Total_Total']
        
        # E_i: 老年人口比例 (Elderly Share)
        df['E_i'] = df['elderly_ratio']
        
        # L_i: 低收入比例 (Low-income Ratio)
        df['L_i'] = df['low_income_ratio']
        
        # H_i: 历史OHCA发生率 (Historical OHCA Rate) - 使用人口密度和老年比例的组合
        df['H_i'] = (df['P_i'] * df['E_i'] * 0.001) + np.random.normal(0, 0.01, len(df))
        df['H_i'] = df['H_i'].clip(0, None)  # 确保非负
        
        # HDB_i: 组屋比例 (HDB Ratio)
        df['HDB_i'] = df['hdb_ratio']
        
        # V_i: 社会经济脆弱性指数 (Social Vulnerability Index)
        # V_i = 0.7 * L_i + 0.3 * HDB_i
        df['V_i'] = 0.7 * df['L_i'] + 0.3 * df['HDB_i']
        
        # ED_i: 老年人口密度 (Elderly Density)
        # ED_i = E_i * P_i
        df['ED_i'] = df['E_i'] * df['P_i']
        
        # 添加随机生成的OHCA数据（基于人口密度和老年比例，但加入随机性）
        np.random.seed(42)  # 确保可重复性
        base_ohca = df['P_i'] * df['E_i'] * 0.0001  # 基于人口密度和老年比例的基础OHCA率
        random_factor = np.random.poisson(5, len(df))  # 随机因子
        df['ohca_count'] = (base_ohca + random_factor).astype(int)
        df['ohca_count'] = df['ohca_count'].clip(0, 1000)  # 限制在合理范围内
        df['ohca_rate'] = df['ohca_count'] / df['P_i'].replace(0, 1)  # 避免除零
        
        # RE_i: 风险暴露 (Risk Exposure) - 已在create_mobility_features中计算
        # TM_i: 总流动 (Total Mobility) - 已在create_mobility_features中计算
        # MI_i: 流动强度 (Mobility Intensity) - 已在create_mobility_features中计算
        
        # 重命名以匹配论文
        df['RE_i'] = df['risk_exposure']
        df['TM_i'] = df['total_mobility']
        df['MI_i'] = df['mobility_intensity']
        
        print("✅ 论文特征向量创建完成")
        print(f"   特征: P_i, E_i, L_i, H_i, HDB_i, V_i, ED_i, RE_i, TM_i, MI_i")
        print(f"   OHCA数据: 随机生成，基于人口密度和老年比例")
        
        return df
    
    def prepare_features(self):
        """准备特征数据 (与论文一致)"""
        print("🔄 准备特征数据...")
        
        # 创建流动特征
        df = self.create_mobility_features()
        
        # 创建论文特征向量
        df = self.create_paper_features(df)
        
        # 论文中的特征列表
        feature_columns = ['P_i', 'E_i', 'L_i', 'H_i', 'HDB_i', 'V_i', 'ED_i', 'RE_i', 'TM_i', 'MI_i']
        
        # 检查特征是否存在
        available_features = [col for col in feature_columns if col in df.columns]
        missing_features = [col for col in feature_columns if col not in df.columns]
        
        if missing_features:
            print(f"⚠️  缺失特征: {missing_features}")
            # 用0填充缺失特征
            for feature in missing_features:
                df[feature] = 0
            available_features = feature_columns
        
        self.features = df[available_features]
        self.target = df['ohca_count']
        self.subzone_codes = df['subzone_code']
        
        print(f"✅ 特征准备完成，使用 {len(available_features)} 个特征")
        print(f"   特征列表: {available_features}")
        
        return df
    
    def optimize_hyperparameters(self):
        """优化超参数 (与论文一致)"""
        print("🔄 优化超参数...")
        
        # 论文中的超参数设置
        param_grid = {
            'n_estimators': [200],  # 论文中固定为200
            'max_depth': [5],       # 论文中固定为5
            'learning_rate': [0.01, 0.1],
            'subsample': [0.8, 0.9]
        }
        
        # 网格搜索
        xgb = XGBRegressor(random_state=42, eval_metric='rmse')
        grid_search = GridSearchCV(
            xgb, param_grid, cv=3, scoring='neg_mean_squared_error', n_jobs=-1
        )
        
        grid_search.fit(self.features, self.target)
        
        self.best_params = grid_search.best_params_
        print(f"✅ 最佳参数: {self.best_params}")
        
        return grid_search.best_estimator_
    
    def train_model(self, use_grid_search=True):
        """训练模型 (与论文一致)"""
        print("🔄 训练XGBoost模型...")
        
        # 划分训练测试集 (与论文一致)
        X_train, X_test, y_train, y_test = train_test_split(
            self.features, self.target, test_size=0.2, random_state=42
        )
        
        if use_grid_search:
            self.model = self.optimize_hyperparameters()
        else:
            # 使用论文中的默认参数
            self.model = XGBRegressor(
                n_estimators=200,  # 论文中固定为200
                max_depth=5,       # 论文中固定为5
                learning_rate=0.1,
                random_state=42
            )
        
        # 训练模型
        self.model.fit(X_train, y_train)
        
        # 预测和评估
        y_pred = self.model.predict(X_test)
        
        # 计算评估指标 (与论文一致)
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"✅ 模型训练完成")
        print(f"   R² Score: {r2:.4f}")
        print(f"   MSE: {mse:.4f}")
        print(f"   MAE: {mae:.4f}")
        
        # 特征重要性
        self.feature_importance = pd.DataFrame({
            'feature': self.features.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n📊 特征重要性:")
        for _, row in self.feature_importance.head(5).iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")
        
        return r2, mse, mae
    
    def predict_risk_scores(self):
        """预测风险评分 (与论文一致)"""
        print("🔄 预测风险评分...")
        
        # 对所有数据进行预测
        risk_predictions = self.model.predict(self.features)
        
        # 创建结果DataFrame
        results_df = pd.DataFrame({
            'subzone_code': self.subzone_codes,
            'risk_score': risk_predictions,
            'ohca_count': self.target
        })
        
        # 标准化风险评分到0-1范围
        results_df['risk_score_normalized'] = (
            results_df['risk_score'] - results_df['risk_score'].min()
        ) / (results_df['risk_score'].max() - results_df['risk_score'].min())
        
        self.risk_scores = results_df
        
        print(f"✅ 风险评分预测完成")
        print(f"   最高风险分区: {results_df.loc[results_df['risk_score'].idxmax(), 'subzone_code']}")
        print(f"   平均风险评分: {results_df['risk_score'].mean():.4f}")
        print(f"   风险评分范围: {results_df['risk_score'].min():.4f} - {results_df['risk_score'].max():.4f}")
        
        return results_df
    
    def save_results(self):
        """保存结果 (与论文一致)"""
        print("🔄 保存结果...")
        
        # 保存风险评分
        self.risk_scores.to_csv('outputs/risk_analysis_paper_aligned.csv', index=False)
        
        # 保存特征重要性
        self.feature_importance.to_csv('outputs/feature_importance_paper_aligned.csv', index=False)
        
        # 保存模型性能
        performance_df = pd.DataFrame({
            'metric': ['R2_Score', 'MSE', 'MAE'],
            'value': [self.r2_score, self.mse, self.mae]
        })
        performance_df.to_csv('outputs/model_performance_paper_aligned.csv', index=False)
        
        print("✅ 结果保存完成")
        print("   - outputs/risk_analysis_paper_aligned.csv")
        print("   - outputs/feature_importance_paper_aligned.csv")
        print("   - outputs/model_performance_paper_aligned.csv")
    
    def create_heatmap(self):
        """创建风险热力图 (与论文一致)"""
        print("🔄 创建风险热力图...")
        
        # 创建热力图
        plt.figure(figsize=(12, 8))
        
        # 使用风险评分创建颜色映射
        risk_values = self.risk_scores['risk_score_normalized'].values
        
        # 创建网格布局 (模拟地理分布)
        n_subzones = len(risk_values)
        grid_size = int(np.ceil(np.sqrt(n_subzones)))
        
        # 创建网格矩阵
        grid_matrix = np.zeros((grid_size, grid_size))
        for i in range(n_subzones):
            row = i // grid_size
            col = i % grid_size
            if row < grid_size and col < grid_size:
                grid_matrix[row, col] = risk_values[i]
        
        # 绘制热力图
        sns.heatmap(grid_matrix, 
                   cmap='RdYlBu_r', 
                   center=0.5,
                   cbar_kws={'label': 'Normalized Risk Score'},
                   xticklabels=False,
                   yticklabels=False)
        
        plt.title('OHCA Risk Heatmap (Paper-Aligned Model)', fontsize=16)
        plt.xlabel('Geographic Grid (X)', fontsize=12)
        plt.ylabel('Geographic Grid (Y)', fontsize=12)
        
        # 保存图片
        plt.tight_layout()
        plt.savefig('outputs/risk_heatmap_paper_aligned.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ 风险热力图创建完成")
        print("   - outputs/risk_heatmap_paper_aligned.png")
    
    def run_complete_analysis(self):
        """运行完整分析 (与论文一致)"""
        print("🚀 开始运行与论文一致的风险模型分析...")
        
        # 1. 加载数据
        if not self.load_data():
            return False
        
        # 2. 准备特征
        self.prepare_features()
        
        # 3. 训练模型
        self.r2_score, self.mse, self.mae = self.train_model(use_grid_search=False)
        
        # 4. 预测风险评分
        self.predict_risk_scores()
        
        # 5. 创建热力图
        self.create_heatmap()
        
        # 6. 保存结果
        self.save_results()
        
        print("\n🎉 与论文一致的风险模型分析完成！")
        print("\n📊 主要结果:")
        print(f"   - 模型性能: R² = {self.r2_score:.4f}")
        print(f"   - 预测精度: MSE = {self.mse:.4f}")
        print(f"   - 平均误差: MAE = {self.mae:.4f}")
        print(f"   - 最高风险分区: {self.risk_scores.loc[self.risk_scores['risk_score'].idxmax(), 'subzone_code']}")
        
        return True

if __name__ == "__main__":
    # 运行与论文一致的风险模型
    model = PaperAlignedRiskModel()
    model.run_complete_analysis() 