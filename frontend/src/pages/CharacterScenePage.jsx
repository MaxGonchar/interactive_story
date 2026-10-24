import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getCharacters } from '../api/characters'
import { getCharacterScene, submitCharacterTurn } from '../api/character_play'
import { getModels } from '../api/models'
import { getStory } from '../api/stories'
import SceneHeader from '../components/SceneHeader'
import StoryTimeline from '../components/StoryTimeline'
import TurnComposer, { PLAYER_ACTOR } from '../components/TurnComposer'
import { deriveModelDefaults } from './characterSceneHelpers'

function CharacterScenePage() {
  const { storyId, sceneId } = useParams()
  const [scene, setScene] = useState(null)
  const [storyTitle, setStoryTitle] = useState('')
  const [characters, setCharacters] = useState([])
  const [models, setModels] = useState([])
  const [characterModelId, setCharacterModelId] = useState(null)
  const [narratorModelId, setNarratorModelId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actor, setActor] = useState(PLAYER_ACTOR)
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const [turnError, setTurnError] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const [sceneResponse, storyResponse, charactersResponse, modelsResponse] =
          await Promise.all([
            getCharacterScene(storyId, sceneId),
            getStory(storyId),
            getCharacters(storyId),
            getModels(),
          ])
        const loadedScene = sceneResponse.data
        const registry = modelsResponse.data
        const modelDefaults = deriveModelDefaults(loadedScene.items ?? [], registry)

        setScene(loadedScene)
        setStoryTitle(storyResponse.data.title)
        setCharacters(charactersResponse.data)
        setModels(
          Object.entries(registry.models).map(([id, model]) => ({ id, ...model }))
        )
        setCharacterModelId(modelDefaults.characterModelId)
        setNarratorModelId(modelDefaults.narratorModelId)
      } catch (err) {
        setError(err.message ?? 'Failed to load scene')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [storyId, sceneId])

  async function handleSubmit() {
    const trimmed = text.trim()
    const isPlayer = actor === PLAYER_ACTOR
    if (isPlayer && !trimmed) return

    const payload = {
      actor: isPlayer ? { type: 'player' } : { type: 'character', character_id: actor },
      ...(isPlayer ? { action: trimmed } : { guidance: trimmed }),
      character_model_id: characterModelId,
      narrator_model_id: narratorModelId,
    }

    setTurnError(null)
    setSending(true)
    try {
      const response = await submitCharacterTurn(storyId, sceneId, payload)
      const item = response.data
      setScene((current) => ({ ...current, items: [...(current.items ?? []), item] }))
      setText('')
      setActor(PLAYER_ACTOR)
      if (item.llm_data?.character_model_id != null) {
        setCharacterModelId(item.llm_data.character_model_id)
      }
      if (item.llm_data?.narrator_model_id != null) {
        setNarratorModelId(item.llm_data.narrator_model_id)
      }
    } catch (err) {
      setTurnError(err.message ?? 'Failed to submit turn')
    } finally {
      setSending(false)
    }
  }

  if (loading) return <p>Loading...</p>
  if (error) return <p className="scene-page__error">{error}</p>

  const characterNames = new Map(characters.map((character) => [character.id, character.name]))
  const nameOf = (id) => characterNames.get(id) ?? id
  const playerName = scene.user_character_id ? nameOf(scene.user_character_id) : 'Narrator'
  const npcCharacters = (scene.character_ids ?? []).map((id) => ({ id, name: nameOf(id) }))
  const npcNames = npcCharacters.map((character) => character.name)

  return (
    <div className="scene-page scene-page--fixed-frame">
      <SceneHeader
        scene={scene}
        storyId={storyId}
        storyTitle={storyTitle}
        models={models}
        selectedModelId={narratorModelId}
        onModelChange={setNarratorModelId}
        disabled={scene.finished || sending}
        modelLabel="LLM"
      />
      <p className="scene-page__participants">
        <span>Player: {playerName}</span>
        {npcNames.length > 0 && <span>Characters: {npcNames.join(', ')}</span>}
      </p>
      <div className="scene-page__messages" role="log" aria-label="Scene story">
        <StoryTimeline items={scene.items ?? []} />
      </div>
      <div className="scene-page__footer">
        {scene.finished ? (
          <p className="scene-page__finished" role="status">This scene is finished.</p>
        ) : (
          <>
            {turnError && <p className="scene-page__error" role="alert">{turnError}</p>}
            <TurnComposer
              actor={actor}
              onActorChange={setActor}
              characters={npcCharacters}
              text={text}
              onTextChange={setText}
              models={models}
              characterModelId={characterModelId}
              onCharacterModelChange={setCharacterModelId}
              onSubmit={handleSubmit}
              sending={sending}
            />
          </>
        )}
      </div>
    </div>
  )
}

export default CharacterScenePage
