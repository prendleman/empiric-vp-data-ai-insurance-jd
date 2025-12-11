"""
Fabric Dataflow Orchestrator

Orchestrates Fabric Gen2 dataflows.
"""

from typing import Dict, List, Optional
from fabric_workspace_manager import FabricWorkspaceManager

class FabricDataflowOrchestrator:
    """Orchestrates Fabric Gen2 dataflows."""
    
    def __init__(self, workspace_manager: FabricWorkspaceManager):
        """
        Initialize dataflow orchestrator.
        
        Args:
            workspace_manager: Fabric workspace manager instance
        """
        self.workspace_manager = workspace_manager
    
    def create_dataflow(self, workspace_id: str, dataflow_name: str, 
                       transformations: Optional[List[Dict]] = None):
        """
        Create a Fabric Gen2 dataflow.
        
        Args:
            workspace_id: Fabric workspace ID
            dataflow_name: Name of the dataflow
            transformations: List of transformation steps
        """
        # Create dataflow item
        dataflow_item = self.workspace_manager.create_dataflow(
            workspace_id=workspace_id,
            name=dataflow_name,
            description=f"Gen2 dataflow for {dataflow_name}"
        )
        
        # Build dataflow definition
        dataflow_definition = {
            "name": dataflow_name,
            "queries": [],
            "transformations": transformations or []
        }
        
        return {
            "item": dataflow_item,
            "definition": dataflow_definition
        }
    
    def add_query(self, dataflow_definition: Dict, query_name: str, 
                 source: str, query_steps: Optional[List[Dict]] = None):
        """Add a query to the dataflow."""
        query = {
            "name": query_name,
            "source": source,
            "steps": query_steps or []
        }
        
        dataflow_definition["queries"].append(query)
        return dataflow_definition
    
    def add_transformation(self, query: Dict, transformation_type: str, 
                          transformation_config: Dict):
        """Add a transformation step to a query."""
        transformation = {
            "type": transformation_type,
            "config": transformation_config
        }
        
        query["steps"].append(transformation)
        return query

