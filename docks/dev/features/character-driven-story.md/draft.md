## Concept.

### Roles:

#### Character
The agent based on a character configs (e.g., personality traits, background, goals, memory). Reacts on the story flow when triggered. Generates actions and dialogue consistent with its character profile.

#### Narrator
The agent responsible for maintaining the overall narrative flow. Creates story from the actions and dialogues of characters, ensuring coherence and progression of the plot.

#### Player
The human participant who interacts with the story, making choices and influencing the direction of the narrative. From the narrator perspective, the player is treated as a one more character within the story.

### Interactions flow.
The story structure is divided by scenes (similar to the scene driven story).
Scene is a minimal unit of the story, typically representing a single event or interaction. Each scene contains:
- set of characters involved in the scene.

#### The play flow:
**Scene start** The first paragraph of the scene as a play field. Next user can choose either post his own actions, words, reactions or trigger a character from the list to act within the scene. As a result of both actions is a new paragraph added to the scene. When scene ends, player can trigger finishing the scene.

#### Player makes own move:
Post message -> call narrator to weave it into the story -> return updated scene.

#### Player triggers character:
Select character from the list -> call the character agent to perform the action within the scene -> call narrator to weave it into the story -> return updated scene.

#### Finishing the scene:
Trigger finishing the scene -> call agents to make summary, update character.


## Functional requirements
**FR1** Create new story with title. Create set of characters for the story (on the current step can be done via manual file manipulation)
**FR2** Create new scene within the story.
  - Choose subset of characters.
  - Choose character for player to control within the scene.
  - Provide context for the scene.
  - Define writing style for narrator.
  - Define General scene direction and tone.
- **FR3** Be able to provide player actions as a raw text input and see it reflected in the updated scene.
- **FR4** Trigger character to act within the scene and see it reflected in the updated scene.
- **FR5** Correct the scene item.
- **FR6** Regenerate last player affect being able to correct the player action leading to the updated scene.
- **FR7** Delete last scene item.
- **FR8** Finish the scene receiving the scene summary and updates for characters memories.
- **FR9** Start new scene.
- Choose llm for character and narrator agents.

-------------------------------------------------------------------------------------------------

## Questions to answer:
### 1. Product and scope

#### Decisions
- The feature separates character agents from the narrator. The current approach puts all character memories into one context, which can cause memories to be assigned to the wrong characters and can degrade characters toward generic behavior over time.
- Character-driven stories are a new story type, separate from scene-based stories for the MVP. They may replace or supersede scene-based stories later, but that is out of scope for now.
- The MVP must satisfy the functional requirements listed above.
- The player can trigger only characters selected for the scene during scene creation.
- The success criterion for the MVP: fewer character hallucinations, stronger character consistency.
- Should existing scene-based stories remain fully supported while character-driven stories are introduced? **Yes**
- Which existing scene-based capabilities must be available in the new story type, and which can wait? **TBD**

### 2. Story progression rules

#### Decisions
- The player decides when a character should act.
- A character may act repeatedly during a scene.
- The player can either trigger a character to react using the current context or provide optional guidance for the character's action. Guidance is intended to reduce hallucinations and steer the action.
- Each turn ends when the narrator generates a new paragraph for the scene.
- The player controls each turn; the scene does not progress autonomously.
- Finishing a scene generates a summary and updates the participating characters' memories.

#### Questions
- Does the character's generated action become visible before the narrator generates the final paragraph, or is only the narrator's paragraph shown? **It should be stored to satisfy FR6**
- Can the player trigger a character immediately after any paragraph, including a paragraph produced from another character? **Yes** The player is a main orchestrator of the scene progression.
- Can the player provide guidance that contradicts the character's personality or memory, and how should that conflict be handled? **For now yes. If player wants to ruin the story, it's their choice.)**
- What conditions, if any, prevent a character from being triggered again? **For now character can be triggered repeatedly without restriction.**

### 3. UI/UX design
Look `docks/dev/features/character-driven-story.md/ui-ux.md` for details on the UI/UX design.

### 4. Data storage design
Look `docks/dev/features/character-driven-story.md/data-storage.md` for details on the data storage design.

### 5. Interaction flow and scene structure
Look `docks/dev/features/character-driven-story.md/UX-play-flow.md` for details on the interaction flow and scene structure.

### 6. Main algorithm for story progression
Look `docks/dev/features/character-driven-story.md/Algorithms.md` for details on the main algorithm for story progression.

### 7. Agents design
Look `docks/dev/features/character-driven-story.md/llm_agents.md` for details on the design of the character and narrator agents.

### 8. API and compatibility
Look `docks/dev/features/character-driven-story.md/API.md` for details on the API and compatibility.

### 9. Implementation plan

