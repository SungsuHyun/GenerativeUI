# MCP Servers Guide
Generated on: 2025-12-11 14:41:15

## Connection Status Summary

**Connected Servers**: 1/1

| Server ID | Status | Type |
|-----------|--------|------|
| sequentialthinking | Connected | External |

## Custom MCP Servers

No custom MCP servers found.

## External MCP Servers

### sequentialthinking
**Command**: `npm`
**Args**: `exec --yes --package @modelcontextprotocol/server-sequential-thinking -- mcp-server-sequential-thinking --stdio`
**Disabled**: False
**Status**: Connected

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| sequentialthinking | A detailed tool for dynamic and reflective problem-solving through thoughts.<br>This tool helps analyze problems through a flexible thinking process that can adapt and evolve.<br>Each thought can build on, question, or revise previous insights as understanding deepens.<br><br>When to use this tool:<br>- Breaking down complex problems into steps<br>- Planning and design with room for revision<br>- Analysis that might need course correction<br>- Problems where the full scope might not be clear initially<br>- Problems that require a multi-step solution<br>- Tasks that need to maintain context over multiple steps<br>- Situations where irrelevant information needs to be filtered out<br><br>Key features:<br>- You can adjust total_thoughts up or down as you progress<br>- You can question or revise previous thoughts<br>- You can add more thoughts even after reaching what seemed like the end<br>- You can express uncertainty and explore alternative approaches<br>- Not every thought needs to build linearly - you can branch or backtrack<br>- Generates a solution hypothesis<br>- Verifies the hypothesis based on the Chain of Thought steps<br>- Repeats the process until satisfied<br>- Provides a correct answer<br><br>Parameters explained:<br>- thought: Your current thinking step, which can include:<br>  * Regular analytical steps<br>  * Revisions of previous thoughts<br>  * Questions about previous decisions<br>  * Realizations about needing more analysis<br>  * Changes in approach<br>  * Hypothesis generation<br>  * Hypothesis verification<br>- nextThoughtNeeded: True if you need more thinking, even if at what seemed like the end<br>- thoughtNumber: Current number in sequence (can go beyond initial total if needed)<br>- totalThoughts: Current estimate of thoughts needed (can be adjusted up/down)<br>- isRevision: A boolean indicating if this thought revises previous thinking<br>- revisesThought: If is_revision is true, which thought number is being reconsidered<br>- branchFromThought: If branching, which thought number is the branching point<br>- branchId: Identifier for the current branch (if any)<br>- needsMoreThoughts: If reaching end but realizing more thoughts needed<br><br>You should:<br>1. Start with an initial estimate of needed thoughts, but be ready to adjust<br>2. Feel free to question or revise previous thoughts<br>3. Don't hesitate to add more thoughts if needed, even at the "end"<br>4. Express uncertainty when present<br>5. Mark thoughts that revise previous thinking or branch into new paths<br>6. Ignore information that is irrelevant to the current step<br>7. Generate a solution hypothesis when appropriate<br>8. Verify the hypothesis based on the Chain of Thought steps<br>9. Repeat the process until satisfied with the solution<br>10. Provide a single, ideally correct answer as the final output<br>11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached | - **thought*** (string): Your current thinking step<br>- **nextThoughtNeeded*** (boolean): Whether another thought step is needed<br>- **thoughtNumber*** (integer): Current thought number (numeric value, e.g., 1, 2, 3)<br>- **totalThoughts*** (integer): Estimated total thoughts needed (numeric value, e.g., 5, 10)<br>- **isRevision** (boolean): Whether this revises previous thinking<br>- **revisesThought** (integer): Which thought is being reconsidered<br>- **branchFromThought** (integer): Branching point thought number<br>- **branchId** (string): Branch identifier<br>- **needsMoreThoughts** (boolean): If more thoughts are needed |

### Detailed Descriptions

#### sequentialthinking

A detailed tool for dynamic and reflective problem-solving through thoughts.
This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use this tool:
- Breaking down complex problems into steps
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope might not be clear initially
- Problems that require a multi-step solution
- Tasks that need to maintain context over multiple steps
- Situations where irrelevant information needs to be filtered out

Key features:
- You can adjust total_thoughts up or down as you progress
- You can question or revise previous thoughts
- You can add more thoughts even after reaching what seemed like the end
- You can express uncertainty and explore alternative approaches
- Not every thought needs to build linearly - you can branch or backtrack
- Generates a solution hypothesis
- Verifies the hypothesis based on the Chain of Thought steps
- Repeats the process until satisfied
- Provides a correct answer

Parameters explained:
- thought: Your current thinking step, which can include:
  * Regular analytical steps
  * Revisions of previous thoughts
  * Questions about previous decisions
  * Realizations about needing more analysis
  * Changes in approach
  * Hypothesis generation
  * Hypothesis verification
- nextThoughtNeeded: True if you need more thinking, even if at what seemed like the end
- thoughtNumber: Current number in sequence (can go beyond initial total if needed)
- totalThoughts: Current estimate of thoughts needed (can be adjusted up/down)
- isRevision: A boolean indicating if this thought revises previous thinking
- revisesThought: If is_revision is true, which thought number is being reconsidered
- branchFromThought: If branching, which thought number is the branching point
- branchId: Identifier for the current branch (if any)
- needsMoreThoughts: If reaching end but realizing more thoughts needed

You should:
1. Start with an initial estimate of needed thoughts, but be ready to adjust
2. Feel free to question or revise previous thoughts
3. Don't hesitate to add more thoughts if needed, even at the "end"
4. Express uncertainty when present
5. Mark thoughts that revise previous thinking or branch into new paths
6. Ignore information that is irrelevant to the current step
7. Generate a solution hypothesis when appropriate
8. Verify the hypothesis based on the Chain of Thought steps
9. Repeat the process until satisfied with the solution
10. Provide a single, ideally correct answer as the final output
11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached

**Parameters:**

- **thought** (required)
  - Type: `string`
  - Description: Your current thinking step

- **nextThoughtNeeded** (required)
  - Type: `boolean`
  - Description: Whether another thought step is needed

- **thoughtNumber** (required)
  - Type: `integer`
  - Description: Current thought number (numeric value, e.g., 1, 2, 3)

- **totalThoughts** (required)
  - Type: `integer`
  - Description: Estimated total thoughts needed (numeric value, e.g., 5, 10)

- **isRevision**
  - Type: `boolean`
  - Description: Whether this revises previous thinking

- **revisesThought**
  - Type: `integer`
  - Description: Which thought is being reconsidered

- **branchFromThought**
  - Type: `integer`
  - Description: Branching point thought number

- **branchId**
  - Type: `string`
  - Description: Branch identifier

- **needsMoreThoughts**
  - Type: `boolean`
  - Description: If more thoughts are needed

---

## All Available Tools Summary

### sequentialthinking

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| sequentialthinking | A detailed tool for dynamic and reflective problem-solving through thoughts.<br>This tool helps analyze problems through a flexible thinking process that can adapt and evolve.<br>Each thought can build on, question, or revise previous insights as understanding deepens.<br><br>When to use this tool:<br>- Breaking down complex problems into steps<br>- Planning and design with room for revision<br>- Analysis that might need course correction<br>- Problems where the full scope might not be clear initially<br>- Problems that require a multi-step solution<br>- Tasks that need to maintain context over multiple steps<br>- Situations where irrelevant information needs to be filtered out<br><br>Key features:<br>- You can adjust total_thoughts up or down as you progress<br>- You can question or revise previous thoughts<br>- You can add more thoughts even after reaching what seemed like the end<br>- You can express uncertainty and explore alternative approaches<br>- Not every thought needs to build linearly - you can branch or backtrack<br>- Generates a solution hypothesis<br>- Verifies the hypothesis based on the Chain of Thought steps<br>- Repeats the process until satisfied<br>- Provides a correct answer<br><br>Parameters explained:<br>- thought: Your current thinking step, which can include:<br>  * Regular analytical steps<br>  * Revisions of previous thoughts<br>  * Questions about previous decisions<br>  * Realizations about needing more analysis<br>  * Changes in approach<br>  * Hypothesis generation<br>  * Hypothesis verification<br>- nextThoughtNeeded: True if you need more thinking, even if at what seemed like the end<br>- thoughtNumber: Current number in sequence (can go beyond initial total if needed)<br>- totalThoughts: Current estimate of thoughts needed (can be adjusted up/down)<br>- isRevision: A boolean indicating if this thought revises previous thinking<br>- revisesThought: If is_revision is true, which thought number is being reconsidered<br>- branchFromThought: If branching, which thought number is the branching point<br>- branchId: Identifier for the current branch (if any)<br>- needsMoreThoughts: If reaching end but realizing more thoughts needed<br><br>You should:<br>1. Start with an initial estimate of needed thoughts, but be ready to adjust<br>2. Feel free to question or revise previous thoughts<br>3. Don't hesitate to add more thoughts if needed, even at the "end"<br>4. Express uncertainty when present<br>5. Mark thoughts that revise previous thinking or branch into new paths<br>6. Ignore information that is irrelevant to the current step<br>7. Generate a solution hypothesis when appropriate<br>8. Verify the hypothesis based on the Chain of Thought steps<br>9. Repeat the process until satisfied with the solution<br>10. Provide a single, ideally correct answer as the final output<br>11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached | - **thought*** (string): Your current thinking step<br>- **nextThoughtNeeded*** (boolean): Whether another thought step is needed<br>- **thoughtNumber*** (integer): Current thought number (numeric value, e.g., 1, 2, 3)<br>- **totalThoughts*** (integer): Estimated total thoughts needed (numeric value, e.g., 5, 10)<br>- **isRevision** (boolean): Whether this revises previous thinking<br>- **revisesThought** (integer): Which thought is being reconsidered<br>- **branchFromThought** (integer): Branching point thought number<br>- **branchId** (string): Branch identifier<br>- **needsMoreThoughts** (boolean): If more thoughts are needed |

### Detailed Descriptions

#### sequentialthinking

A detailed tool for dynamic and reflective problem-solving through thoughts.
This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use this tool:
- Breaking down complex problems into steps
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope might not be clear initially
- Problems that require a multi-step solution
- Tasks that need to maintain context over multiple steps
- Situations where irrelevant information needs to be filtered out

Key features:
- You can adjust total_thoughts up or down as you progress
- You can question or revise previous thoughts
- You can add more thoughts even after reaching what seemed like the end
- You can express uncertainty and explore alternative approaches
- Not every thought needs to build linearly - you can branch or backtrack
- Generates a solution hypothesis
- Verifies the hypothesis based on the Chain of Thought steps
- Repeats the process until satisfied
- Provides a correct answer

Parameters explained:
- thought: Your current thinking step, which can include:
  * Regular analytical steps
  * Revisions of previous thoughts
  * Questions about previous decisions
  * Realizations about needing more analysis
  * Changes in approach
  * Hypothesis generation
  * Hypothesis verification
- nextThoughtNeeded: True if you need more thinking, even if at what seemed like the end
- thoughtNumber: Current number in sequence (can go beyond initial total if needed)
- totalThoughts: Current estimate of thoughts needed (can be adjusted up/down)
- isRevision: A boolean indicating if this thought revises previous thinking
- revisesThought: If is_revision is true, which thought number is being reconsidered
- branchFromThought: If branching, which thought number is the branching point
- branchId: Identifier for the current branch (if any)
- needsMoreThoughts: If reaching end but realizing more thoughts needed

You should:
1. Start with an initial estimate of needed thoughts, but be ready to adjust
2. Feel free to question or revise previous thoughts
3. Don't hesitate to add more thoughts if needed, even at the "end"
4. Express uncertainty when present
5. Mark thoughts that revise previous thinking or branch into new paths
6. Ignore information that is irrelevant to the current step
7. Generate a solution hypothesis when appropriate
8. Verify the hypothesis based on the Chain of Thought steps
9. Repeat the process until satisfied with the solution
10. Provide a single, ideally correct answer as the final output
11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached

**Parameters:**

- **thought** (required)
  - Type: `string`
  - Description: Your current thinking step

- **nextThoughtNeeded** (required)
  - Type: `boolean`
  - Description: Whether another thought step is needed

- **thoughtNumber** (required)
  - Type: `integer`
  - Description: Current thought number (numeric value, e.g., 1, 2, 3)

- **totalThoughts** (required)
  - Type: `integer`
  - Description: Estimated total thoughts needed (numeric value, e.g., 5, 10)

- **isRevision**
  - Type: `boolean`
  - Description: Whether this revises previous thinking

- **revisesThought**
  - Type: `integer`
  - Description: Which thought is being reconsidered

- **branchFromThought**
  - Type: `integer`
  - Description: Branching point thought number

- **branchId**
  - Type: `string`
  - Description: Branch identifier

- **needsMoreThoughts**
  - Type: `boolean`
  - Description: If more thoughts are needed

---

**Total Available Tools**: 1