import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getScene } from '../api/scenes'
import SceneHeader from '../components/SceneHeader'
import MessageList from '../components/MessageList'
import MessageComposer from '../components/MessageComposer'
import SceneActions from '../components/SceneActions'

function ScenePage() {
  const { storyId, sceneId } = useParams()
  const [scene, setScene] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getScene(storyId, sceneId)
      .then((response) => setScene(response.data))
      .catch((err) => setError(err.message ?? 'Failed to load scene'))
      .finally(() => setLoading(false))
  }, [storyId, sceneId])

  if (loading) {
    return <p>Loading...</p>
  }

  if (error) {
    return <p>{error}</p>
  }

  return (
    <>
      <SceneHeader scene={scene} />
      <MessageList messages={scene.messages} />
      <MessageComposer
        onSend={() => console.log('send')}
        disabled={scene.finished}
      />
      <SceneActions
        finished={scene.finished}
        sceneSummary={scene.scene_summary}
        onFinish={() => console.log('finish')}
      />
    </>
  )
}

export default ScenePage
