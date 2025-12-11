"""
Semantic Model Builder

Builds Fabric semantic models programmatically.
"""

import json
from typing import Dict, List, Optional
from fabric_workspace_manager import FabricWorkspaceManager

class SemanticModelBuilder:
    """Builds semantic models for Microsoft Fabric."""
    
    def __init__(self, workspace_manager: FabricWorkspaceManager):
        """
        Initialize semantic model builder.
        
        Args:
            workspace_manager: Fabric workspace manager instance
        """
        self.workspace_manager = workspace_manager
    
    def create_semantic_model(self, workspace_id: str, model_name: str, 
                             data_source: str, tables: Optional[List[Dict]] = None):
        """
        Create a semantic model in Fabric.
        
        Args:
            workspace_id: Fabric workspace ID
            model_name: Name of the semantic model
            data_source: Data source (e.g., 'lakehouse', 'sql', 'api')
            tables: List of table definitions
        """
        # Create semantic model item
        model_item = self.workspace_manager.create_semantic_model(
            workspace_id=workspace_id,
            name=model_name,
            description=f"Semantic model for {model_name}"
        )
        
        # Build model structure
        model_structure = {
            "name": model_name,
            "tables": tables or [],
            "relationships": [],
            "cultures": []
        }
        
        return {
            "item": model_item,
            "model_structure": model_structure
        }
    
    def add_table(self, model_structure: Dict, table_name: str, 
                 columns: List[Dict], measures: Optional[List[Dict]] = None):
        """Add a table to the semantic model."""
        table = {
            "name": table_name,
            "columns": columns,
            "measures": measures or []
        }
        
        model_structure["tables"].append(table)
        return model_structure
    
    def add_relationship(self, model_structure: Dict, from_table: str, 
                        from_column: str, to_table: str, to_column: str):
        """Add a relationship to the semantic model."""
        relationship = {
            "name": f"{from_table}_{from_column}_to_{to_table}_{to_column}",
            "fromTable": from_table,
            "fromColumn": from_column,
            "toTable": to_table,
            "toColumn": to_column,
            "cardinality": "ManyToOne"
        }
        
        model_structure["relationships"].append(relationship)
        return model_structure

