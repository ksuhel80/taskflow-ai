from __future__ import annotations

from dataclasses import dataclass

from ..base.contracts import AgentRole, AgentStepSpec


@dataclass(frozen=True)
class AgentRoleAssignment:
    """
    Assignment of roles for a workflow step.

    Example: for "Sprint Planning" step "Researcher", assigned roles include
    - researcher
    - scrum_master (optional collaboration)
    """

    role: AgentRole
    rolePriority: int = 100


class AgentRegistry:
    """
    Registry mapping a workflow step to agent roles and (later) prompt/tool policies.
    """

    def __init__(self) -> None:
        # Design-only mapping.
        self._byStep: dict[str, list[AgentRoleAssignment]] = {
            "researcher_analyze_history": [
                AgentRoleAssignment(role="researcher"),
                AgentRoleAssignment(role="scrum_master", rolePriority=200),
            ],
            "planner_propose_allocation": [AgentRoleAssignment(role="planner")],
            "reviewer_validate_workload": [AgentRoleAssignment(role="reviewer")],
            "human_confidence_and_approval": [AgentRoleAssignment(role="reviewer")],
        }

    def get_roles_for_step(self, *, stepSpec: AgentStepSpec) -> list[AgentRoleAssignment]:
        return sorted(self._byStep.get(stepSpec.stepId, []), key=lambda a: a.rolePriority)

