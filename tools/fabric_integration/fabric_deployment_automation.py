"""
Fabric Deployment Automation

Automates deployment of Power BI projects and semantic models to Fabric.
"""

import os
from pathlib import Path
from typing import Dict, Optional
from fabric_workspace_manager import FabricWorkspaceManager
from pbip_generator import PBIPGenerator

class FabricDeploymentAutomation:
    """Automates deployment to Microsoft Fabric."""
    
    def __init__(self, workspace_manager: FabricWorkspaceManager):
        """
        Initialize deployment automation.
        
        Args:
            workspace_manager: Fabric workspace manager instance
        """
        self.workspace_manager = workspace_manager
        self.pbip_generator = PBIPGenerator()
    
    def deploy_pbip_to_workspace(self, pbip_path: str, workspace_id: str, 
                                 dataset_name: Optional[str] = None):
        """
        Deploy a Power BI Project to a Fabric workspace.
        
        Args:
            pbip_path: Path to pbip project
            workspace_id: Target Fabric workspace ID
            dataset_name: Name for the dataset in Fabric
        """
        pbip_dir = Path(pbip_path)
        
        if not pbip_dir.exists():
            raise FileNotFoundError(f"pbip project not found: {pbip_path}")
        
        # Read report.json
        report_file = pbip_dir / "Report" / "report.json"
        if report_file.exists():
            import json
            with open(report_file, 'r') as f:
                report = json.load(f)
            
            dataset_name = dataset_name or report.get('name', 'Dataset')
        
        # In a real implementation, this would use Fabric REST API
        # to upload and deploy the pbip project
        print(f"Deploying {pbip_path} to workspace {workspace_id} as {dataset_name}")
        
        return {
            "status": "deployed",
            "workspace_id": workspace_id,
            "dataset_name": dataset_name,
            "pbip_path": pbip_path
        }
    
    def create_fabric_analytics_solution(self, workspace_id: str, solution_name: str,
                                        config: Dict):
        """
        Create a complete Fabric analytics solution.
        
        Args:
            workspace_id: Fabric workspace ID
            solution_name: Name of the solution
            config: Solution configuration
        """
        solution_components = []
        
        # Create Lakehouse if specified
        if config.get('create_lakehouse'):
            lakehouse = self.workspace_manager.create_lakehouse(
                workspace_id=workspace_id,
                name=f"{solution_name}_Lakehouse",
                description=f"Lakehouse for {solution_name}"
            )
            solution_components.append({"type": "Lakehouse", "item": lakehouse})
        
        # Create Dataflow if specified
        if config.get('create_dataflow'):
            dataflow = self.workspace_manager.create_dataflow(
                workspace_id=workspace_id,
                name=f"{solution_name}_Dataflow",
                description=f"Dataflow for {solution_name}"
            )
            solution_components.append({"type": "Dataflow", "item": dataflow})
        
        # Create Semantic Model if specified
        if config.get('create_semantic_model'):
            semantic_model = self.workspace_manager.create_semantic_model(
                workspace_id=workspace_id,
                name=f"{solution_name}_SemanticModel",
                description=f"Semantic model for {solution_name}"
            )
            solution_components.append({"type": "SemanticModel", "item": semantic_model})
        
        return {
            "solution_name": solution_name,
            "workspace_id": workspace_id,
            "components": solution_components
        }

