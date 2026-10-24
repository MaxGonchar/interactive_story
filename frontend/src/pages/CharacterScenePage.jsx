import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getCharacters } from '../api/characters'
import { getCharacterScene } from '../api/character_play'
import { getModels } from '../api/models'
import { getStory } from '../api/stories'
import SceneHeader from '../components/SceneHeader'
import StoryTimeline from '../components/StoryTimeline'
import { deriveModelDefaults } from './characterSceneHelpers'

function CharacterScenePage() {
  const { storyId, sceneId } = useParams()
  const [scene, setScene] = useState(null)
  const [storyTitle, setStoryTitle] = useState('')
  const [characters, setCharacters] = useState([])
  const [models, setModels] = useState([])
  const [, setCharacterModelId] = useState(null)
  const [narratorModelId, setNarratorModelId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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

  if (loading) return <p>Loading...</p>
  if (error) return <p className="scene-page__error">{error}</p>

  const characterNames = new Map(characters.map((character) => [character.id, character.name]))
  const nameOf = (id) => characterNames.get(id) ?? id
  const playerName = scene.user_character_id ? nameOf(scene.user_character_id) : 'Narrator'
  const npcNames = (scene.character_ids ?? []).map(nameOf)

  return (
    <div className="scene-page scene-page--fixed-frame">
      <SceneHeader
        scene={scene}
        storyId={storyId}
        storyTitle={storyTitle}
        models={models}
        selectedModelId={narratorModelId}
        onModelChange={setNarratorModelId}
        disabled={scene.finished}
        modelLabel="LLM"
      />
      <p className="scene-page__participants">
        <span>Player: {playerName}</span>
        {npcNames.length > 0 && <span>Characters: {npcNames.join(', ')}</span>}
      </p>
      <div className="scene-page__messages" role="log" aria-label="Scene story">
        <StoryTimeline items={scene.items ?? []} />
      </div>
      {scene.finished && (
        <div className="scene-page__footer">
          <p className="scene-page__finished" role="status">This scene is finished.</p>
        </div>
      )}
    </div>
  )
}

export default CharacterScenePage
