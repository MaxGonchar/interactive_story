import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getStory } from '../api/stories'
import SceneList from '../components/SceneList'

function StoryPage() {
  const { storyId } = useParams()
  const [story, setStory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    getStory(storyId)
      .then((response) => setStory(response.data))
      .catch((err) => setError(err.message ?? 'Failed to load story'))
      .finally(() => setLoading(false))
  }, [storyId])

  if (loading) {
    return <p>Loading...</p>
  }

  if (error) {
    return <p>{error}</p>
  }

  return (
    <>
      <h1>{story.title}</h1>
      <SceneList
        scenes={story.scenes}
        activeSceneId={story.active_scene_id}
        onSelect={(sceneId) => navigate(`/stories/${storyId}/scenes/${sceneId}`)}
      />
    </>
  )
}

export default StoryPage
