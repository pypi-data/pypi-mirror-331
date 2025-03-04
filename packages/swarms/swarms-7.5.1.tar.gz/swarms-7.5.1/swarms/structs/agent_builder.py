import os
from typing import List

from pydantic import BaseModel, Field

from swarms.structs.agent import Agent
from swarms.utils.function_caller_model import OpenAIFunctionCaller
from swarms.utils.loguru_logger import initialize_logger
from swarms.structs.agents_available import showcase_available_agents
from swarms.structs.swarms_api import AgentInput as AgentConfig
from swarms.utils.any_to_str import any_to_str
from swarms.utils.litellm_tokenizer import count_tokens

logger = initialize_logger(log_folder="auto_swarm_builder")


class Agents(BaseModel):
    """Configuration for a list of agents"""

    agents: List[AgentConfig] = Field(
        description="The list of agents that make up the swarm",
    )


BOSS_SYSTEM_PROMPT = """
# Swarm Intelligence Orchestrator

You are the Chief Orchestrator of a sophisticated agent swarm. Your primary responsibility is to analyze tasks and create the optimal team of specialized agents to accomplish complex objectives efficiently.

## Agent Creation Protocol

1. **Task Analysis**:
   - Thoroughly analyze the user's task to identify all required skills, knowledge domains, and subtasks
   - Break down complex problems into discrete components that can be assigned to specialized agents
   - Identify potential challenges and edge cases that might require specialized handling

2. **Agent Design Principles**:
   - Create highly specialized agents with clearly defined roles and responsibilities
   - Design each agent with deep expertise in their specific domain
   - Provide agents with comprehensive system prompts that include:
     * Precise definition of their role and scope of responsibility
     * Detailed methodology for approaching problems in their domain
     * Specific techniques, frameworks, and mental models to apply
     * Guidelines for output format and quality standards
     * Instructions for collaboration with other agents

3. **Cognitive Enhancement**:
   - Equip agents with advanced reasoning frameworks:
     * First principles thinking to break down complex problems
     * Systems thinking to understand interconnections
     * Lateral thinking for creative solutions
     * Critical thinking to evaluate information quality
   - Implement specialized thought patterns:
     * Step-by-step reasoning for complex problems
     * Hypothesis generation and testing
     * Counterfactual reasoning to explore alternatives
     * Analogical reasoning to apply solutions from similar domains

4. **Swarm Architecture**:
   - Design optimal agent interaction patterns based on task requirements
   - Consider hierarchical, networked, or hybrid structures
   - Establish clear communication protocols between agents
   - Define escalation paths for handling edge cases

5. **Agent Specialization Examples**:
   - Research Agents: Literature review, data gathering, information synthesis
   - Analysis Agents: Data processing, pattern recognition, insight generation
   - Creative Agents: Idea generation, content creation, design thinking
   - Planning Agents: Strategy development, resource allocation, timeline creation
   - Implementation Agents: Code writing, document drafting, execution planning
   - Quality Assurance Agents: Testing, validation, error detection
   - Integration Agents: Combining outputs, ensuring consistency, resolving conflicts

## Output Format

For each agent, provide:

1. **Agent Name**: Clear, descriptive title reflecting specialization
2. **Description**: Concise overview of the agent's purpose and capabilities
3. **System Prompt**: Comprehensive instructions including:
   - Role definition and responsibilities
   - Specialized knowledge and methodologies
   - Thinking frameworks and problem-solving approaches
   - Output requirements and quality standards
   - Collaboration guidelines with other agents

## Optimization Guidelines

- Create only the agents necessary for the task - no more, no less
- Ensure each agent has a distinct, non-overlapping area of responsibility
- Design system prompts that maximize agent performance through clear guidance and specialized knowledge
- Balance specialization with the need for effective collaboration
- Prioritize agents that address the most critical aspects of the task

Remember: Your goal is to create a swarm of agents that collectively possesses the intelligence, knowledge, and capabilities to deliver exceptional results for the user's task.
"""


class AgentsBuilder:
    """A class that automatically builds and manages swarms of AI agents.

    This class handles the creation, coordination and execution of multiple AI agents working
    together as a swarm to accomplish complex tasks. It uses a boss agent to delegate work
    and create new specialized agents as needed.

    Args:
        name (str): The name of the swarm
        description (str): A description of the swarm's purpose
        verbose (bool, optional): Whether to output detailed logs. Defaults to True.
        max_loops (int, optional): Maximum number of execution loops. Defaults to 1.
    """

    def __init__(
        self,
        name: str = "swarm-creator-01",
        description: str = "This is a swarm that creates swarms",
        verbose: bool = True,
        max_loops: int = 1,
    ):
        self.name = name
        self.description = description
        self.verbose = verbose
        self.max_loops = max_loops
        self.agents_pool = []

        logger.info(
            f"Initialized AutoSwarmBuilder: {name} {description}"
        )

    def run(self, task: str, image_url: str = None, *args, **kwargs):
        """Run the swarm on a given task.

        Args:
            task (str): The task to be accomplished
            image_url (str, optional): URL of an image input if needed. Defaults to None.
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            The output from the swarm's execution
        """
        logger.info(f"Running swarm on task: {task}")
        agents, tokens = self._create_agents(task, image_url, *args, **kwargs)

        return agents, tokens

    def _create_agents(self, task: str, *args, **kwargs):
        """Create the necessary agents for a task.

        Args:
            task (str): The task to create agents for
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            list: List of created agents
        """
        logger.info("Creating agents for task")
        model = OpenAIFunctionCaller(
            system_prompt=BOSS_SYSTEM_PROMPT,
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1,
            base_model=Agents,
        )

        agents_dictionary = model.run(task)
        agents_dictionary = any_to_str(agents_dictionary)
        
        tokens = count_tokens(agents_dictionary)
        logger.info(f"Tokens: {tokens}")
        
        logger.info(f"Agents dictionary: {agents_dictionary}")

        # Convert dictionary to SwarmConfig if needed
        if isinstance(agents_dictionary, dict):
            agents_dictionary = Agents(**agents_dictionary)

        # Create agents from config
        agents = []
        for agent_config in agents_dictionary.agents:
            # Convert dict to AgentConfig if needed
            if isinstance(agent_config, dict):
                agent_config = AgentConfig(**agent_config)

            agent = self.build_agent(
                agent_name=agent_config.name,
                agent_description=agent_config.description,
                agent_system_prompt=agent_config.system_prompt,
                model_name=agent_config.model_name,
                max_loops=agent_config.max_loops,
                dynamic_temperature_enabled=agent_config.dynamic_temperature_enabled,
                auto_generate_prompt=agent_config.auto_generate_prompt,
                role=agent_config.role,
                max_tokens=agent_config.max_tokens,
                temperature=agent_config.temperature,
            )
            agents.append(agent)

        # Showcasing available agents
        agents_available = showcase_available_agents(
            name=self.name,
            description=self.description,
            agents=agents,
        )

        for agent in agents:
            agent.system_prompt += "\n" + agents_available

        return agents, tokens

    def build_agent(
        self,
        agent_name: str,
        agent_description: str,
        agent_system_prompt: str,
        max_loops: int = 1,
        model_name: str = "gpt-4o",
        dynamic_temperature_enabled: bool = True,
        auto_generate_prompt: bool = False,
        role: str = "worker",
        max_tokens: int = 8192,
        temperature: float = 0.5,
    ):
        """Build a single agent with the given specifications.

        Args:
            agent_name (str): Name of the agent
            agent_description (str): Description of the agent's purpose
            agent_system_prompt (str): The system prompt for the agent

        Returns:
            Agent: The constructed agent instance
        """
        logger.info(f"Building agent: {agent_name}")
        agent = Agent(
            agent_name=agent_name,
            description=agent_description,
            system_prompt=agent_system_prompt,
            model_name=model_name,
            max_loops=max_loops,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            context_length=200000,
            output_type="str",  # "json", "dict", "csv" OR "string" soon "yaml" and
            streaming_on=False,
            auto_generate_prompt=auto_generate_prompt,
            role=role,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return agent
