import enum


class AgentIdentifier(enum.Enum):
    workflow_support_agent = 1
    workflow_agent = 2
    event_selection_agent = 3
    impact_analysis_agent = 4
    constraint_selection_agent = 5
    solution_design_agent = 7
    high_level_solution = 8
    solution_modeling_agent = 9
    enterprise_generation_agent = 10
