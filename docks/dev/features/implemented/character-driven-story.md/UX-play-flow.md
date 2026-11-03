# Interaction flow

## 1. Create Story
1. Create the story folder manually. The folder name is the story ID (UUID).
2. In the story folder:
   1. Create `story.yaml` with the title, `type: character_driven`, and creation time. See `docks/dev/features/character-driven-story.md/data-storage.md` for the format.
   2. Create a `characters` folder and add one YAML file per character, including the character's profile and initial memory.
   3. Create an empty `scenes` folder.

## 2. Create First Scene
1. From the story's scenes page, select **Create scene**.
2. Choose the player character, or **Narrator** to play without one. A chosen character is controlled by the player and is not available as an NPC trigger in this scene.
3. Select zero or more other story characters as scene participants. These are the NPCs the player can trigger during the scene.
4. Enter at least one context item describing the starting situation.
5. Enter the opening narrator paragraph, general scene direction, and writing style.
6. Select the character-agent model and narrator-agent model.
7. Create the scene. The app opens it with the opening paragraph as its first story item and the composer ready for a player turn.


## 3. Player Turn
1. Read the current narrator paragraph or paragraphs in the scene timeline.
2. Leave **Actor** set to **Player**, enter an action, dialogue, or reaction, and select the narrator model for this turn.
3. Submit the turn. The narrator incorporates the player action into a new paragraph.
4. When generation succeeds, the new narrator paragraph appears at the end of the timeline and the composer is cleared with **Actor** reset to **Player**. The player action is retained with the turn data but is not shown in the default story view.

### Trigger a character
1. Select one of the NPCs included when the scene was created. The player may trigger the same character repeatedly.
2. Optionally enter guidance for the character. Leave it empty to let the character react to the current scene context.
3. Select the character-agent model and narrator model, then trigger the character.
4. The character agent generates the character's action; the narrator uses that action to produce the next paragraph.
5. On success, show only the narrator paragraph in the timeline. Keep the guidance and generated action in the turn data for correction and regeneration.

### Correct or remove a paragraph
- Use **Edit** on any paragraph to change only its displayed narration. Save applies the edit in place; cancel discards it.
- Use **Delete** on the last paragraph to remove that turn from the scene. The opening paragraph cannot be deleted.
- Use **Retry** on the last paragraph to stage a replacement. The opening paragraph cannot be retried. Restore the actor and text used for the turn, allow the player to change the actor, input, or models, and keep the current paragraph visible until replacement succeeds.
- Canceling a retry restores the composer draft and selections that were present before retry mode. If replacement fails, retain the retry input and selections so the player can adjust and resubmit.
- While a turn is processing, while a retry is staged, or after the scene is finished, disable paragraph actions and turn submission (except the staged replacement). If either the character call or the narration fails, nothing is saved; the player resubmits the whole request, and a retried character action may differ from the failed attempt.

## 4. Finish Scene
1. Select **Finish** in the composer area.
2. Review the **Summary** tab and one memory-update tab for each character participating in the scene. Generate all outputs, or generate/regenerate only the selected output.
3. Edit the generated summary and memory updates as needed. Switching tabs preserves each tab's text; generation errors remain visible and only failed outputs need to be retried.
4. Select **Finish scene** to save the reviewed summary, update each participating character's memory, and mark the scene finished. If any memory tab was neither generated nor edited, the app warns once and asks the user to select **Finish scene** again to confirm.
5. The finished scene remains readable, but its composer and paragraph actions are disabled. Cancel closes the review without finishing or saving the proposed summary and memory updates.

## 5. Create Next Scene
1. Return to the story's scenes page and select **Create scene**.
2. Set up the next scene using the current story characters. Their saved memories from completed scenes are available to their character agents.
3. Choose the player character (or **Narrator**) and NPC participants for this scene, then provide its context, opening paragraph, narrative direction, writing style, and agent models. The form pre-fills the context (previous context plus summary), writing style, opening paragraph (the previous scene's last narration), and agent models from the previous scene.
4. Create the scene and continue play from its opening narrator paragraph. The previous scene remains finished and unchanged.
