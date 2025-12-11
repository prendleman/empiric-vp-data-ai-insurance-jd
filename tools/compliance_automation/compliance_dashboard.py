"""
Compliance Dashboard

Tracks compliance metrics, deadlines, and risk scores.
"""

import pandas as pd
from datetime import datetime, timedelta
import json

class ComplianceDashboard:
    """Generates compliance dashboard and tracks metrics."""
    
    def __init__(self):
        """Initialize compliance dashboard."""
        self.deadlines = []
        self.compliance_scores = {}
        self.risk_scores = {}
    
    def track_deadline(self, report_type, deadline_date, status='pending'):
        """Track compliance deadline."""
        self.deadlines.append({
            'report_type': report_type,
            'deadline_date': deadline_date,
            'status': status,
            'days_remaining': (deadline_date - datetime.now()).days,
            'tracked_date': datetime.now()
        })
    
    def update_compliance_score(self, category, score, timestamp=None):
        """Update compliance score for a category."""
        if timestamp is None:
            timestamp = datetime.now()
        
        if category not in self.compliance_scores:
            self.compliance_scores[category] = []
        
        self.compliance_scores[category].append({
            'score': score,
            'timestamp': timestamp.isoformat()
        })
    
    def calculate_risk_score(self, compliance_scores, deadline_status):
        """
        Calculate overall compliance risk score.
        
        Args:
            compliance_scores: Dictionary of compliance scores by category
            deadline_status: List of deadline statuses
            
        Returns:
            Risk score (0-100, higher = more risk)
        """
        # Calculate average compliance score
        if compliance_scores:
            avg_compliance = sum(
                scores[-1]['score'] if isinstance(scores, list) else scores
                for scores in compliance_scores.values()
            ) / len(compliance_scores)
        else:
            avg_compliance = 100
        
        # Calculate deadline risk
        overdue_deadlines = sum(1 for d in deadline_status if d['status'] == 'overdue')
        total_deadlines = len(deadline_status)
        deadline_risk = (overdue_deadlines / total_deadlines * 100) if total_deadlines > 0 else 0
        
        # Combined risk score (inverse of compliance)
        risk_score = 100 - avg_compliance + deadline_risk * 0.5
        risk_score = max(0, min(100, risk_score))
        
        return {
            'overall_risk_score': risk_score,
            'compliance_score': avg_compliance,
            'deadline_risk': deadline_risk,
            'risk_level': 'High' if risk_score >= 70 else ('Medium' if risk_score >= 40 else 'Low')
        }
    
    def generate_dashboard(self, output_path='compliance_dashboard.json'):
        """Generate compliance dashboard."""
        # Get upcoming deadlines
        upcoming_deadlines = [
            d for d in self.deadlines
            if d['days_remaining'] >= 0 and d['status'] == 'pending'
        ]
        upcoming_deadlines.sort(key=lambda x: x['days_remaining'])
        
        # Get overdue deadlines
        overdue_deadlines = [
            d for d in self.deadlines
            if d['days_remaining'] < 0 and d['status'] != 'completed'
        ]
        
        # Calculate risk score
        risk_assessment = self.calculate_risk_score(
            self.compliance_scores,
            self.deadlines
        )
        
        dashboard = {
            'metadata': {
                'title': 'Compliance Dashboard',
                'generated_date': datetime.now().isoformat(),
                'version': '1.0'
            },
            'risk_assessment': risk_assessment,
            'deadlines': {
                'upcoming': upcoming_deadlines[:5],  # Next 5
                'overdue': overdue_deadlines,
                'total_pending': len([d for d in self.deadlines if d['status'] == 'pending']),
                'total_completed': len([d for d in self.deadlines if d['status'] == 'completed'])
            },
            'compliance_scores': {
                category: scores[-1] if isinstance(scores, list) else scores
                for category, scores in self.compliance_scores.items()
            },
            'recommendations': self._generate_recommendations(risk_assessment, overdue_deadlines)
        }
        
        with open(output_path, 'w') as f:
            json.dump(dashboard, f, indent=2, default=str)
        
        print(f"Compliance dashboard saved to {output_path}")
        return dashboard
    
    def _generate_recommendations(self, risk_assessment, overdue_deadlines):
        """Generate compliance recommendations."""
        recommendations = []
        
        if risk_assessment['risk_level'] == 'High':
            recommendations.append({
                'priority': 'Critical',
                'recommendation': 'Immediate action required to address compliance gaps',
                'action_items': [
                    'Review and address overdue deadlines',
                    'Improve data quality scores',
                    'Implement additional compliance controls'
                ]
            })
        
        if len(overdue_deadlines) > 0:
            recommendations.append({
                'priority': 'High',
                'recommendation': f'Address {len(overdue_deadlines)} overdue compliance deadlines',
                'action_items': [
                    f"Complete {d['report_type']} report" for d in overdue_deadlines[:3]
                ]
            })
        
        if risk_assessment['compliance_score'] < 90:
            recommendations.append({
                'priority': 'Medium',
                'recommendation': 'Improve data quality and compliance scores',
                'action_items': [
                    'Review data validation rules',
                    'Enhance data governance processes',
                    'Implement automated quality checks'
                ]
            })
        
        return recommendations

