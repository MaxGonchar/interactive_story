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
