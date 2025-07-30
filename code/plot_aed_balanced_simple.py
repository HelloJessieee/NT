import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set English font
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """Load balanced AED deployment result data"""
    aed_data = pd.read_csv("outputs/aed_optimization_balanced_simple.csv")
    return aed_data

def plot_balanced_aed_map(aed_data):
    """Plot balanced AED deployment map with color intensity representing quantity"""
    plt.figure(figsize=(15, 12))
    
    # Filter out subzones with no AED deployment
    deployed_data = aed_data[aed_data['deployed_aeds'] > 0].copy()
    
    # Create scatter plot with size and color based on AED count
    scatter = plt.scatter(deployed_data['longitude'], deployed_data['latitude'], 
                         s=deployed_data['deployed_aeds'] * 50 + 30,  # Size based on AED count
                         c=deployed_data['deployed_aeds'], 
                         cmap='YlOrRd', alpha=0.8, edgecolors='black', linewidth=0.5)
    
    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('Number of Deployed AEDs')
    
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Balanced AED Deployment - Color Intensity vs Quantity')
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    total_deployed = deployed_data['deployed_aeds'].sum()
    total_subzones = len(deployed_data)
    avg_aed_per_subzone = deployed_data['deployed_aeds'].mean()
    
    plt.text(0.02, 0.98, f'Total AEDs: {total_deployed}\nCovered Subzones: {total_subzones}\nAverage AEDs per Subzone: {avg_aed_per_subzone:.1f}', 
             transform=plt.gca().transAxes, fontsize=12, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('outputs/aed_balanced_deployment_map.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_balanced_distribution(aed_data):
    """Plot balanced AED distribution analysis"""
    plt.figure(figsize=(15, 10))
    
    # Subplot 1: AED count distribution
    plt.subplot(2, 2, 1)
    deployed_data = aed_data[aed_data['deployed_aeds'] > 0]
    aed_counts = deployed_data['deployed_aeds'].value_counts().sort_index()
    colors = ['lightblue', 'skyblue', 'deepskyblue']
    plt.bar(aed_counts.index, aed_counts.values, color=colors[:len(aed_counts)], alpha=0.7)
    plt.xlabel('Number of Deployed AEDs')
    plt.ylabel('Number of Subzones')
    plt.title('Balanced AED Count Distribution')
    plt.grid(True, alpha=0.3)
    
    # Add count labels on bars
    for i, v in enumerate(aed_counts.values):
        plt.text(aed_counts.index[i], v + 5, str(v), ha='center', va='bottom', fontweight='bold')
    
    # Subplot 2: Coverage effect vs AED count
    plt.subplot(2, 2, 2)
    plt.scatter(deployed_data['deployed_aeds'], deployed_data['coverage_effect'], 
               alpha=0.6, color='green', s=50)
    plt.xlabel('Number of Deployed AEDs')
    plt.ylabel('Coverage Effect')
    plt.title('Coverage Effect vs AED Count')
    plt.grid(True, alpha=0.3)
    
    # Subplot 3: Population density vs AED count
    plt.subplot(2, 2, 3)
    plt.scatter(deployed_data['population_density_proxy'], deployed_data['deployed_aeds'], 
               alpha=0.6, color='purple', s=50)
    plt.xlabel('Population Density')
    plt.ylabel('Number of Deployed AEDs')
    plt.title('Population Density vs AED Count')
    plt.grid(True, alpha=0.3)
    
    # Subplot 4: Top 15 subzones by coverage effect
    plt.subplot(2, 2, 4)
    top_15 = deployed_data.nlargest(15, 'coverage_effect')
    bars = plt.barh(range(len(top_15)), top_15['coverage_effect'], color='gold', alpha=0.8)
    plt.yticks(range(len(top_15)), top_15['subzone_name'])
    plt.xlabel('Coverage Effect')
    plt.title('Top 15 Subzones by Coverage Effect')
    plt.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('outputs/aed_balanced_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_aed_comparison(aed_data):
    """Plot comparison between balanced and original allocation"""
    plt.figure(figsize=(16, 8))
    
    # Subplot 1: Balanced allocation
    plt.subplot(1, 2, 1)
    deployed_data = aed_data[aed_data['deployed_aeds'] > 0]
    aed_counts = deployed_data['deployed_aeds'].value_counts().sort_index()
    colors = ['lightgreen', 'green', 'darkgreen']
    plt.bar(aed_counts.index, aed_counts.values, color=colors[:len(aed_counts)], alpha=0.7)
    plt.xlabel('Number of Deployed AEDs')
    plt.ylabel('Number of Subzones')
    plt.title('Balanced Allocation Distribution')
    plt.grid(True, alpha=0.3)
    
    # Add count labels
    for i, v in enumerate(aed_counts.values):
        plt.text(aed_counts.index[i], v + 3, str(v), ha='center', va='bottom', fontweight='bold')
    
    # Subplot 2: Coverage effect distribution
    plt.subplot(1, 2, 2)
    plt.hist(deployed_data['coverage_effect'], bins=20, color='lightcoral', alpha=0.7, edgecolor='black')
    plt.xlabel('Coverage Effect')
    plt.ylabel('Number of Subzones')
    plt.title('Coverage Effect Distribution')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/aed_balanced_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_balanced_summary_report(aed_data):
    """Generate balanced AED deployment summary report"""
    deployed_data = aed_data[aed_data['deployed_aeds'] > 0]
    
    report = f"""# Balanced AED Deployment Visualization Report

## Deployment Overview
- **Total AEDs Deployed**: {deployed_data['deployed_aeds'].sum()}
- **Covered Subzones**: {len(deployed_data)}
- **Average AEDs per Subzone**: {deployed_data['deployed_aeds'].mean():.1f}
- **Maximum AEDs in Single Subzone**: {deployed_data['deployed_aeds'].max()}
- **Minimum AEDs in Single Subzone**: {deployed_data['deployed_aeds'].min()}

## Allocation Strategy
- **Base Allocation**: 1 AED per subzone (332 AEDs)
- **Priority Allocation**: Remaining AEDs distributed by risk × area weight
- **Tiered Distribution**:
  - High Priority (Top 20%): 6 AEDs per subzone
  - Medium Priority (Top 50%): 4 AEDs per subzone  
  - Other Subzones: 2 AEDs per subzone

## Distribution Statistics
"""
    
    aed_distribution = deployed_data['deployed_aeds'].value_counts().sort_index()
    for aed_count, subzone_count in aed_distribution.items():
        report += f"- **{aed_count} AEDs**: {subzone_count} subzones\n"
    
    report += f"""
## Top 10 Subzones by Coverage Effect
"""
    
    top_10 = deployed_data.nlargest(10, 'coverage_effect')
    for i, (_, row) in enumerate(top_10.iterrows(), 1):
        report += f"{i}. **{row['subzone_name']}** - {int(row['deployed_aeds'])} AEDs\n"
        report += f"   - Population Density: {row['population_density_proxy']:.0f}\n"
        report += f"   - Coverage Effect: {row['coverage_effect']:.2f}\n\n"
    
    report += f"""
## Visualization Files
- `aed_balanced_deployment_map.png`: Main deployment map with color intensity
- `aed_balanced_analysis.png`: Distribution and correlation analysis
- `aed_balanced_comparison.png`: Allocation comparison

## Color Legend
- **Red (Dark)**: 6 AEDs (High Priority)
- **Orange**: 4 AEDs (Medium Priority)
- **Yellow**: 2 AEDs (Base Allocation)
"""
    
    with open("outputs/aed_balanced_visualization_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    return report

def main():
    """Main function"""
    print("📊 Generating balanced AED deployment visualization charts...")
    
    # Load data
    aed_data = load_data()
    
    # Generate charts
    plot_balanced_aed_map(aed_data)
    plot_balanced_distribution(aed_data)
    plot_aed_comparison(aed_data)
    
    # Generate report
    report = generate_balanced_summary_report(aed_data)
    
    print("✅ Balanced AED deployment visualization charts completed!")
    print("📁 Output files:")
    print("   - outputs/aed_balanced_deployment_map.png")
    print("   - outputs/aed_balanced_analysis.png")
    print("   - outputs/aed_balanced_comparison.png")
    print("   - outputs/aed_balanced_visualization_report.md")

if __name__ == "__main__":
    main() 