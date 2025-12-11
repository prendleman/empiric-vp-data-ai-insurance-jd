"""
Power BI Dashboard Generator for Policy Analytics

Generates Power BI-compatible dashboards and reports from policy analysis results.
"""

import json
import pandas as pd
from datetime import datetime
import os

class DashboardGenerator:
    """Generates Power BI dashboards from policy analysis results."""
    
    def __init__(self, analysis_results):
        """
        Initialize dashboard generator with analysis results.
        
        Args:
            analysis_results: Dictionary containing analysis results from PolicyAnalyzer
        """
        self.results = analysis_results
        self.dashboard_data = {}
    
    def generate_powerbi_dashboard(self, output_path='policy_analytics_dashboard.pbix'):
        """
        Generate Power BI dashboard file.
        
        Note: This creates a JSON structure that can be imported into Power BI.
        For actual .pbix generation, use Power BI REST API or pbip format.
        
        Args:
            output_path: Path to save dashboard file
        """
        self._prepare_dashboard_data()
        
        # Create dashboard structure
        dashboard = {
            'metadata': {
                'title': 'Life & Annuity Policy Analytics Dashboard',
                'created_date': datetime.now().isoformat(),
                'version': '1.0'
            },
            'summary_metrics': self.dashboard_data.get('summary', {}),
            'visualizations': self._create_visualizations(),
            'executive_summary': self._create_executive_summary()
        }
        
        # Save as JSON (can be converted to pbip format)
        json_path = output_path.replace('.pbix', '.json')
        with open(json_path, 'w') as f:
            json.dump(dashboard, f, indent=2, default=str)
        
        print(f"Dashboard data saved to {json_path}")
        print("To create .pbix file, use Power BI Desktop or Fabric API")
        
        return dashboard
    
    def _prepare_dashboard_data(self):
        """Prepare data for dashboard visualizations."""
        # Summary metrics
        if 'summary' in self.results:
            self.dashboard_data['summary'] = self.results['summary']
        
        # Lapse analysis data
        if 'lapse_analysis' in self.results:
            self.dashboard_data['lapse_analysis'] = self.results['lapse_analysis']
        
        # Premium trends
        if 'premium_trends' in self.results:
            self.dashboard_data['premium_trends'] = self.results['premium_trends']
        
        # ROI metrics
        if 'roi_metrics' in self.results:
            self.dashboard_data['roi_metrics'] = self.results['roi_metrics']
    
    def _create_visualizations(self):
        """Create visualization definitions."""
        visualizations = []
        
        # Summary KPI cards
        if 'summary' in self.dashboard_data:
            summary = self.dashboard_data['summary']
            visualizations.append({
                'type': 'kpi_card',
                'title': 'Total Policies',
                'value': summary.get('total_policies', 0),
                'format': 'number'
            })
            visualizations.append({
                'type': 'kpi_card',
                'title': 'Active Policies',
                'value': summary.get('active_policies', 0),
                'format': 'number'
            })
            visualizations.append({
                'type': 'kpi_card',
                'title': 'Lapse Rate',
                'value': summary.get('overall_lapse_rate', 0),
                'format': 'percentage'
            })
            visualizations.append({
                'type': 'kpi_card',
                'title': 'Total Annual Premium',
                'value': summary.get('total_annual_premium', 0),
                'format': 'currency'
            })
        
        # Lapse rate by policy type
        if 'lapse_analysis' in self.dashboard_data:
            lapse_analysis = self.dashboard_data['lapse_analysis']
            if 'by_policy_type' in lapse_analysis:
                visualizations.append({
                    'type': 'bar_chart',
                    'title': 'Lapse Rate by Policy Type',
                    'data': lapse_analysis['by_policy_type'],
                    'x_axis': 'Policy Type',
                    'y_axis': 'Lapse Rate'
                })
        
        # Premium trends over time
        if 'premium_trends' in self.dashboard_data:
            premium_trends = self.dashboard_data['premium_trends']
            if 'by_year' in premium_trends:
                visualizations.append({
                    'type': 'line_chart',
                    'title': 'Premium Trends by Year',
                    'data': premium_trends['by_year'],
                    'x_axis': 'Year',
                    'y_axis': 'Average Premium'
                })
        
        # ROI metrics
        if 'roi_metrics' in self.dashboard_data:
            roi = self.dashboard_data['roi_metrics']
            visualizations.append({
                'type': 'kpi_card',
                'title': 'Potential ROI',
                'value': roi.get('roi_percentage', 0),
                'format': 'percentage'
            })
            visualizations.append({
                'type': 'kpi_card',
                'title': 'Potential Annual Benefit',
                'value': roi.get('net_benefit_annual', 0),
                'format': 'currency'
            })
        
        return visualizations
    
    def _create_executive_summary(self):
        """Create executive summary section."""
        summary = self.dashboard_data.get('summary', {})
        roi = self.dashboard_data.get('roi_metrics', {})
        
        return {
            'key_metrics': {
                'total_policies': summary.get('total_policies', 0),
                'active_policies': summary.get('active_policies', 0),
                'lapse_rate': f"{summary.get('overall_lapse_rate', 0):.2%}",
                'total_annual_premium': f"${summary.get('total_annual_premium', 0):,.0f}"
            },
            'business_impact': {
                'potential_roi': f"{roi.get('roi_percentage', 0):.1f}%",
                'potential_annual_benefit': f"${roi.get('net_benefit_annual', 0):,.0f}",
                'premium_retention_opportunity': f"${roi.get('potential_premium_retained_annual', 0):,.0f}"
            },
            'recommendations': [
                'Implement predictive analytics to identify at-risk policies early',
                'Develop targeted retention campaigns for high-value policyholders',
                'Optimize pricing strategies based on cohort analysis insights',
                'Invest in analytics infrastructure to achieve projected ROI'
            ]
        }
    
    def generate_excel_report(self, output_path='policy_analytics_report.xlsx'):
        """Generate Excel report with analysis results."""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            if 'summary' in self.dashboard_data:
                summary_df = pd.DataFrame([self.dashboard_data['summary']])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Lapse analysis sheet
            if 'lapse_analysis' in self.dashboard_data:
                lapse_data = self.dashboard_data['lapse_analysis']
                if 'by_policy_type' in lapse_data:
                    lapse_df = pd.DataFrame(lapse_data['by_policy_type']).T
                    lapse_df.to_excel(writer, sheet_name='Lapse Analysis')
            
            # Premium trends sheet
            if 'premium_trends' in self.dashboard_data:
                trends = self.dashboard_data['premium_trends']
                if 'by_year' in trends:
                    trends_df = pd.DataFrame(trends['by_year']).T
                    trends_df.to_excel(writer, sheet_name='Premium Trends')
            
            # ROI metrics sheet
            if 'roi_metrics' in self.dashboard_data:
                roi_df = pd.DataFrame([self.dashboard_data['roi_metrics']])
                roi_df.to_excel(writer, sheet_name='ROI Analysis', index=False)
        
        print(f"Excel report saved to {output_path}")
        return output_path

