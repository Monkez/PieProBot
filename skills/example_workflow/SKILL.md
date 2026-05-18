# Example Workflow Skill

Purpose: Demonstrate the on-disk skill format PiePro can load in future iterations.

Trigger: User asks for a repeatable implementation workflow.

Steps:
1. Inspect current runtime state.
2. Create a task plan.
3. Spawn a scoped subagent.
4. Validate the output.

Tools required:
- task.status
- memory.search

Validation:
- Task reaches completed status.
- Artifact or summary is attached to the task.
