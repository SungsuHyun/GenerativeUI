# MCP Servers Guide
Generated on: 2025-07-22 15:06:24

## Connection Status Summary

**Connected Servers**: 6/6

| Server ID | Status | Type |
|-----------|--------|------|
| sequentialthinking | Connected | External |
| google-maps | Connected | External |
| time | Connected | External |
| brave-search | Connected | External |
| memory | Connected | External |
| weather | Connected | External |

## Local MCP Servers

No local MCP servers found.

## External MCP Servers

### sequentialthinking
**Command**: `docker`
**Args**: `run --rm -i mcp/sequentialthinking`
**Disabled**: False
**Status**: Connected

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| sequentialthinking | A detailed tool for dynamic and reflective problem-solving through thoughts.<br>This tool helps analyze problems through a flexible thinking process that can adapt and evolve.<br>Each thought can build on, question, or revise previous insights as understanding deepens.<br><br>When to use this tool:<br>- Breaking down complex problems into steps<br>- Planning and design with room for revision<br>- Analysis that might need course correction<br>- Problems where the full scope might not be clear initially<br>- Problems that require a multi-step solution<br>- Tasks that need to maintain context over multiple steps<br>- Situations where irrelevant information needs to be filtered out<br><br>Key features:<br>- You can adjust total_thoughts up or down as you progress<br>- You can question or revise previous thoughts<br>- You can add more thoughts even after reaching what seemed like the end<br>- You can express uncertainty and explore alternative approaches<br>- Not every thought needs to build linearly - you can branch or backtrack<br>- Generates a solution hypothesis<br>- Verifies the hypothesis based on the Chain of Thought steps<br>- Repeats the process until satisfied<br>- Provides a correct answer<br><br>Parameters explained:<br>- thought: Your current thinking step, which can include:<br>* Regular analytical steps<br>* Revisions of previous thoughts<br>* Questions about previous decisions<br>* Realizations about needing more analysis<br>* Changes in approach<br>* Hypothesis generation<br>* Hypothesis verification<br>- next_thought_needed: True if you need more thinking, even if at what seemed like the end<br>- thought_number: Current number in sequence (can go beyond initial total if needed)<br>- total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)<br>- is_revision: A boolean indicating if this thought revises previous thinking<br>- revises_thought: If is_revision is true, which thought number is being reconsidered<br>- branch_from_thought: If branching, which thought number is the branching point<br>- branch_id: Identifier for the current branch (if any)<br>- needs_more_thoughts: If reaching end but realizing more thoughts needed<br><br>You should:<br>1. Start with an initial estimate of needed thoughts, but be ready to adjust<br>2. Feel free to question or revise previous thoughts<br>3. Don't hesitate to add more thoughts if needed, even at the "end"<br>4. Express uncertainty when present<br>5. Mark thoughts that revise previous thinking or branch into new paths<br>6. Ignore information that is irrelevant to the current step<br>7. Generate a solution hypothesis when appropriate<br>8. Verify the hypothesis based on the Chain of Thought steps<br>9. Repeat the process until satisfied with the solution<br>10. Provide a single, ideally correct answer as the final output<br>11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached | - **thought*** (string): Your current thinking step<br>- **nextThoughtNeeded*** (boolean): Whether another thought step is needed<br>- **thoughtNumber*** (integer): Current thought number<br>- **totalThoughts*** (integer): Estimated total thoughts needed<br>- **isRevision** (boolean): Whether this revises previous thinking<br>- **revisesThought** (integer): Which thought is being reconsidered<br>- **branchFromThought** (integer): Branching point thought number<br>- **branchId** (string): Branch identifier<br>- **needsMoreThoughts** (boolean): If more thoughts are needed |

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
- next_thought_needed: True if you need more thinking, even if at what seemed like the end
- thought_number: Current number in sequence (can go beyond initial total if needed)
- total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
- is_revision: A boolean indicating if this thought revises previous thinking
- revises_thought: If is_revision is true, which thought number is being reconsidered
- branch_from_thought: If branching, which thought number is the branching point
- branch_id: Identifier for the current branch (if any)
- needs_more_thoughts: If reaching end but realizing more thoughts needed

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
  - Description: Current thought number

- **totalThoughts** (required)
  - Type: `integer`
  - Description: Estimated total thoughts needed

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

### google-maps
**Command**: `docker`
**Args**: `run -i --rm -e GOOGLE_MAPS_API_KEY mcp/google-maps mcp/google-maps`
**Disabled**: False
**Status**: Connected

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| maps_geocode | Convert an address into geographic coordinates | - **address*** (string): The address to geocode |
| maps_reverse_geocode | Convert coordinates into an address | - **latitude*** (number): Latitude coordinate<br>- **longitude*** (number): Longitude coordinate |
| maps_search_places | Search for places using Google Places API | - **query*** (string): Search query<br>- **location** (object): Optional center point for the search<br>- **radius** (number): Search radius in meters (max 50000) |
| maps_place_details | Get detailed information about a specific place | - **place_id*** (string): The place ID to get details for |
| maps_distance_matrix | Calculate travel distance and time for multiple origins and destinations | - **origins*** (array): Array of origin addresses or coordinates<br>- **destinations*** (array): Array of destination addresses or coordinates<br>- **mode** (string): Travel mode (driving, walking, bicycling, transit) |
| maps_elevation | Get elevation data for locations on the earth | - **locations*** (array): Array of locations to get elevation for |
| maps_directions | Get directions between two points | - **origin*** (string): Starting point address or coordinates<br>- **destination*** (string): Ending point address or coordinates<br>- **mode** (string): Travel mode (driving, walking, bicycling, transit) |

### Detailed Descriptions

#### maps_geocode

Convert an address into geographic coordinates

**Parameters:**

- **address** (required)
  - Type: `string`
  - Description: The address to geocode

---

#### maps_reverse_geocode

Convert coordinates into an address

**Parameters:**

- **latitude** (required)
  - Type: `number`
  - Description: Latitude coordinate

- **longitude** (required)
  - Type: `number`
  - Description: Longitude coordinate

---

#### maps_search_places

Search for places using Google Places API

**Parameters:**

- **query** (required)
  - Type: `string`
  - Description: Search query

- **location**
  - Type: `object`
  - Description: Optional center point for the search

- **radius**
  - Type: `number`
  - Description: Search radius in meters (max 50000)

---

#### maps_place_details

Get detailed information about a specific place

**Parameters:**

- **place_id** (required)
  - Type: `string`
  - Description: The place ID to get details for

---

#### maps_distance_matrix

Calculate travel distance and time for multiple origins and destinations

**Parameters:**

- **origins** (required)
  - Type: `array`
  - Description: Array of origin addresses or coordinates

- **destinations** (required)
  - Type: `array`
  - Description: Array of destination addresses or coordinates

- **mode**
  - Type: `string`
  - Description: Travel mode (driving, walking, bicycling, transit)

---

#### maps_elevation

Get elevation data for locations on the earth

**Parameters:**

- **locations** (required)
  - Type: `array`
  - Description: Array of locations to get elevation for

---

#### maps_directions

Get directions between two points

**Parameters:**

- **origin** (required)
  - Type: `string`
  - Description: Starting point address or coordinates

- **destination** (required)
  - Type: `string`
  - Description: Ending point address or coordinates

- **mode**
  - Type: `string`
  - Description: Travel mode (driving, walking, bicycling, transit)

---

### time
**Command**: `docker`
**Args**: `run --rm -i mcp/time`
**Disabled**: False
**Status**: Connected

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| get_current_time | Get current time in a specific timezones | - **timezone*** (string): IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Etc/UTC' as local timezone if no timezone provided by the user. |
| convert_time | Convert time between timezones | - **source_timezone*** (string): Source IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Etc/UTC' as local timezone if no source timezone provided by the user.<br>- **time*** (string): Time to convert in 24-hour format (HH:MM)<br>- **target_timezone*** (string): Target IANA timezone name (e.g., 'Asia/Tokyo', 'America/San_Francisco'). Use 'Etc/UTC' as local timezone if no target timezone provided by the user. |

### Detailed Descriptions

#### get_current_time

Get current time in a specific timezones

**Parameters:**

- **timezone** (required)
  - Type: `string`
  - Description: IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Etc/UTC' as local timezone if no timezone provided by the user.

---

#### convert_time

Convert time between timezones

**Parameters:**

- **source_timezone** (required)
  - Type: `string`
  - Description: Source IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Etc/UTC' as local timezone if no source timezone provided by the user.

- **time** (required)
  - Type: `string`
  - Description: Time to convert in 24-hour format (HH:MM)

- **target_timezone** (required)
  - Type: `string`
  - Description: Target IANA timezone name (e.g., 'Asia/Tokyo', 'America/San_Francisco'). Use 'Etc/UTC' as local timezone if no target timezone provided by the user.

---

### brave-search
**Command**: `docker`
**Args**: `run -i --rm -e BRAVE_API_KEY mcp/brave-search mcp/brave-search`
**Disabled**: False
**Status**: Connected

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| brave_web_search | Performs a web search using the Brave Search API, ideal for general queries, news, articles, and online content. Use this for broad information gathering, recent events, or when you need diverse web sources. Supports pagination, content filtering, and freshness controls. Maximum 20 results per request, with offset for pagination.  | - **query*** (string): Search query (max 400 chars, 50 words)<br>- **count** (number): Number of results (1-20, default 10)<br>- **offset** (number): Pagination offset (max 9, default 0) |
| brave_local_search | Searches for local businesses and places using Brave's Local Search API. Best for queries related to physical locations, businesses, restaurants, services, etc. Returns detailed information including:<br>- Business names and addresses<br>- Ratings and review counts<br>- Phone numbers and opening hours<br>Use this when the query implies 'near me' or mentions specific locations. Automatically falls back to web search if no local results are found. | - **query*** (string): Local search query (e.g. 'pizza near Central Park')<br>- **count** (number): Number of results (1-20, default 5) |

### Detailed Descriptions

#### brave_web_search

Performs a web search using the Brave Search API, ideal for general queries, news, articles, and online content. Use this for broad information gathering, recent events, or when you need diverse web sources. Supports pagination, content filtering, and freshness controls. Maximum 20 results per request, with offset for pagination. 

**Parameters:**

- **query** (required)
  - Type: `string`
  - Description: Search query (max 400 chars, 50 words)

- **count**
  - Type: `number`
  - Description: Number of results (1-20, default 10)

- **offset**
  - Type: `number`
  - Description: Pagination offset (max 9, default 0)

---

#### brave_local_search

Searches for local businesses and places using Brave's Local Search API. Best for queries related to physical locations, businesses, restaurants, services, etc. Returns detailed information including:
- Business names and addresses
- Ratings and review counts
- Phone numbers and opening hours
Use this when the query implies 'near me' or mentions specific locations. Automatically falls back to web search if no local results are found.

**Parameters:**

- **query** (required)
  - Type: `string`
  - Description: Local search query (e.g. 'pizza near Central Park')

- **count**
  - Type: `number`
  - Description: Number of results (1-20, default 5)

---

### memory
**Command**: `docker`
**Args**: `run -i -v claude-memory:/app/dist --rm mcp/memory mcp/memory`
**Disabled**: False
**Status**: Connected

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| create_entities | Create multiple new entities in the knowledge graph | - **entities*** (array):  |
| create_relations | Create multiple new relations between entities in the knowledge graph. Relations should be in active voice | - **relations*** (array):  |
| add_observations | Add new observations to existing entities in the knowledge graph | - **observations*** (array):  |
| delete_entities | Delete multiple entities and their associated relations from the knowledge graph | - **entityNames*** (array): An array of entity names to delete |
| delete_observations | Delete specific observations from entities in the knowledge graph | - **deletions*** (array):  |
| delete_relations | Delete multiple relations from the knowledge graph | - **relations*** (array): An array of relations to delete |
| read_graph | Read the entire knowledge graph | None |
| search_nodes | Search for nodes in the knowledge graph based on a query | - **query*** (string): The search query to match against entity names, types, and observation content |
| open_nodes | Open specific nodes in the knowledge graph by their names | - **names*** (array): An array of entity names to retrieve |

### Detailed Descriptions

#### create_entities

Create multiple new entities in the knowledge graph

**Parameters:**

- **entities** (required)
  - Type: `array`
  - Description: 

---

#### create_relations

Create multiple new relations between entities in the knowledge graph. Relations should be in active voice

**Parameters:**

- **relations** (required)
  - Type: `array`
  - Description: 

---

#### add_observations

Add new observations to existing entities in the knowledge graph

**Parameters:**

- **observations** (required)
  - Type: `array`
  - Description: 

---

#### delete_entities

Delete multiple entities and their associated relations from the knowledge graph

**Parameters:**

- **entityNames** (required)
  - Type: `array`
  - Description: An array of entity names to delete

---

#### delete_observations

Delete specific observations from entities in the knowledge graph

**Parameters:**

- **deletions** (required)
  - Type: `array`
  - Description: 

---

#### delete_relations

Delete multiple relations from the knowledge graph

**Parameters:**

- **relations** (required)
  - Type: `array`
  - Description: An array of relations to delete

---

#### read_graph

Read the entire knowledge graph

---

#### search_nodes

Search for nodes in the knowledge graph based on a query

**Parameters:**

- **query** (required)
  - Type: `string`
  - Description: The search query to match against entity names, types, and observation content

---

#### open_nodes

Open specific nodes in the knowledge graph by their names

**Parameters:**

- **names** (required)
  - Type: `array`
  - Description: An array of entity names to retrieve

---

### weather
**Command**: `npx`
**Args**: `-y @timlukahorstmann/mcp-weather`
**Disabled**: False
**Status**: Connected

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| weather-get_hourly | Get hourly weather forecast for the next 12 hours | - **location*** (string): The city or location for which to retrieve the weather forecast.<br>- **units** (string): Temperature unit system (metric for Celsius, imperial for Fahrenheit). Default is metric. |
| weather-get_daily | Get daily weather forecast for up to 15 days | - **location*** (string): The city or location for which to retrieve the weather forecast.<br>- **days** (number): Number of days to forecast (1, 5, 10, or 15). Default is 5.<br>- **units** (string): Temperature unit system (metric for Celsius, imperial for Fahrenheit). Default is metric. |

### Detailed Descriptions

#### weather-get_hourly

Get hourly weather forecast for the next 12 hours

**Parameters:**

- **location** (required)
  - Type: `string`
  - Description: The city or location for which to retrieve the weather forecast.

- **units**
  - Type: `string`
  - Description: Temperature unit system (metric for Celsius, imperial for Fahrenheit). Default is metric.

---

#### weather-get_daily

Get daily weather forecast for up to 15 days

**Parameters:**

- **location** (required)
  - Type: `string`
  - Description: The city or location for which to retrieve the weather forecast.

- **days**
  - Type: `number`
  - Description: Number of days to forecast (1, 5, 10, or 15). Default is 5.

- **units**
  - Type: `string`
  - Description: Temperature unit system (metric for Celsius, imperial for Fahrenheit). Default is metric.

---

## All Available Tools Summary

### sequentialthinking

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| sequentialthinking | A detailed tool for dynamic and reflective problem-solving through thoughts.<br>This tool helps analyze problems through a flexible thinking process that can adapt and evolve.<br>Each thought can build on, question, or revise previous insights as understanding deepens.<br><br>When to use this tool:<br>- Breaking down complex problems into steps<br>- Planning and design with room for revision<br>- Analysis that might need course correction<br>- Problems where the full scope might not be clear initially<br>- Problems that require a multi-step solution<br>- Tasks that need to maintain context over multiple steps<br>- Situations where irrelevant information needs to be filtered out<br><br>Key features:<br>- You can adjust total_thoughts up or down as you progress<br>- You can question or revise previous thoughts<br>- You can add more thoughts even after reaching what seemed like the end<br>- You can express uncertainty and explore alternative approaches<br>- Not every thought needs to build linearly - you can branch or backtrack<br>- Generates a solution hypothesis<br>- Verifies the hypothesis based on the Chain of Thought steps<br>- Repeats the process until satisfied<br>- Provides a correct answer<br><br>Parameters explained:<br>- thought: Your current thinking step, which can include:<br>* Regular analytical steps<br>* Revisions of previous thoughts<br>* Questions about previous decisions<br>* Realizations about needing more analysis<br>* Changes in approach<br>* Hypothesis generation<br>* Hypothesis verification<br>- next_thought_needed: True if you need more thinking, even if at what seemed like the end<br>- thought_number: Current number in sequence (can go beyond initial total if needed)<br>- total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)<br>- is_revision: A boolean indicating if this thought revises previous thinking<br>- revises_thought: If is_revision is true, which thought number is being reconsidered<br>- branch_from_thought: If branching, which thought number is the branching point<br>- branch_id: Identifier for the current branch (if any)<br>- needs_more_thoughts: If reaching end but realizing more thoughts needed<br><br>You should:<br>1. Start with an initial estimate of needed thoughts, but be ready to adjust<br>2. Feel free to question or revise previous thoughts<br>3. Don't hesitate to add more thoughts if needed, even at the "end"<br>4. Express uncertainty when present<br>5. Mark thoughts that revise previous thinking or branch into new paths<br>6. Ignore information that is irrelevant to the current step<br>7. Generate a solution hypothesis when appropriate<br>8. Verify the hypothesis based on the Chain of Thought steps<br>9. Repeat the process until satisfied with the solution<br>10. Provide a single, ideally correct answer as the final output<br>11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached | - **thought*** (string): Your current thinking step<br>- **nextThoughtNeeded*** (boolean): Whether another thought step is needed<br>- **thoughtNumber*** (integer): Current thought number<br>- **totalThoughts*** (integer): Estimated total thoughts needed<br>- **isRevision** (boolean): Whether this revises previous thinking<br>- **revisesThought** (integer): Which thought is being reconsidered<br>- **branchFromThought** (integer): Branching point thought number<br>- **branchId** (string): Branch identifier<br>- **needsMoreThoughts** (boolean): If more thoughts are needed |

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
- next_thought_needed: True if you need more thinking, even if at what seemed like the end
- thought_number: Current number in sequence (can go beyond initial total if needed)
- total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
- is_revision: A boolean indicating if this thought revises previous thinking
- revises_thought: If is_revision is true, which thought number is being reconsidered
- branch_from_thought: If branching, which thought number is the branching point
- branch_id: Identifier for the current branch (if any)
- needs_more_thoughts: If reaching end but realizing more thoughts needed

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
  - Description: Current thought number

- **totalThoughts** (required)
  - Type: `integer`
  - Description: Estimated total thoughts needed

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

### google-maps

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| maps_geocode | Convert an address into geographic coordinates | - **address*** (string): The address to geocode |
| maps_reverse_geocode | Convert coordinates into an address | - **latitude*** (number): Latitude coordinate<br>- **longitude*** (number): Longitude coordinate |
| maps_search_places | Search for places using Google Places API | - **query*** (string): Search query<br>- **location** (object): Optional center point for the search<br>- **radius** (number): Search radius in meters (max 50000) |
| maps_place_details | Get detailed information about a specific place | - **place_id*** (string): The place ID to get details for |
| maps_distance_matrix | Calculate travel distance and time for multiple origins and destinations | - **origins*** (array): Array of origin addresses or coordinates<br>- **destinations*** (array): Array of destination addresses or coordinates<br>- **mode** (string): Travel mode (driving, walking, bicycling, transit) |
| maps_elevation | Get elevation data for locations on the earth | - **locations*** (array): Array of locations to get elevation for |
| maps_directions | Get directions between two points | - **origin*** (string): Starting point address or coordinates<br>- **destination*** (string): Ending point address or coordinates<br>- **mode** (string): Travel mode (driving, walking, bicycling, transit) |

### Detailed Descriptions

#### maps_geocode

Convert an address into geographic coordinates

**Parameters:**

- **address** (required)
  - Type: `string`
  - Description: The address to geocode

---

#### maps_reverse_geocode

Convert coordinates into an address

**Parameters:**

- **latitude** (required)
  - Type: `number`
  - Description: Latitude coordinate

- **longitude** (required)
  - Type: `number`
  - Description: Longitude coordinate

---

#### maps_search_places

Search for places using Google Places API

**Parameters:**

- **query** (required)
  - Type: `string`
  - Description: Search query

- **location**
  - Type: `object`
  - Description: Optional center point for the search

- **radius**
  - Type: `number`
  - Description: Search radius in meters (max 50000)

---

#### maps_place_details

Get detailed information about a specific place

**Parameters:**

- **place_id** (required)
  - Type: `string`
  - Description: The place ID to get details for

---

#### maps_distance_matrix

Calculate travel distance and time for multiple origins and destinations

**Parameters:**

- **origins** (required)
  - Type: `array`
  - Description: Array of origin addresses or coordinates

- **destinations** (required)
  - Type: `array`
  - Description: Array of destination addresses or coordinates

- **mode**
  - Type: `string`
  - Description: Travel mode (driving, walking, bicycling, transit)

---

#### maps_elevation

Get elevation data for locations on the earth

**Parameters:**

- **locations** (required)
  - Type: `array`
  - Description: Array of locations to get elevation for

---

#### maps_directions

Get directions between two points

**Parameters:**

- **origin** (required)
  - Type: `string`
  - Description: Starting point address or coordinates

- **destination** (required)
  - Type: `string`
  - Description: Ending point address or coordinates

- **mode**
  - Type: `string`
  - Description: Travel mode (driving, walking, bicycling, transit)

---

### time

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| get_current_time | Get current time in a specific timezones | - **timezone*** (string): IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Etc/UTC' as local timezone if no timezone provided by the user. |
| convert_time | Convert time between timezones | - **source_timezone*** (string): Source IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Etc/UTC' as local timezone if no source timezone provided by the user.<br>- **time*** (string): Time to convert in 24-hour format (HH:MM)<br>- **target_timezone*** (string): Target IANA timezone name (e.g., 'Asia/Tokyo', 'America/San_Francisco'). Use 'Etc/UTC' as local timezone if no target timezone provided by the user. |

### Detailed Descriptions

#### get_current_time

Get current time in a specific timezones

**Parameters:**

- **timezone** (required)
  - Type: `string`
  - Description: IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Etc/UTC' as local timezone if no timezone provided by the user.

---

#### convert_time

Convert time between timezones

**Parameters:**

- **source_timezone** (required)
  - Type: `string`
  - Description: Source IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Etc/UTC' as local timezone if no source timezone provided by the user.

- **time** (required)
  - Type: `string`
  - Description: Time to convert in 24-hour format (HH:MM)

- **target_timezone** (required)
  - Type: `string`
  - Description: Target IANA timezone name (e.g., 'Asia/Tokyo', 'America/San_Francisco'). Use 'Etc/UTC' as local timezone if no target timezone provided by the user.

---

### brave-search

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| brave_web_search | Performs a web search using the Brave Search API, ideal for general queries, news, articles, and online content. Use this for broad information gathering, recent events, or when you need diverse web sources. Supports pagination, content filtering, and freshness controls. Maximum 20 results per request, with offset for pagination.  | - **query*** (string): Search query (max 400 chars, 50 words)<br>- **count** (number): Number of results (1-20, default 10)<br>- **offset** (number): Pagination offset (max 9, default 0) |
| brave_local_search | Searches for local businesses and places using Brave's Local Search API. Best for queries related to physical locations, businesses, restaurants, services, etc. Returns detailed information including:<br>- Business names and addresses<br>- Ratings and review counts<br>- Phone numbers and opening hours<br>Use this when the query implies 'near me' or mentions specific locations. Automatically falls back to web search if no local results are found. | - **query*** (string): Local search query (e.g. 'pizza near Central Park')<br>- **count** (number): Number of results (1-20, default 5) |

### Detailed Descriptions

#### brave_web_search

Performs a web search using the Brave Search API, ideal for general queries, news, articles, and online content. Use this for broad information gathering, recent events, or when you need diverse web sources. Supports pagination, content filtering, and freshness controls. Maximum 20 results per request, with offset for pagination. 

**Parameters:**

- **query** (required)
  - Type: `string`
  - Description: Search query (max 400 chars, 50 words)

- **count**
  - Type: `number`
  - Description: Number of results (1-20, default 10)

- **offset**
  - Type: `number`
  - Description: Pagination offset (max 9, default 0)

---

#### brave_local_search

Searches for local businesses and places using Brave's Local Search API. Best for queries related to physical locations, businesses, restaurants, services, etc. Returns detailed information including:
- Business names and addresses
- Ratings and review counts
- Phone numbers and opening hours
Use this when the query implies 'near me' or mentions specific locations. Automatically falls back to web search if no local results are found.

**Parameters:**

- **query** (required)
  - Type: `string`
  - Description: Local search query (e.g. 'pizza near Central Park')

- **count**
  - Type: `number`
  - Description: Number of results (1-20, default 5)

---

### memory

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| create_entities | Create multiple new entities in the knowledge graph | - **entities*** (array):  |
| create_relations | Create multiple new relations between entities in the knowledge graph. Relations should be in active voice | - **relations*** (array):  |
| add_observations | Add new observations to existing entities in the knowledge graph | - **observations*** (array):  |
| delete_entities | Delete multiple entities and their associated relations from the knowledge graph | - **entityNames*** (array): An array of entity names to delete |
| delete_observations | Delete specific observations from entities in the knowledge graph | - **deletions*** (array):  |
| delete_relations | Delete multiple relations from the knowledge graph | - **relations*** (array): An array of relations to delete |
| read_graph | Read the entire knowledge graph | None |
| search_nodes | Search for nodes in the knowledge graph based on a query | - **query*** (string): The search query to match against entity names, types, and observation content |
| open_nodes | Open specific nodes in the knowledge graph by their names | - **names*** (array): An array of entity names to retrieve |

### Detailed Descriptions

#### create_entities

Create multiple new entities in the knowledge graph

**Parameters:**

- **entities** (required)
  - Type: `array`
  - Description: 

---

#### create_relations

Create multiple new relations between entities in the knowledge graph. Relations should be in active voice

**Parameters:**

- **relations** (required)
  - Type: `array`
  - Description: 

---

#### add_observations

Add new observations to existing entities in the knowledge graph

**Parameters:**

- **observations** (required)
  - Type: `array`
  - Description: 

---

#### delete_entities

Delete multiple entities and their associated relations from the knowledge graph

**Parameters:**

- **entityNames** (required)
  - Type: `array`
  - Description: An array of entity names to delete

---

#### delete_observations

Delete specific observations from entities in the knowledge graph

**Parameters:**

- **deletions** (required)
  - Type: `array`
  - Description: 

---

#### delete_relations

Delete multiple relations from the knowledge graph

**Parameters:**

- **relations** (required)
  - Type: `array`
  - Description: An array of relations to delete

---

#### read_graph

Read the entire knowledge graph

---

#### search_nodes

Search for nodes in the knowledge graph based on a query

**Parameters:**

- **query** (required)
  - Type: `string`
  - Description: The search query to match against entity names, types, and observation content

---

#### open_nodes

Open specific nodes in the knowledge graph by their names

**Parameters:**

- **names** (required)
  - Type: `array`
  - Description: An array of entity names to retrieve

---

### weather

### Available Tools

| Function Name | Description | Parameters |
|---------------|-------------|------------|
| weather-get_hourly | Get hourly weather forecast for the next 12 hours | - **location*** (string): The city or location for which to retrieve the weather forecast.<br>- **units** (string): Temperature unit system (metric for Celsius, imperial for Fahrenheit). Default is metric. |
| weather-get_daily | Get daily weather forecast for up to 15 days | - **location*** (string): The city or location for which to retrieve the weather forecast.<br>- **days** (number): Number of days to forecast (1, 5, 10, or 15). Default is 5.<br>- **units** (string): Temperature unit system (metric for Celsius, imperial for Fahrenheit). Default is metric. |

### Detailed Descriptions

#### weather-get_hourly

Get hourly weather forecast for the next 12 hours

**Parameters:**

- **location** (required)
  - Type: `string`
  - Description: The city or location for which to retrieve the weather forecast.

- **units**
  - Type: `string`
  - Description: Temperature unit system (metric for Celsius, imperial for Fahrenheit). Default is metric.

---

#### weather-get_daily

Get daily weather forecast for up to 15 days

**Parameters:**

- **location** (required)
  - Type: `string`
  - Description: The city or location for which to retrieve the weather forecast.

- **days**
  - Type: `number`
  - Description: Number of days to forecast (1, 5, 10, or 15). Default is 5.

- **units**
  - Type: `string`
  - Description: Temperature unit system (metric for Celsius, imperial for Fahrenheit). Default is metric.

---

**Total Available Tools**: 23