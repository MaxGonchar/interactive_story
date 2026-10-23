let _counter = 1
function uid() {
  return `test-id-${_counter++}`
}

export function makeMessage(overrides = {}) {
  return {
    id: uid(),
    role: 'user',
    content: 'Test message content',
    ...overrides,
  }
}

export function makeScene(overrides = {}) {
  return {
    id: uid(),
    storyId: uid(),
    finished: false,
    summary: null,
    messages: [],
    ...overrides,
  }
}

export function makeCharacterSceneItem(overrides = {}) {
  return {
    id: uid(),
    actor: null,
    input: null,
    character_action: null,
    narration: 'A scene begins.',
    llm_data: {
      character_model_id: 'character-model',
      narrator_model_id: 'narrator-model',
    },
    ...overrides,
  }
}

export function makeCharacterScene(overrides = {}) {
  return {
    id: uid(),
    finished: false,
    context: [],
    scene_summary: null,
    scene_description: {
      general_scene_guide: '',
      writing_style: '',
    },
    items: [],
    ...overrides,
  }
}

export function makeModel(overrides = {}) {
  return {
    name: 'Test Model',
    providerModelID: 'test-provider-model',
    ...overrides,
  }
}

export function makeModelRegistry(overrides = {}) {
  const modelId = uid()
  const model = makeModel()
  return {
    models: { [modelId]: model },
    default_model_id: modelId,
    ...overrides,
  }
}

export function makeStory(overrides = {}) {
  return {
    id: uid(),
    title: 'Test Story',
    type: 'scene',
    scenes: [],
    ...overrides,
  }
}

export function makeCharacter(overrides = {}) {
  return {
    id: uid(),
    name: 'Test Character',
    ...overrides,
  }
}
