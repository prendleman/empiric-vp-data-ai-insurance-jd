"""
Executive Presentation Generator

Generates executive-ready presentations from analytics results.
"""

from datetime import datetime
from typing import Dict, List, Optional
import json

class PresentationGenerator:
    """Generates executive presentations."""
    
    def __init__(self):
        """Initialize presentation generator."""
        self.templates = {
            'analytics_review': self._analytics_review_template,
            'business_case': self._business_case_template,
            'quarterly_review': self._quarterly_review_template
        }
    
    def generate_presentation(self, analytics_results: Dict, 
                            presentation_type: str = 'analytics_review',
                            title: str = "Executive Presentation"):
        """
        Generate executive presentation.
        
        Args:
            analytics_results: Dictionary with analytics results
            presentation_type: Type of presentation
            title: Presentation title
        """
        template = self.templates.get(presentation_type, self._analytics_review_template)
        
        presentation = {
            'metadata': {
                'title': title,
                'generated_date': datetime.now().isoformat(),
                'presentation_type': presentation_type,
                'version': '1.0'
            },
            'slides': template(analytics_results)
        }
        
        return presentation
    
    def _analytics_review_template(self, results: Dict) -> List[Dict]:
        """Analytics review presentation template."""
        slides = []
        
        # Title slide
        slides.append({
            'slide_number': 1,
            'type': 'title',
            'title': 'Analytics Review',
            'subtitle': datetime.now().strftime('%B %Y'),
            'content': []
        })
        
        # Executive summary
        slides.append({
            'slide_number': 2,
            'type': 'summary',
            'title': 'Executive Summary',
            'content': self._extract_key_insights(results)
        })
        
        # Key metrics
        if 'summary' in results or 'metrics' in results:
            slides.append({
                'slide_number': 3,
                'type': 'metrics',
                'title': 'Key Metrics',
                'content': self._extract_metrics(results)
            })
        
        # Business impact
        if 'roi' in results or 'business_impact' in results:
            slides.append({
                'slide_number': 4,
                'type': 'business_impact',
                'title': 'Business Impact',
                'content': self._extract_business_impact(results)
            })
        
        # Recommendations
        slides.append({
            'slide_number': 5,
            'type': 'recommendations',
            'title': 'Recommendations',
            'content': self._generate_recommendations(results)
        })
        
        return slides
    
    def _business_case_template(self, results: Dict) -> List[Dict]:
        """Business case presentation template."""
        slides = []
        
        # Title slide
        slides.append({
            'slide_number': 1,
            'type': 'title',
            'title': 'Business Case',
            'subtitle': results.get('initiative_name', 'Data & AI Initiative'),
            'content': []
        })
        
        # Problem statement
        slides.append({
            'slide_number': 2,
            'type': 'problem',
            'title': 'Business Challenge',
            'content': results.get('problem_statement', [])
        })
        
        # Proposed solution
        slides.append({
            'slide_number': 3,
            'type': 'solution',
            'title': 'Proposed Solution',
            'content': results.get('solution_description', [])
        })
        
        # ROI analysis
        if 'roi' in results:
            slides.append({
                'slide_number': 4,
                'type': 'roi',
                'title': 'Return on Investment',
                'content': self._format_roi_slide(results['roi'])
            })
        
        # Implementation plan
        slides.append({
            'slide_number': 5,
            'type': 'implementation',
            'title': 'Implementation Plan',
            'content': results.get('implementation_plan', [])
        })
        
        return slides
    
    def _quarterly_review_template(self, results: Dict) -> List[Dict]:
        """Quarterly review presentation template."""
        slides = []
        
        # Title slide
        slides.append({
            'slide_number': 1,
            'type': 'title',
            'title': 'Quarterly Business Review',
            'subtitle': f"Q{datetime.now().month // 4 + 1} {datetime.now().year}",
            'content': []
        })
        
        # Performance summary
        slides.append({
            'slide_number': 2,
            'type': 'performance',
            'title': 'Performance Summary',
            'content': self._extract_performance_metrics(results)
        })
        
        # Key achievements
        slides.append({
            'slide_number': 3,
            'type': 'achievements',
            'title': 'Key Achievements',
            'content': results.get('achievements', [])
        })
        
        # Challenges and opportunities
        slides.append({
            'slide_number': 4,
            'type': 'challenges',
            'title': 'Challenges & Opportunities',
            'content': results.get('challenges', [])
        })
        
        # Next quarter priorities
        slides.append({
            'slide_number': 5,
            'type': 'priorities',
            'title': 'Next Quarter Priorities',
            'content': results.get('priorities', [])
        })
        
        return slides
    
    def _extract_key_insights(self, results: Dict) -> List[str]:
        """Extract key insights from results."""
        insights = []
        
        if 'summary' in results:
            summary = results['summary']
            if 'key_insights' in summary:
                insights.extend(summary['key_insights'])
        
        if 'executive_summary' in results:
            exec_summary = results['executive_summary']
            if 'key_metrics' in exec_summary:
                insights.append(f"Total policies: {exec_summary['key_metrics'].get('total_policies', 'N/A')}")
        
        return insights if insights else ["Key insights will be generated from analytics results"]
    
    def _extract_metrics(self, results: Dict) -> Dict:
        """Extract metrics from results."""
        metrics = {}
        
        if 'summary' in results:
            metrics.update(results['summary'])
        elif 'metrics' in results:
            metrics.update(results['metrics'])
        
        return metrics
    
    def _extract_business_impact(self, results: Dict) -> Dict:
        """Extract business impact from results."""
        impact = {}
        
        if 'roi' in results:
            impact['roi'] = results['roi']
        elif 'business_impact' in results:
            impact = results['business_impact']
        elif 'roi_metrics' in results:
            impact = results['roi_metrics']
        
        return impact
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations from results."""
        recommendations = []
        
        if 'recommendations' in results:
            recommendations.extend(results['recommendations'])
        elif 'executive_summary' in results and 'recommendations' in results['executive_summary']:
            recommendations.extend(results['executive_summary']['recommendations'])
        else:
            recommendations = [
                "Continue monitoring key metrics",
                "Implement recommended improvements",
                "Review and adjust strategies based on results"
            ]
        
        return recommendations
    
    def _format_roi_slide(self, roi_data: Dict) -> List[str]:
        """Format ROI data for slide."""
        content = []
        
        if isinstance(roi_data, dict):
            if 'roi_percentage' in roi_data:
                content.append(f"ROI: {roi_data['roi_percentage']:.1f}%")
            if 'net_benefit_annual' in roi_data:
                content.append(f"Annual Net Benefit: ${roi_data['net_benefit_annual']:,.0f}")
            if 'payback_period_months' in roi_data:
                content.append(f"Payback Period: {roi_data['payback_period_months']:.1f} months")
        
        return content if content else ["ROI analysis will be included"]
    
    def _extract_performance_metrics(self, results: Dict) -> Dict:
        """Extract performance metrics."""
        return results.get('performance_metrics', {})
    
    def save_presentation(self, presentation: Dict, output_path: str):
        """Save presentation to file."""
        with open(output_path, 'w') as f:
            json.dump(presentation, f, indent=2, default=str)
        print(f"Presentation saved to {output_path}")

