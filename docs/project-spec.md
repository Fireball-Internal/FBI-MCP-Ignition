# FBI Ignition MCP Server - Project Specification

## Overview

The FBI Ignition MCP Server is designed to enable AI agents to safely and effectively develop, interact with, and validate Inductive Automation's Ignition SCADA systems. It establishes a "Spec-Driven Development" model by combining two powerful paradigms into a single unified MCP toolset:

1. **Execution Tools (Caldera MCP)**
2. **Engineering Specifications (WhiskeyHouse / `ignition-lint`)**

## Component Details

### 1. Caldera MCP (The Execution Tool)
Provides the AI with active connectivity to the Ignition environment.
- **Capabilities:**
  - Connect to the live gateway.
  - Read and write tags.
  - Pull Perspective `view.json` files.
  - Execute or test Jython scripts.
- **Purpose:** Allows the AI to iteratively build screens, query states, and modify active configurations.

### 2. WhiskeyHouse (The Engineering Spec Sheet / `ignition-lint`)
Provides strict rules, static analysis, and quality assurance to mathematically prove the correctness of the AI's generated work before deployment.
- **Capabilities:**
  - **Perspective JSON Schemas:** Validates generated or modified UI components against production-tested, empirically derived schemas to prevent malformed properties (e.g., injecting invalid flex containers or erroneous CSS classes).
  - **Jython Syntax Catching:** Statically analyzes Jython 2.7 code to catch syntax errors, fragile component traversals (e.g., `getSibling()`), and deprecated API calls prior to runtime.
  - **Expression Binding Validation:** Verifies expression bindings to prevent excessive polling (e.g., inefficient `now()` intervals) and to ensure valid tag references.

## The Spec-Driven Development Workflow

By unifying both components, the development lifecycle guarantees safe AI-assisted engineering:
1. **Creation:** The AI uses *Caldera* functionalities to construct screens and scripts.
2. **Validation:** The AI is forced to pass its code through *WhiskeyHouse* linting and schema validation.
3. **Deployment:** Only empirically proven, valid changes are applied, eliminating hallucinations and runtime exceptions that typically result from unconstrained LLM generation in Ignition.
