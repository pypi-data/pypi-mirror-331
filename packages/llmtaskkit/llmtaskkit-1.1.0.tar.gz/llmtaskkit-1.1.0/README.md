# LLMTaskKit

LLMTaskKit is a Python library designed to simplify the definition, execution, and chaining of tasks that leverage large language models (LLMs). It provides a flexible framework for creating tasks, executing them via configurable executors, and integrating data validation using Pydantic models. With built‐in support for YAML-based task definitions (including a custom `thinking` tag), LLMTaskKit streamlines the creation of complex workflows that require dynamic prompt generation and iterative processing.

## Table of Contents

- [Overview](#overview)
- [Key Components](#key-components)
  - [Tasks](#tasks)
  - [TaskExecutors](#taskexecutors)
  - [ChainTaskExecutors](#chaintaskexecutors)
  - [Pydantic Integration](#pydantic-integration)
  - [Custom `thinking` YAML Tag](#custom-thinking-yaml-tag)
- [Project Examples](#project-examples)
- [Dependencies and Configuration](#dependencies-and-configuration)
- [Getting Started](#getting-started)
- [License](#license)

## Overview

LLMTaskKit enables developers to create and manage LLM-driven workflows by abstracting tasks into self-contained units. Each task includes prompts, context, and optional output validation through Pydantic models. The library supports both standalone task execution as well as sequential (chained) execution for more complex processing pipelines.

## Installation

```bash
poetry install
```

## Key Components

### Tasks

A **Task** in LLMTaskKit represents a discrete unit of work that contains the following **special fields**:
- **name**: The unique identifier for the task.
- **system_prompt**: Defines the context and instructions for the LLM.
- **thinking**: (Optional) Contains internal reasoning or additional instructions to guide the LLM's response.

All other fields can be defined as needed, and the order of definition is preserved. For instance, you might include custom fields like `goal` or `description` to provide extra context. Additionally, you can retrieve the result of a previous task by using the syntax `{{TASK_RESULT.OtherTaskName}}`, where `OtherTaskName` corresponds to the name of the preceding task. You can also embed dynamic variables using the `{{var}}` syntax; for example, `{{prompt_detail}}` will be replaced with the value provided in the execution context (e.g., `context.prompt_detail`).

Tasks are typically defined in YAML format and then instantiated in Python. For example:

```yaml
# Example with dynamic variable substitution:
- name: MarketingStrategyAnalysis
  system_prompt: |
    You are a "Marketing Strategist". Analyze the provided product details and campaign information to devise a comprehensive marketing strategy.
  product_info: "{{product_details}}"
  campaign_name: "{{campaign}}"
  campaign_plan: "{{TASK_RESULT.PlanMarketingCampagn}}"
  expected_output: "A detailed marketing strategy outlining key actions and target audiences."
  thinking: |
    Ok. Let's dig dive into this plan. First of all, I notice that
```

You can instantiate a Task from raw YAML data as follows:

```python
import yaml
from LLMTaskKit.core.task import Task

# Load tasks definitions from a YAML file
with open('tasks.yaml', 'r') as file:
    raw_tasks = yaml.safe_load(file)

# Instantiate the first task from the loaded YAML data
task = Task.from_raw(
    raw_tasks[0],
    llm=your_llm_config,  # Optional custom LLM configuration
    output_pydantic=YourOutputModel,  # Optional Pydantic model for validation
    forced_output_format="json"  # Optional format specification
)
```

### TaskExecutors

A **TaskExecutor** is responsible for:
- Preparing the prompt by combining the system prompt and user prompt.
- Injecting context into dynamic placeholders.
- Calling the LLM with the constructed messages.
- Processing and optionally validating the LLM's response using a Pydantic model.

Below is an example of how to execute a task using a TaskExecutor, including loading the task from a YAML file and creating an LLM configuration. Note that behind the scenes, **LiteLLM** is used for the LLM configuration.

```python
import yaml
import logging
from LLMTaskKit.core.task import Task, TaskExecutor
from LLMTaskKit.core.llm_config import LLMConfig


# Create an LLM configuration (LiteLLM is used under the hood)
llm_config = LLMConfig(api_key="your_api_key", model="gpt-4")

# Define a comprehensive context with multiple variables for a complex scenario
context = {
    "customer_id": "CUST-98765",
    "campaign": "Summer Extravaganza",
    "product_details": "A cutting-edge smartphone with advanced AI-powered features",
    "market_trends": "Growing demand for integrated smart technology solutions",
    "budget": "150000",
    "prompt_detail": "Develop a multi-channel marketing strategy integrating both digital and traditional media."
}

# Load task definitions from YAML
with open('tasks.yaml', 'r') as file:
    tasks_definitions = yaml.safe_load(file)

# Instantiate a specific task from the loaded definitions
task = Task.from_raw(tasks_definitions["MarketingStrategyAnalysis"])

# Instantiate the TaskExecutor with the LLM configuration
executor = TaskExecutor(llm_config, verbose=True)

# Execute the task
result = executor.execute(task, context)

logging.info("Task Result:")
logging.info(result)
```

### ChainTaskExecutors

For more complex workflows, **ChainTaskExecutors** allow you to execute multiple tasks sequentially, passing the output of one task as input to the next. This chaining mechanism enables iterative refinement and complex data flows with error handling between steps.

Consider the following example:

```python
import yaml
from LLMTaskKit.core.task import Task
from LLMTaskKit.prompt_chain.task_chain_executor import TaskChainExecutor
from LLMTaskKit.core.llm_config import LLMConfig

# Create an LLM configuration (LiteLLM is used under the hood)
llm_config = LLMConfig(api_key="your_api_key", model="gpt-4")

# Create an initial context with multiple variables for a complex scenario
context = {
    "customer_id": "CUST-98765",
    "campaign": "Summer Extravaganza",
    "product_details": "A cutting-edge smartphone with advanced AI capabilities",
    "market_trends": "Rising consumer interest in sustainable and smart technology",
    "competitor_analysis": "Competitor A targets budget segments, while Competitor B focuses on premium users.",
    "budget": "150000",
    "additional_insights": "Leverage social media trends and influencer partnerships."
}
# Load a chain of task definitions from YAML
with open('chain_tasks.yaml', 'r') as file:
    tasks_chain_definitions = yaml.safe_load(file)

# Instantiate tasks from the YAML definitions
tasks_chain = [Task.from_raw(task_def) for task_def in tasks_chain_definitions]

# Initialize the TaskChainExecutor with the LLM configuration
chain_executor = TaskChainExecutor(llm_config, verbose=True, step_by_step=False)
# Execute the chain of tasks sequentially
final_result = chain_executor.execute(tasks_chain, context)

print("Final Result from Task Chain:")
print(final_result)
```

### Pydantic Integration

LLMTaskKit leverages [Pydantic](https://pydantic-docs.helpmanual.io/) for:
- Defining input and output schemas.
- Validating responses from the LLM.
- Serializing and deserializing task data.

Here’s how you can define and use Pydantic models with tasks:

```python
from pydantic import BaseModel
from typing import List

# Define a Pydantic model for task output validation
class Questions(BaseModel):
    questions: List[str]

# When creating a task, specify the output model:
task_StretchPrompt = Task.from_raw(
    raw_task,
    output_pydantic=Questions,
    forced_output_format="json"
)

# After execution, the TaskExecutor will validate and parse the output:
result = executor.execute(task_StretchPrompt, context)
if isinstance(result, Questions):
    print("Validated Questions:", result.questions)
```

This integration ensures that the responses adhere to the expected schema, minimizing errors in downstream processing.

### Custom `thinking` YAML Tag

The custom `thinking` YAML tag allows you to embed internal reasoning or additional instructions directly within your YAML task definitions. This tag provides a mechanism for dynamic task execution by predefining a "thinking" phase that can guide the LLM’s response construction.

For example, a task definition might include:

```yaml
- name: RolesExtraction
  system_prompt: |
    You are a "Meeting Analyst". Your task is to analyze the transcription to identify and clarify all the participants by assigning each a specific role and assessing their level of influence.
  goal: "Identify and clarify all the participants in meeting transcriptions while determining their respective roles and levels of influence."
  description: "Analyze the transcription to extract the participants and their associated roles."
  transcription: "{{TASK_RESULT.TopicExtraction}}"
  expected_output: "A list of participants with their defined roles."
  thinking: |
    Ok. I think it is important to identify the name of each person. To do this, I will start by mentally outlining everything I can deduce about the participants and their interactions.
```

During execution, if a task contains a `thinking` field, the TaskExecutor pre-fills the assistant’s response with this reasoning, ensuring that the internal thought process is embedded in the workflow. This can be particularly useful when dynamic prompt construction is required.

## Project Examples

LLMTaskKit comes with several example projects to help you get started:

- **Prompt Finetuner:** Located in the [`/example/prompt_finetuner`](./example/prompt_finetuner) directory, this project demonstrates a multi-step workflow for refining prompts. It utilizes chained tasks and Pydantic models to guide the LLM through a series of refinements.
  
- **Meeting Summary:** The [`/example/meeting_summary`](./example/meeting_summary) project provides a practical demonstration of extracting, processing, and summarizing meeting transcriptions using a series of LLM tasks.

These examples serve as practical use cases and are a great starting point for understanding the full capabilities of the library.

## Dependencies and Configuration

LLMTaskKit is designed to work in any standard Python environment. There are no special dependencies or complex configurations required beyond:
- Python 3.7+
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- A standard LLM configuration (e.g., API key and model details)

Simply install the library (and any optional dependencies for your specific LLM) and start integrating tasks into your application.

## Getting Started

1. **Installation:**
   ```bash
   pip install LLMTaskKit
   ```

2. **Define Your Tasks:**
   Create YAML files for your tasks or define them programmatically using the `Task.from_raw` method.

3. **Execute Tasks:**
   Use `TaskExecutor` for standalone tasks or `TaskChainExecutor` for sequential workflows.

4. **Validate Outputs:**
   Integrate Pydantic models to enforce schema validation and ensure data integrity.

Refer to the example projects in the `/example/prompt_finetuner` and `meeting_summary` directories for a comprehensive demonstration of setting up and running workflows with LLMTaskKit.

## License

LLMTaskKit is distributed under the GPL v3.0 and commercial License. See [LICENSE](LICENSE) or [COMMERCIAL-LICENSE](COMMERCIAL-LICENSE.md) for more details.
