# crow-client

A client for interacting with endpoints of the FutureHouse crow service.

## Installation

```bash
uv pip install crow-client
```

## Usage

The CrowClient provides simple functions to deploy and monitor your crow.

In the case of environments the deployment looks like this

```python
from pathlib import Path
from crow_client import CrowClient
from crow_client.models import CrowDeploymentConfig

client = CrowClient()

crow = CrowDeploymentConfig(
    path=Path("../envs/dummy_env"),
    environment="dummy_env.env.DummyEnv",
    requires_aviary_internal=False,
    environment_variables={"SAMPLE_ENV_VAR": "sample_val"},
    agent="ldp.agent.SimpleAgent",
)

client.create_crow(crow)

# checks the status
client.get_build_status()
```

For functional environments we don't need to pass the file path and can pass the environment builder instead

```python
from aviary.core import fenv
import numpy as np


def function_to_use_here(inpste: str):
    a = np.array(np.asmatrix("1 2; 3 4"))
    return inpste


@fenv.start()
def my_env(topic: str):
    """
    Here is the doc string describing the task.
    """
    a = np.array(np.asmatrix("1 2; 3 4"))
    return f"Write a sad story about {topic}", {"chosen_topic": topic}


@my_env.tool()
def print_story(story: str, state) -> None:
    """Print the story and complete the task"""
    print(story)
    print(function_to_use_here(story))
    state.reward = 1
    state.done = True


from crow_client import CrowClient
from crow_client.models import CrowDeploymentConfig, Stage
from crow_client.clients.rest_client import generate_requirements

client = CrowClient(stage=Stage.LOCAL)

crow = CrowDeploymentConfig(
    functional_environment=my_env,
    environment="my_env",
    requires_aviary_internal=False,
    environment_variables={"SAMPLE_ENV_VAR": "sample_val"},
    agent="ldp.agent.SimpleAgent",
    requirements=generate_requirements(my_env, globals()),
)

client.create_crow(crow)
```

This client also provides functions that let you send tasks to an existing crow:

```python
from crow_client import CrowJob

client = CrowClient()

job_data = {"name": "your-job-name", "query": "your task"}
client.create_job(job_data)

# checks the status
client.get_job()
```

The CrowJobClient provides an interface for managing environment states and agent interactions in the FutureHouse crow service.

```python
from crow_client import CrowJobClient
from crow_client.models.app import Stage

client = CrowJobClient(
    environment="your_environment_name",
    agent="your_agent_id",
    auth_token="your_auth_token",
    base_uri=Stage.DEV,
    trajectory_id=None,
)
```
