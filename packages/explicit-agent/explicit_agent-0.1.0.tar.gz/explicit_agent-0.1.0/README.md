# Hi, this is Explicit Agent

A minimalist, transparent framework for building AI agents with full user control and zero abstraction layers - yes ZERO!

![Explicit Agent](assets/explicit.png)

## Table of Contents
- [Why Explicit Agent?](#why-explicit-agent)
- [Get Started](#get-started)
  - [Installation](#installation)
  - [How to use it](#how-to-use-it)
- [Core Concepts](#core-concepts)
  - [Agent State](#agent-state)
  - [Tool Types](#tool-types)


## Why Explicit Agent?

Most agentic frameworks are overengineered with layers of abstraction that obscure what's actually happening. Explicit Agent cuts through the BS to provide:

- **Complete transparency**: No hidden prompts or "magic" under the hood
- **Full control**: You define exactly how your agent behaves
- **Minimal infrastructure**: Only the essentials needed to run capable AI agents
- **Simplicity first**: Ability to build complex behaviors from simple, understandable components

This framework provides the minimum viable infrastructure for running AI agents while maintaining full visibility into their operation.

## Get Started

### Installation

```bash
# Clone the repository
git clone https://github.com/gabriansa/explicit-agent.git
cd explicit-agent

# Install the package
pip install e .
```

### How to use it



## Core Concepts
The Explicit Agent Framework is built around a few simple concepts that work together to create powerful, transparent AI agents.

![Explicit Agent Framework](assets/framework.png)



### Agent State

The agent maintains a state that persists across tool calls and interactions. This allows tools to share information and build on previous results. The state can be initialized when creating the agent and is updated by "stateful" tools.

### Tool Types

The framework supports four types of tools:

- **StatelessTool**: Standard tools that execute a function and return a result. These tools don't have access to or modify the agent's state.
  
- **StatefulTool**: Tools that receive the current state and return a result. These are perfect for tools that need to read from or write to the agent's persistent memory.
  
- **StopStatelessTool**: Special stateless tools that signal when the agent should stop execution. They return a result and prevent further tool calls.

- **StopStatefulTool**: Special stateful tools that signal when the agent should stop execution. They receive the final state, return a result, and prevent further tool calls.

### Execution Flow

1. The agent receives a prompt from the user
2. The agent generates tool calls based on the prompt and system instructions
3. The tools are executed, potentially updating the agent's state
4. The results are fed back to the agent
5. This continues until a Stop tool is called or the budget is exhausted

## Examples

For more advanced usage and detailed documentation, see the examples directory.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
