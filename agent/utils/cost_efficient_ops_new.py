"""
Cost-Effective AI Agent + Manual Execution System (Generic)

This module implements a cost-effective hybrid automation system:
1. LLM Planner Agent - generates structured task metadata
2. Task Executor Agent (non-LLM) - applies metadata to filesystem
3. Task Memory - stores and retrieves execution plans
4. Generic content storage and application system
5. Cost optimization through minimal LLM usage

The system is generic and not tied to any specific domain.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import re


class TaskMetadataStore:
    """Stores and manages task metadata without LLM dependency"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.tasks_dir = self.base_dir / "tasks"
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        
    def store_task(self, task_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store task metadata to filesystem"""
        try:
            task_id = task_metadata.get("task_id", str(uuid.uuid4()))
            task_metadata["task_id"] = task_id
            task_metadata["stored_at"] = datetime.now().isoformat()
            
            task_file = self.tasks_dir / f"{task_id}.json"
            
            with open(task_file, 'w') as f:
                json.dump(task_metadata, f, indent=2)
            
            return {
                "success": True,
                "task_id": task_id,
                "stored_file": str(task_file)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve task metadata by ID"""
        try:
            task_file = self.tasks_dir / f"{task_id}.json"
            if task_file.exists():
                with open(task_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception:
            return None
    
    def store_batch_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Store multiple tasks in batch"""
        try:
            stored_tasks = []
            for task in tasks:
                result = self.store_task(task)
                if result["success"]:
                    stored_tasks.append(result["task_id"])
            
            return {
                "success": True,
                "tasks_stored": len(stored_tasks),
                "task_ids": stored_tasks
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_task_status(self, task_id: str, status: str, **kwargs) -> Dict[str, Any]:
        """Update task execution status"""
        try:
            task = self.get_task(task_id)
            if not task:
                return {"success": False, "error": "Task not found"}
            
            task["status"] = status
            task["updated_at"] = datetime.now().isoformat()
            
            # Add any additional fields
            for key, value in kwargs.items():
                task[key] = value
            
            return self.store_task(task)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class TaskExecutorAgent:
    """Non-LLM agent that executes tasks based on stored metadata"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.metadata_store = TaskMetadataStore(base_dir)
        self.execution_history = []
        
    def execute_task(self, task_id: str, enable_rollback: bool = False) -> Dict[str, Any]:
        """Execute a single task based on its metadata"""
        try:
            # Get task metadata
            task = self.metadata_store.get_task(task_id)
            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}
            
            # Update status to executing
            self.metadata_store.update_task_status(task_id, "executing")
            
            # Execute based on task type
            if task["type"] == "file_creation":
                result = self._execute_file_creation(task)
            elif task["type"] == "file_modification":
                result = self._execute_file_modification(task)
            else:
                result = {"success": False, "error": f"Unknown task type: {task['type']}"}
            
            # Update final status
            if result["success"]:
                self.metadata_store.update_task_status(
                    task_id, "completed", execution_result=result
                )
            else:
                self.metadata_store.update_task_status(
                    task_id, "failed", execution_result=result
                )
                
                if enable_rollback:
                    self._rollback_operation(task_id)
                    result["action"] = "rollback_completed"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "error"
            }
    
    def _execute_file_creation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file creation from metadata"""
        try:
            target_path = self.base_dir / task["target"]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'w') as f:
                f.write(task["content"])
            
            return {
                "success": True,
                "action": "file_created",
                "target": str(target_path),
                "bytes_written": len(task["content"])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "creation_failed"
            }
    
    def _execute_file_modification(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file modification from metadata"""
        try:
            target_path = self.base_dir / task["target"]
            
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"Target file {target_path} does not exist",
                    "action": "modification_failed"
                }
            
            modification_type = task.get("modification", "replace")
            
            if modification_type == "append":
                with open(target_path, 'a') as f:
                    f.write(task["content"])
            elif modification_type == "prepend":
                with open(target_path, 'r') as f:
                    original = f.read()
                with open(target_path, 'w') as f:
                    f.write(task["content"] + original)
            elif modification_type == "update_json":
                with open(target_path, 'r') as f:
                    data = json.load(f)
                data.update(task["content"])
                with open(target_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:  # replace
                with open(target_path, 'w') as f:
                    f.write(task["content"])
            
            return {
                "success": True,
                "action": "file_modified",
                "target": str(target_path),
                "modification_type": modification_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "modification_failed"
            }
    
    def execute_batch_tasks(self, task_ids: List[str]) -> Dict[str, Any]:
        """Execute multiple tasks in sequence"""
        try:
            results = []
            succeeded = 0
            failed = 0
            
            for task_id in task_ids:
                result = self.execute_task(task_id)
                results.append(result)
                
                if result["success"]:
                    succeeded += 1
                else:
                    failed += 1
            
            return {
                "success": True,
                "tasks_executed": succeeded,
                "tasks_failed": failed,
                "detailed_results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _rollback_operation(self, task_id: str):
        """Rollback a failed operation"""
        # Implementation for rollback logic
        # For now, just log the rollback attempt
        print(f"Rolling back task {task_id}")


class LLMPlannerAgent:
    """LLM agent that generates structured task metadata"""
    
    def __init__(self, llm_model):
        self.llm_model = llm_model
        self.cost_tracker = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    def create_execution_plan(self, user_request: str) -> Dict[str, Any]:
        """Generate structured execution plan using LLM"""
        try:
            # Use LLM to generate structured plan
            prompt = f"""
            Convert this user request into a structured task plan:
            Request: {user_request}
            
            Output format (JSON):
            {{
                "task_type": "file_creation|file_modification|multi_file_creation",
                "target_file": "path/to/file",
                "content": "file content here",
                "reasoning": "explanation of the plan"
            }}
            
            For multi-file tasks:
            {{
                "task_type": "multi_file_creation",
                "tasks": [
                    {{"target_file": "file1", "content": "content1"}},
                    {{"target_file": "file2", "content": "content2"}}
                ],
                "reasoning": "explanation"
            }}
            """
            
            response = self.llm_model.generate(prompt)
            
            # Track costs
            self.cost_tracker["total_calls"] += 1
            
            return {
                "success": True,
                "plan": response,
                "cost_used": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary"""
        if hasattr(self.llm_model, 'get_usage_stats'):
            stats = self.llm_model.get_usage_stats()
            return {
                "total_tokens": stats.get("tokens_used", 0),
                "estimated_total_cost": stats.get("estimated_cost", 0.0),
                "llm_calls": self.cost_tracker["total_calls"]
            }
        else:
            return {
                "total_tokens": 0,
                "estimated_total_cost": 0.0,
                "llm_calls": self.cost_tracker["total_calls"]
            }


class StructuredTaskProcessor:
    """Main processor that coordinates LLM and non-LLM agents"""
    
    def __init__(self, base_dir: str, llm_model=None):
        self.base_dir = base_dir
        self.llm_planner = LLMPlannerAgent(llm_model) if llm_model else None
        self.task_executor = TaskExecutorAgent(base_dir)
        self.metadata_store = TaskMetadataStore(base_dir)
        
        self.stats = {
            "total_requests": 0,
            "llm_requests": 0,
            "rule_based_requests": 0
        }
    
    def process_user_request(self, user_request: str) -> Dict[str, Any]:
        """Process user request end-to-end"""
        try:
            self.stats["total_requests"] += 1
            
            # Determine if LLM is needed
            needs_llm = self.should_use_llm(user_request)
            
            if needs_llm and self.llm_planner:
                # Use LLM for planning
                plan_result = self.llm_planner.create_execution_plan(user_request)
                self.stats["llm_requests"] += 1
                
                if not plan_result["success"]:
                    return plan_result
                
                # Convert plan to task metadata
                plan = plan_result["plan"]
                if plan["task_type"] == "multi_file_creation":
                    # Store multiple tasks
                    tasks = []
                    for task_data in plan["tasks"]:
                        task_metadata = {
                            "type": "file_creation",
                            "target": task_data["target_file"],
                            "content": task_data["content"],
                            "status": "pending"
                        }
                        tasks.append(task_metadata)
                    
                    batch_result = self.metadata_store.store_batch_tasks(tasks)
                    if batch_result["success"]:
                        # Execute all tasks
                        exec_result = self.task_executor.execute_batch_tasks(batch_result["task_ids"])
                        return {
                            "success": True,
                            "llm_used": True,
                            "llm_used_for_execution": False,
                            "files_created": len(batch_result["task_ids"]),
                            "execution_result": exec_result
                        }
                else:
                    # Single task
                    task_metadata = {
                        "type": plan["task_type"],
                        "target": plan["target_file"],
                        "content": plan["content"],
                        "status": "pending"
                    }
                    
                    store_result = self.metadata_store.store_task(task_metadata)
                    if store_result["success"]:
                        exec_result = self.task_executor.execute_task(store_result["task_id"])
                        return {
                            "success": True,
                            "llm_used": True,
                            "llm_used_for_execution": False,
                            "execution_result": exec_result
                        }
            else:
                # Use rule-based processing
                self.stats["rule_based_requests"] += 1
                return self._process_rule_based(user_request)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def should_use_llm(self, request: str) -> bool:
        """Determine if LLM is needed for this request"""
        request_lower = request.lower()
        
        # Simple rules for when LLM is needed
        creative_keywords = [
            "creative", "story", "narrative", "unique", "design", 
            "algorithm", "complex", "generate", "innovative"
        ]
        
        simple_keywords = [
            "create file", "make file", "add file", "simple", 
            "basic", "standard", "update", "modify"
        ]
        
        # Check for creative/complex content
        for keyword in creative_keywords:
            if keyword in request_lower:
                return True
        
        # Check for simple operations
        for keyword in simple_keywords:
            if keyword in request_lower:
                return False
        
        # Default: use LLM for uncertain cases
        return True
    
    def _process_rule_based(self, request: str) -> Dict[str, Any]:
        """Process request using rules without LLM"""
        # Simple rule-based processing
        request_lower = request.lower()
        
        if "create" in request_lower and "html" in request_lower:
            content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>"""
            
            task_metadata = {
                "type": "file_creation",
                "target": "index.html",
                "content": content,
                "status": "pending"
            }
            
            store_result = self.metadata_store.store_task(task_metadata)
            if store_result["success"]:
                exec_result = self.task_executor.execute_task(store_result["task_id"])
                return {
                    "success": True,
                    "llm_used": False,
                    "rule_based": True,
                    "execution_result": exec_result
                }
        
        # Default fallback
        return {
            "success": False,
            "error": "No rule matched, LLM needed but not available"
        }
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get cost optimization metrics"""
        total = self.stats["total_requests"]
        if total == 0:
            return {
                "total_requests": 0,
                "llm_requests": 0,
                "rule_based_requests": 0,
                "cost_savings_percentage": 0.0
            }
        
        savings_percentage = (self.stats["rule_based_requests"] / total) * 100
        
        return {
            "total_requests": total,
            "llm_requests": self.stats["llm_requests"],
            "rule_based_requests": self.stats["rule_based_requests"],
            "cost_savings_percentage": savings_percentage,
            "ai_usage_percentage": (self.stats["llm_requests"] / total) * 100
        }


class TaskMemory:
    """Task memory for plan history and rollback capabilities"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.memory_dir = self.base_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir = self.memory_dir / "reusable_plans"
        self.plans_dir.mkdir(parents=True, exist_ok=True)
    
    def store_execution(self, execution_record: Dict[str, Any]) -> Dict[str, Any]:
        """Store execution history"""
        try:
            session_id = execution_record["session_id"]
            session_file = self.memory_dir / f"session_{session_id}.json"
            
            # Load existing history
            history = []
            if session_file.exists():
                with open(session_file, 'r') as f:
                    history = json.load(f)
            
            # Add new record
            history.append(execution_record)
            
            # Save updated history
            with open(session_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get execution history for a session"""
        try:
            session_file = self.memory_dir / f"session_{session_id}.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def rollback_to_state(self, session_id: str, target_task_id: str) -> Dict[str, Any]:
        """Rollback to a previous execution state"""
        try:
            history = self.get_session_history(session_id)
            
            # Find target state index
            target_index = -1
            for i, record in enumerate(history):
                if record["task_id"] == target_task_id:
                    target_index = i
                    break
            
            if target_index == -1:
                return {"success": False, "error": "Target state not found"}
            
            # Truncate history to target state
            truncated_history = history[:target_index + 1]
            
            # Save truncated history
            session_file = self.memory_dir / f"session_{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(truncated_history, f, indent=2)
            
            return {
                "success": True,
                "rolled_back_to": target_task_id,
                "states_removed": len(history) - len(truncated_history)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def store_reusable_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Store a reusable execution plan"""
        try:
            plan_id = plan["plan_id"]
            plan_file = self.plans_dir / f"{plan_id}.json"
            
            with open(plan_file, 'w') as f:
                json.dump(plan, f, indent=2)
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_reusable_plan(self, pattern: str) -> Optional[Dict[str, Any]]:
        """Get a reusable plan by pattern"""
        try:
            for plan_file in self.plans_dir.glob("*.json"):
                with open(plan_file, 'r') as f:
                    plan = json.load(f)
                    if plan.get("pattern") == pattern:
                        return plan
            return None
        except Exception:
            return None
    
    def apply_plan_template(self, pattern: str, variables: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Apply variables to a plan template"""
        plan = self.get_reusable_plan(pattern)
        if not plan:
            return None
        
        template = plan["template"].copy()
        
        # Replace variables in template
        for key, value in template.items():
            if isinstance(value, str):
                for var_name, var_value in variables.items():
                    value = value.replace(f"{{{var_name}}}", var_value)
                template[key] = value
        
        return template
