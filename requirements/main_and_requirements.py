# ✅ requirements.txt (示例)

# === 基础数据处理 ===
pandas
numpy
geopandas

# === 机器学习 ===
xgboost
scikit-learn

# === 可视化 ===
matplotlib
seaborn

# === 空间优化 ===
PuLP

# === GIS / 地理文件支持 ===
fiona
shapely

# === 可选：仪表盘 ===
dash
streamlit

# ===========================================

# ✅ main.py

import src.risk_model as risk_model
import src.prediction_model as prediction_model
import src.aed_optimizer as aed_optimizer
import src.volunteer_matcher as volunteer_matcher


def main():
    print("[1/4] 🔍 Running Risk Heatmap Model...")
    risk_model.run()

    print("[2/4] 🧠 Running Predictive Risk Model...")
    prediction_model.run()

    print("[3/4] 🗺️ Running AED Deployment Optimizer...")
    aed_optimizer.run()

    print("[4/4] 🙋 Running Volunteer Assignment Matcher...")
    volunteer_matcher.run()

    print("✅ All modules completed. Check outputs/ directory.")


if __name__ == "__main__":
    main()
