"""
Power BI Project (pbip) Generator

Generates Power BI Project files in pbip v7 format.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class PBIPGenerator:
    """Generates Power BI Project files in pbip v7 format."""
    
    def __init__(self):
        """Initialize pbip generator."""
        self.pbip_version = "7.0"
        self.pbip_format_version = "1.0"
    
    def create_pbip_project(self, project_name: str, output_path: str, 
                           report_config: Optional[Dict] = None):
        """
        Create a Power BI Project in pbip v7 format.
        
        Args:
            project_name: Name of the project
            output_path: Path to create the pbip project
            report_config: Configuration for the report
        """
        # Create project directory
        project_dir = Path(output_path)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .pbi directory
        pbi_dir = project_dir / ".pbi"
        pbi_dir.mkdir(exist_ok=True)
        
        # Create Data Model directory
        data_model_dir = project_dir / "Data Model"
        data_model_dir.mkdir(exist_ok=True)
        
        # Create Report directory
        report_dir = project_dir / "Report"
        report_dir.mkdir(exist_ok=True)
        
        # Create .pbi/globalSettings.json
        self._create_global_settings(pbi_dir)
        
        # Create .pbi/localSettings.json
        self._create_local_settings(pbi_dir)
        
        # Create Data Model files
        self._create_data_model(data_model_dir, report_config)
        
        # Create Report files
        self._create_report(report_dir, project_name, report_config)
        
        print(f"Power BI Project created at {output_path}")
        return output_path
    
    def _create_global_settings(self, pbi_dir: Path):
        """Create globalSettings.json file."""
        global_settings = {
            "version": self.pbip_version,
            "formatVersion": self.pbip_format_version,
            "createdDate": datetime.now().isoformat(),
            "settings": {
                "queryGroup": {
                    "enabled": True
                },
                "reportMetadata": {
                    "enabled": True
                }
            }
        }
        
        settings_file = pbi_dir / "globalSettings.json"
        with open(settings_file, 'w') as f:
            json.dump(global_settings, f, indent=2)
    
    def _create_local_settings(self, pbi_dir: Path):
        """Create localSettings.json file."""
        local_settings = {
            "version": self.pbip_version,
            "formatVersion": self.pbip_format_version,
            "localSettings": {
                "queryGroup": {
                    "enabled": True
                }
            }
        }
        
        settings_file = pbi_dir / "localSettings.json"
        with open(settings_file, 'w') as f:
            json.dump(local_settings, f, indent=2)
    
    def _create_data_model(self, data_model_dir: Path, config: Optional[Dict]):
        """Create data model files."""
        # Create model.bim (Basic Information Model) file
        model_bim = {
            "name": "Model",
            "tables": [],
            "relationships": [],
            "cultures": [],
            "version": "1.0"
        }
        
        if config and 'tables' in config:
            model_bim["tables"] = config['tables']
        
        bim_file = data_model_dir / "model.bim"
        with open(bim_file, 'w') as f:
            json.dump(model_bim, f, indent=2)
    
    def _create_report(self, report_dir: Path, project_name: str, config: Optional[Dict]):
        """Create report files."""
        # Create report.json
        report_json = {
            "version": self.pbip_version,
            "name": project_name,
            "sections": [],
            "theme": {
                "name": "Default",
                "dataColors": [
                    "#118DFF", "#12239E", "#E66C37", "#6B007B",
                    "#E044A7", "#744EC2", "#D9B300", "#D64550"
                ]
            },
            "settings": {
                "useDefaultVisuals": True
            }
        }
        
        if config and 'sections' in config:
            report_json["sections"] = config['sections']
        
        report_file = report_dir / "report.json"
        with open(report_file, 'w') as f:
            json.dump(report_json, f, indent=2)
    
    def add_table_to_model(self, pbip_path: str, table_name: str, 
                          columns: List[Dict], measures: Optional[List[Dict]] = None):
        """
        Add a table to the data model.
        
        Args:
            pbip_path: Path to pbip project
            table_name: Name of the table
            columns: List of column definitions
            measures: List of measure definitions
        """
        model_file = Path(pbip_path) / "Data Model" / "model.bim"
        
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")
        
        with open(model_file, 'r') as f:
            model = json.load(f)
        
        table = {
            "name": table_name,
            "columns": columns,
            "measures": measures or [],
            "partitions": []
        }
        
        model["tables"].append(table)
        
        with open(model_file, 'w') as f:
            json.dump(model, f, indent=2)
    
    def add_visual_to_report(self, pbip_path: str, section_name: str, 
                            visual_config: Dict):
        """
        Add a visual to the report.
        
        Args:
            pbip_path: Path to pbip project
            section_name: Name of the section
            visual_config: Visual configuration
        """
        report_file = Path(pbip_path) / "Report" / "report.json"
        
        if not report_file.exists():
            raise FileNotFoundError(f"Report file not found: {report_file}")
        
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        # Find or create section
        section = None
        for sec in report["sections"]:
            if sec["name"] == section_name:
                section = sec
                break
        
        if not section:
            section = {
                "name": section_name,
                "displayName": section_name,
                "visuals": []
            }
            report["sections"].append(section)
        
        section["visuals"].append(visual_config)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

