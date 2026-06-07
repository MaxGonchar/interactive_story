# Problems

## Only one message bubble can be edited at a time
Currently I can open more than one message bubble for editing, which causes confusion and bugs. The UI should enforce that only one bubble can be in edit mode at a time.

# Enhancements

## User Character Card

- No user character card in a story data. No place for it in the system prompt. (As a user I want to play different roles in a story. Since all personality related traits will be a user responsobility, the card should contain a user character appearance so LLM can use it in the system prompt to create more personalized and immersive responses)
  - the card form should be free form dict with "name" key as a mandatory field and other fields that can be added on demand. The final character card text that is supposed to be injected into the system prompt will be generated fallowing next pattern:
  ```md
  ## {{name}}

  ### {{feature_key}}
  {{feature_value if it's string}}
  - {{feature_value if it's list}}
  ```

---

## Character Card

- Character card is currently restricted with predefined set of fields. It expects all character fallow the same schema and restricts space for experiments. How would I like to see character data structure that will allow to more flexible:
  - mandatory fields: "name", and "memory"
  - The final character text that is supposed to be injected into the system prompt will be generated fallowing next pattern:
  ```md
  ## {{name}}

  ### {{feature_key}}
  {{feature_value if it's string}}
  - {{feature_value if it's list}}
  ```
  This will allow me to play with different types of characters with different sets of features without changing the code.

  Architectural questions:
  - who will be responsible for character mg text generating.

---

## Navigation

- main nav bar (discuss placement and items to be added there)
