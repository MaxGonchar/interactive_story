import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getScene, playScene, finishScene, editMessage } from '../api/scenes'
import SceneHeader from '../components/SceneHeader'
import MessageList from '../components/MessageList'
import MessageComposer from '../components/MessageComposer'
import SceneActions from '../components/SceneActions'

function ScenePage() {
  const { storyId, sceneId } = useParams()
  const [scene, setScene] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)
  const [opError, setOpError] = useState(null)

  useEffect(() => {
    getScene(storyId, sceneId)
      .then((response) => setScene(response.data))
      .catch((err) => setError(err.message ?? 'Failed to load scene'))
      .finally(() => setLoading(false))
  }, [storyId, sceneId])

  async function handleSend(content) {
    setOpError(null)
    setBusy(true)
    try {
      const response = await playScene(storyId, sceneId, content)
      const { user_message, assistant_message } = response.data
      setScene((prev) => ({
        ...prev,
        messages: [...prev.messages, user_message, assistant_message],
      }))
    } catch (err) {
      setOpError(err.message ?? 'Failed to send message')
    } finally {
      setBusy(false)
    }
  }

  async function handleFinish(summary) {
    setOpError(null)
    setBusy(true)
    try {
      const response = await finishScene(storyId, sceneId, summary)
      setScene((prev) => ({
        ...prev,
        finished: response.data.finished,
        scene_summary: response.data.scene_summary,
      }))
    } catch (err) {
      setOpError(err.message ?? 'Failed to finish scene')
    } finally {
      setBusy(false)
    }
  }

  async function handleEditMessage(messageId, content) {
    setOpError(null)
    setBusy(true)
    try {
      const response = await editMessage(storyId, sceneId, messageId, content)
      setScene((prev) => ({
        ...prev,
        messages: prev.messages.map((m) =>
          m.id === messageId ? response.data : m
        ),
      }))
    } catch (err) {
      setOpError(err.message ?? 'Failed to edit message')
    } finally {
      setBusy(false)
    }
  }

  if (loading) {
    return <p>Loading...</p>
  }

  if (error) {
    return <p>{error}</p>
  }

  return (
    <>
      <SceneHeader scene={scene} />
      <MessageList messages={scene.messages} onEdit={handleEditMessage} disabled={scene.finished || busy} />
      {opError && <p>{opError}</p>}
      <MessageComposer
        onSend={handleSend}
        disabled={scene.finished || busy}
      />
      <SceneActions
        finished={scene.finished}
        sceneSummary={scene.scene_summary}
        onFinish={handleFinish}
      />
    </>
  )
}

export default ScenePage
