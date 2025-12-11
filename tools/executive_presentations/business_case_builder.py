"""
Business Case Builder

Creates ROI and business case narratives for data and AI initiatives.
"""

from datetime import datetime
from typing import Dict, List, Optional

class BusinessCaseBuilder:
    """Builds business cases for data and AI initiatives."""
    
    def __init__(self):
        """Initialize business case builder."""
        self.templates = {
            'fraud_detection': self._fraud_detection_template,
            'retention_analytics': self._retention_analytics_template,
            'data_analytics': self._data_analytics_template
        }
    
    def build_business_case(self, initiative_name: str, roi_data: Dict,
                          template_type: Optional[str] = None) -> Dict:
        """
        Build a business case for an initiative.
        
        Args:
            initiative_name: Name of the initiative
            roi_data: ROI and financial data
            template_type: Type of template to use
        """
        if template_type and template_type in self.templates:
            template = self.templates[template_type]
        else:
            template = self._generic_template
        
        business_case = {
            'metadata': {
                'initiative_name': initiative_name,
                'created_date': datetime.now().isoformat(),
                'version': '1.0'
            },
            'executive_summary': self._build_executive_summary(initiative_name, roi_data),
            'business_case': template(initiative_name, roi_data),
            'roi_analysis': self._build_roi_analysis(roi_data),
            'implementation_plan': self._build_implementation_plan()
        }
        
        return business_case
    
    def _build_executive_summary(self, initiative_name: str, roi_data: Dict) -> Dict:
        """Build executive summary."""
        roi_percentage = roi_data.get('roi_percentage', 0)
        net_benefit = roi_data.get('net_benefit_annual', 0)
        
        return {
            'initiative': initiative_name,
            'key_benefits': [
                f"ROI: {roi_percentage:.1f}%",
                f"Annual Net Benefit: ${net_benefit:,.0f}",
                "Improved operational efficiency",
                "Enhanced decision-making capabilities"
            ],
            'recommendation': 'Proceed with implementation',
            'urgency': 'High' if roi_percentage > 200 else 'Medium'
        }
    
    def _build_roi_analysis(self, roi_data: Dict) -> Dict:
        """Build ROI analysis section."""
        return {
            'investment': {
                'total_investment': roi_data.get('total_investment', 0),
                'annual_cost': roi_data.get('analytics_investment_annual', 0)
            },
            'benefits': {
                'annual_benefit': roi_data.get('potential_premium_retained_annual', 0) or 
                                roi_data.get('cost_savings_annual', 0),
                'net_benefit_annual': roi_data.get('net_benefit_annual', 0)
            },
            'roi_metrics': {
                'roi_percentage': roi_data.get('roi_percentage', 0),
                'payback_period_months': roi_data.get('payback_period_months', 0)
            },
            'sensitivity_analysis': self._build_sensitivity_analysis(roi_data)
        }
    
    def _build_sensitivity_analysis(self, roi_data: Dict) -> Dict:
        """Build sensitivity analysis."""
        base_roi = roi_data.get('roi_percentage', 0)
        base_benefit = roi_data.get('net_benefit_annual', 0)
        
        return {
            'scenarios': [
                {
                    'scenario': 'Conservative (80% of benefits)',
                    'roi': base_roi * 0.8,
                    'net_benefit': base_benefit * 0.8
                },
                {
                    'scenario': 'Base Case',
                    'roi': base_roi,
                    'net_benefit': base_benefit
                },
                {
                    'scenario': 'Optimistic (120% of benefits)',
                    'roi': base_roi * 1.2,
                    'net_benefit': base_benefit * 1.2
                }
            ]
        }
    
    def _build_implementation_plan(self) -> Dict:
        """Build implementation plan."""
        return {
            'phases': [
                {
                    'phase': 1,
                    'name': 'Planning & Setup',
                    'duration_weeks': 4,
                    'activities': [
                        'Project kickoff',
                        'Requirements gathering',
                        'Infrastructure setup',
                        'Team formation'
                    ]
                },
                {
                    'phase': 2,
                    'name': 'Development',
                    'duration_weeks': 12,
                    'activities': [
                        'Solution development',
                        'Testing and validation',
                        'Integration with existing systems'
                    ]
                },
                {
                    'phase': 3,
                    'name': 'Deployment',
                    'duration_weeks': 4,
                    'activities': [
                        'Production deployment',
                        'User training',
                        'Go-live support'
                    ]
                },
                {
                    'phase': 4,
                    'name': 'Optimization',
                    'duration_weeks': 8,
                    'activities': [
                        'Performance monitoring',
                        'Optimization and tuning',
                        'Continuous improvement'
                    ]
                }
            ],
            'total_duration_weeks': 28,
            'key_milestones': [
                'Project kickoff',
                'Development complete',
                'Production deployment',
                'First quarter results'
            ]
        }
    
    def _generic_template(self, initiative_name: str, roi_data: Dict) -> Dict:
        """Generic business case template."""
        return {
            'problem_statement': [
                f"Current challenges in {initiative_name.lower()} area",
                "Need for improved analytics and automation",
                "Opportunity to leverage AI/ML capabilities"
            ],
            'proposed_solution': [
                f"Implement {initiative_name} solution",
                "Leverage advanced analytics and AI/ML",
                "Automate manual processes",
                "Provide real-time insights"
            ],
            'expected_outcomes': [
                "Improved operational efficiency",
                "Better decision-making",
                "Cost savings and revenue protection",
                "Enhanced customer experience"
            ]
        }
    
    def _fraud_detection_template(self, initiative_name: str, roi_data: Dict) -> Dict:
        """Fraud detection business case template."""
        return {
            'problem_statement': [
                "Fraudulent claims result in significant financial losses",
                "Manual fraud detection is time-consuming and error-prone",
                "Need for real-time fraud detection capabilities"
            ],
            'proposed_solution': [
                "Implement AI/ML-based fraud detection system",
                "Real-time fraud scoring for all claims",
                "Automated case routing for high-risk claims",
                "Executive dashboards for fraud metrics"
            ],
            'expected_outcomes': [
                "Reduce fraudulent claim payouts by 20-40%",
                "Improve fraud detection accuracy",
                "Reduce manual review workload",
                "ROI of 300-500%"
            ]
        }
    
    def _retention_analytics_template(self, initiative_name: str, roi_data: Dict) -> Dict:
        """Retention analytics business case template."""
        return {
            'problem_statement': [
                "Policyholder churn results in lost revenue",
                "Need to identify at-risk policyholders early",
                "Lack of targeted retention strategies"
            ],
            'proposed_solution': [
                "Implement predictive churn analytics",
                "Customer segmentation by risk and value",
                "Automated retention campaign optimization",
                "CLV calculation and optimization"
            ],
            'expected_outcomes': [
                "Reduce churn rate by 20-30%",
                "Protect millions in annual premium revenue",
                "Improve customer lifetime value",
                "ROI of 200-400%"
            ]
        }
    
    def _data_analytics_template(self, initiative_name: str, roi_data: Dict) -> Dict:
        """Data analytics business case template."""
        return {
            'problem_statement': [
                "Limited visibility into business performance",
                "Manual reporting is time-consuming",
                "Need for real-time analytics and insights"
            ],
            'proposed_solution': [
                "Implement comprehensive analytics platform",
                "Automated reporting and dashboards",
                "Real-time data integration",
                "Self-service analytics capabilities"
            ],
            'expected_outcomes': [
                "Reduce reporting time by 60-80%",
                "Improve decision-making speed",
                "Enable data-driven culture",
                "ROI of 150-300%"
            ]
        }

