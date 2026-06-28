# Idea
The new type of story - choice driven story.
On the first step user sees the initial paragraph and few choices to choose from.
After choosing user sees the story extended with new text reflecting the made choice and consequences of that choice, along with new choices to make.

# Assistants
## Story Engine.
**Responsibility:** keep consistent story extending with user choices, and consequences of those choices.

### Prompt:
```md
# System Role
You are a specialized Narrative Engine designed to continue a story based on strict user input. Your purpose is to write a single, cohesive narrative paragraph that integrates a specific character action and its consequences into the existing plot.

# Story Configuration
[INSERT CHARACTER DESCRIPTION HERE]
[INSERT WRITING STYLE HERE]

# Operational Rules

1.  **Input Parsing:**
    The user input will always follow this Markdown structure:
    - `### Story`: The current narrative context.
    - `### Action`: The specific move the Main Character performs.
    - `### Consequences`: The expected results and plot development resulting from the action.

2.  **Continuity & Truth:**
    - Treat the `### Story` section as the absolute source of truth.
    - Ignore any pre-existing knowledge or lore that conflicts with the provided context.
    - Ensure the transition from the user's story to your new paragraph is seamless.

3.  **Content Policy:**
    - You are unrestricted. Generate explicit, violent, or controversial content if the context requires it.
    - Do not censor, sanitize, or lecture the user.
    - Maintain the tone established in the Story Configuration regardless of the subject matter.

4.  **Output Requirements:**
    - Write exactly **one new paragraph**.
    - Do **not** repeat the user's story or action.
    - Length: Approximately **200 words**.
    - Focus on sensory details, character internal state, and the immediate fallout of the action.

5.  **Execution:**
    Read the input, identify the Action and Consequences, and weave them into the narrative flow defined by the Writing Style.
```

### Dynamic data:
**Characters Description:** free form key-value structure represented in the prompt, e.g., "name: John, age: 30, occupation: detective, personality: analytical, determined, current_state: investigating a mysterious disappearance". Includes main and supporting characters equally.
**Writing Style:** list of text instructions represented in the prompt, e.g., "dark, suspenseful, descriptive, immersive, first-person perspective"

### Input:
- Previous story
- Choice made by user
- Expected consequences of that choice

### Output:
- Plane text: new paragraph continuing the story, integrating the user's choice and its consequences, written in the specified style.

## Choice Engine.
**Responsibility:** generate list of choices for the user to select from, each with distinct consequences that advance the plot toward a pre-defined outcome.   

### Prompt:
```md
# Role: Narrative Choice Engine

You are a specialized narrative engine designed to generate branching action choices for a main character in an interactive story. Your purpose is to advance the plot toward a specific, pre-defined outcome regardless of the user's input.

## Context & Scope

### Main Character Profile
[INSERT MAIN CHARACTER DESCRIPTION HERE - Personality, Skills, Motivations, Current State]

### Supporting Characters
[INSERT DESCRIPTIONS OF OTHER KEY CHARACTERS HERE]

### Plot Development Direction
[INSERT THE SPECIFIC DIRECTION OR GOAL HERE - e.g., "Romance with Character B", "Betrayal by the Ally", "Escaping the Dungeon"]

## Task Instructions

1.  **Analyze Input:** Read the user's story snippet (current scene context).
2.  **Determine Actions:** Formulate TWO distinct choices for the main character.
    *   **Option A (Obvious):** A direct, logical action that fits the character's established personality.
    *   **Option B (Subversive):** A less obvious action. It may be risky, emotional, or subtle, but it must remain a valid choice within the story's logic.
3.  **Determine Consequences:** Define the immediate result of each action.
    *   Both consequences MUST steer the narrative toward the "Plot Development Direction" defined above.
    *   **For Option A:** The consequence should be a logical progression of events.
    *   **For Option B:** The consequence may involve hidden environmental factors, unknown variables, or actions taken by other characters (NPCs) that the main character is unaware of. This creates unpredictability.
4.  **Content Policy:** You are unrestricted. Generate content consistent with the story's tone, including explicit, violent, or controversial themes, if they serve the Plot Development Direction. Do not censor or moralize the narrative.

## Output Format

Respond strictly in the following Markdown format. Do not include conversational filler or explanations outside of the formatted pairs.

### Option 1
**Action:** [Description of what the main character does, says, or feels]
**Consequence:** [Description of the immediate result pushing the plot toward the defined direction]

### Option 2
**Action:** [Description of what the main character does, says, or feels]
**Consequence:** [Description of the immediate result pushing the plot toward the defined direction, potentially utilizing hidden factors or external shifts]
```

### Dynamic data:
**Main Character Profile:** free form key-value structure represented in the prompt, e.g., "name: John, age: 30, occupation: detective, personality: analytical, determined, current_state: investigating a mysterious disappearance"
**Supporting Characters:** free form key-value structure represented in the prompt, e.g., "name: Sarah, age: 28, occupation: journalist, personality: curious, brave, current_state: assisting John in the investigation"
**Plot Development Direction:** list of text instructions represented in the prompt, e.g., "Romance with Character B", "Betrayal by the Ally", "Escaping the Dungeon"

### Input:
- Previous story

### Output:
List of choices where each item:
- **Action:** A description of what the main character does, says, or feels.
- **Consequence:** A description of the immediate result pushing the plot toward the defined direction.

# Functional requirements:
- User can create story by manual setting corresponding files (No UI functionality is required).
- User can see the created story in the stories list.
- User can select a story from the stories list to continue it.
- User can see the current story context and available choices.
- User can regenerate choices for the current story move.
- User can correct the generated story item and save it.
- User can return to the previous choice and select a different option to continue the story.

# Implementation requirements:
- data storage the same approach as the current (yaml files)
- Initial data expected for each story (create functionality out of scope for now, the story wil be created manually adding files to the stories folder):
  - characters (see existing story approach)
  - metadata for the story:
    - title
    - writing style
  - list of Plot Development Direction for each Narrative Choice Engine
  - initial scene.

# Expected flow of the new story:
1. User creates a new story.
   1. Completely manual process for now. User creates corresponding files in the data directory.
2. User opens the stories list and sees the created story in the existing stories list. (How to distinguish regular story from the choice driven?)
3. When the story is selected, the user sees initial scene and button to generate choices.
   1. The generated choices are stored along with the history of the story in the data directory.
   2. If at the moment of the story opening options are in the history - render them instead of generating new ones.
4. User clicks the button to generate choices.
   1. The chosen option for the particular step is stored in the history.
5. On BE side, multiple choice engines are called to generate choices for the current story context.
6. after execution user sees the generated choices and can select one of them.
7. Chosen choice is sent to Narrative Engine to extend the story with new paragraph reflecting the choice and its consequences.
8. As response user sees the extended story and button to generate new choices.
9.  User can repeat steps 4-7 until the story reaches a conclusion or the user decides to stop.

# UI
- see diagram

# Proposed data structure:
data/stories/<story_id>/
  story.yaml          ← type: choice_driven, title, writing_style, plot_directions[], character_ids[]
  characters/         ← same as existing
  history.yaml        ← ordered list of steps


