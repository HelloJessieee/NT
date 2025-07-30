import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set English font
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """Load volunteer assignment result data"""
    assignments = pd.read_csv("outputs/volunteer_assignment_simple.csv")
    summary = pd.read_csv("outputs/volunteer_assignment_simple_summary.csv")
    subzone_data = pd.read_csv("sg_subzone_all_features.csv")
    
    return assignments, summary, subzone_data

def plot_volunteer_distribution(assignments, summary):
    """Plot volunteer assignment distribution"""
    plt.figure(figsize=(15, 10))
    
    # Subplot 1: Volunteer count distribution per subzone
    plt.subplot(2, 2, 1)
    volunteer_counts = summary['assigned_volunteers'].value_counts().sort_index()
    plt.bar(volunteer_counts.index, volunteer_counts.values, color='skyblue', alpha=0.7)
    plt.xlabel('Number of Assigned Volunteers')
    plt.ylabel('Number of Subzones')
    plt.title('Subzone Volunteer Assignment Distribution')
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Priority score distribution
    plt.subplot(2, 2, 2)
    plt.hist(summary['priority_score'], bins=20, color='lightgreen', alpha=0.7, edgecolor='black')
    plt.xlabel('Priority Score')
    plt.ylabel('Number of Subzones')
    plt.title('Subzone Priority Score Distribution')
    plt.grid(True, alpha=0.3)
    
    # Subplot 3: Response time distribution
    plt.subplot(2, 2, 3)
    plt.hist(assignments['response_time'], bins=20, color='lightcoral', alpha=0.7, edgecolor='black')
    plt.xlabel('Response Time (minutes)')
    plt.ylabel('Number of Assignments')
    plt.title('Volunteer Response Time Distribution')
    plt.grid(True, alpha=0.3)
    
    # Subplot 4: Priority vs volunteer count
    plt.subplot(2, 2, 4)
    plt.scatter(summary['priority_score'], summary['assigned_volunteers'], 
               alpha=0.6, color='purple', s=50)
    plt.xlabel('Priority Score')
    plt.ylabel('Number of Assigned Volunteers')
    plt.title('Priority Score vs Volunteer Assignment Count')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/volunteer_assignment_simple_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_top_subzones(summary, top_n=10):
    """Plot top priority subzones"""
    top_subzones = summary.nlargest(top_n, 'priority_score')
    
    plt.figure(figsize=(12, 8))
    bars = plt.barh(range(len(top_subzones)), top_subzones['priority_score'], 
                    color='gold', alpha=0.8)
    
    # Add volunteer count labels
    for i, (idx, row) in enumerate(top_subzones.iterrows()):
        plt.text(row['priority_score'] + 0.01, i, 
                f"{int(row['assigned_volunteers'])} volunteers", 
                va='center', fontweight='bold')
    
    plt.yticks(range(len(top_subzones)), top_subzones['subzone_name'])
    plt.xlabel('Priority Score')
    plt.title(f'Top {top_n} Priority Subzones')
    plt.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('outputs/volunteer_assignment_top_subzones.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_coverage_map(assignments, subzone_data):
    """Plot coverage map"""
    # Merge data
    coverage_data = subzone_data[['subzone_code', 'subzone_name', 'latitude', 'longitude']].copy()
    
    # Calculate volunteer count per subzone
    volunteer_counts = assignments.groupby('subzone_code')['volunteer_id'].count().reset_index()
    volunteer_counts.columns = ['subzone_code', 'volunteer_count']
    
    coverage_data = coverage_data.merge(volunteer_counts, on='subzone_code', how='left')
    coverage_data['volunteer_count'] = coverage_data['volunteer_count'].fillna(0)
    
    plt.figure(figsize=(12, 10))
    
    # Plot scatter plot, size represents volunteer count
    scatter = plt.scatter(coverage_data['longitude'], coverage_data['latitude'], 
                         s=coverage_data['volunteer_count'] * 50 + 20,  # Size based on volunteer count
                         c=coverage_data['volunteer_count'], 
                         cmap='YlOrRd', alpha=0.7, edgecolors='black', linewidth=0.5)
    
    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('Number of Assigned Volunteers')
    
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Volunteer Assignment Coverage Map')
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    total_covered = (coverage_data['volunteer_count'] > 0).sum()
    total_subzones = len(coverage_data)
    coverage_rate = total_covered / total_subzones * 100
    
    plt.text(0.02, 0.98, f'Covered Subzones: {total_covered}/{total_subzones} ({coverage_rate:.1f}%)', 
             transform=plt.gca().transAxes, fontsize=12, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('outputs/volunteer_assignment_coverage_map.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_summary_report(assignments, summary):
    """Generate summary report"""
    report = f"""# Volunteer Assignment Optimization Results Summary

## Basic Statistics
- **Total Assignments**: {len(assignments)}
- **Covered Subzones**: {len(summary)}
- **Volunteers Used**: {assignments['volunteer_id'].nunique()}
- **Average Response Time**: {assignments['response_time'].mean():.1f} minutes

## Assignment Effectiveness
- **Average Volunteers per Subzone**: {summary['assigned_volunteers'].mean():.1f}
- **Maximum Volunteers in Subzone**: {summary['assigned_volunteers'].max()} volunteers
- **Minimum Volunteers in Subzone**: {summary['assigned_volunteers'].min()} volunteers

## Priority Distribution
- **Highest Priority**: {summary['priority_score'].max():.3f}
- **Lowest Priority**: {summary['priority_score'].min():.3f}
- **Average Priority**: {summary['priority_score'].mean():.3f}

## Top 10 High Priority Subzones
"""
    
    top_10 = summary.nlargest(10, 'priority_score')
    for i, (_, row) in enumerate(top_10.iterrows(), 1):
        report += f"{i}. **{row['subzone_name']}** - Priority: {row['priority_score']:.3f}, Volunteers: {int(row['assigned_volunteers'])}\n"
    
    return report

def main():
    """Main function"""
    print("📊 Generating volunteer assignment visualization charts...")
    
    # Load data
    assignments, summary, subzone_data = load_data()
    
    # Generate charts
    plot_volunteer_distribution(assignments, summary)
    plot_top_subzones(summary, top_n=10)
    plot_coverage_map(assignments, subzone_data)
    
    # Generate report
    report = generate_summary_report(assignments, summary)
    with open("outputs/volunteer_assignment_simple_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ Volunteer assignment visualization charts completed!")
    print("📁 Output files:")
    print("   - outputs/volunteer_assignment_simple_analysis.png")
    print("   - outputs/volunteer_assignment_top_subzones.png") 
    print("   - outputs/volunteer_assignment_coverage_map.png")
    print("   - outputs/volunteer_assignment_simple_report.md")

if __name__ == "__main__":
    main() 