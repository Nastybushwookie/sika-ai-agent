import json
from typing import Dict, Any


class DecisionTreeEngine:
    """JSON-based decision tree engine for IT troubleshooting flows."""
    
    def __init__(self):
        self.trees = {}
        
    def load_tree(self, tree_path: str) -> None:
        """Load a decision tree from JSON file."""
        with open(tree_path) as f:
            tree_data = json.load(f)
            
        issue_type = tree_data["issue_type"]
        self.trees[issue_type] = {
            "nodes": {},
            "current_node": None
        }
        
        # Build nodes dictionary
        for node_id, node_data in tree_data.items():
            if node_id != 'issue_type' and isinstance(node_data, dict):
                self.trees[issue_type]["nodes"][node_id] = node_data
                
    def start_troubleshooting(self, issue_type: str) -> Dict[str, Any]:
        """Start a new troubleshooting session."""
        tree = self.trees.get(issue_type)
        if not tree:
            raise ValueError(f"Decision tree not found for: {issue_type}")
            
        # Get root node
        root_node = tree["nodes"].get("root") or next(iter(tree["nodes"]))
        tree["current_node"] = root_node
        self.current_issue_type = issue_type  # Track which tree is active
        
        return {
            "question": tree["nodes"][root_node]["question"],
            "options": tree["nodes"][root_node].get("options", []),
            "issue_type": issue_type
        }
        
    def process_response(self, user_answer: str) -> Dict[str, Any]:
        """Process user response and move to next node."""
        tree = self.trees[self.current_issue_type]
        current_node = tree["current_node"]
        
        # Find matching option (case-insensitive partial match)
        matched_option = None
        for option in current_node.get("options", []):
            if user_answer.lower() in option["text"].lower():
                matched_option = option
                break
                
        if not matched_option:
            return {"status": "error", "message": "I didn't understand your answer. Please respond with 'Yes' or 'No', or select from the available options."}
            
        # Check for resolution (leaf node)
        if "resolution" in matched_option:
            tree["current_node"] = None  # End session
            return {
                "status": "resolved",
                "resolution": matched_option["resolution"],
                "next_steps": matched_option.get("next_steps")
            }
            
        # Move to next node
        next_node_id = matched_option["next_node"]
        tree["current_node"] = tree["nodes"][next_node_id]
        
        return {
            "status": "continue",
            "question": tree["current_node"]["question"],
            "options": tree["current_node"].get("options", [])
        }
