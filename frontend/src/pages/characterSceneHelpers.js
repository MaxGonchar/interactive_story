export function deriveModelDefaults(items, registry) {
  const models = registry.models
  const defaultModelId = registry.default_model_id
  const latestItem = items.at(-1)
  const latestCharacterItem = [...items]
    .reverse()
    .find((item) => item.llm_data?.character_model_id != null)

  const narratorModelId = latestItem?.llm_data?.narrator_model_id
  const characterModelId = latestCharacterItem?.llm_data?.character_model_id

  return {
    characterModelId:
      characterModelId != null && Object.hasOwn(models, characterModelId)
        ? characterModelId
        : defaultModelId,
    narratorModelId:
      narratorModelId != null && Object.hasOwn(models, narratorModelId)
        ? narratorModelId
        : defaultModelId,
  }
}

export function buildScenePrefill(previousScene) {
  const items = previousScene.items ?? []

  return {
    context: [
      ...(previousScene.context ?? []),
      ...(previousScene.scene_summary ?? []),
    ],
    writingStyle: previousScene.scene_description?.writing_style ?? '',
    firstMessage: items.at(-1)?.narration ?? '',
  }
}
