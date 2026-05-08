import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getStories } from '../api/stories'
import StoryList from '../components/StoryList'

function StoriesPage() {
  const [stories, setStories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    getStories()
      .then((response) => setStories(response.data))
      .catch((err) => setError(err.message ?? 'Failed to load stories'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <p>Loading...</p>
  }

  if (error) {
    return <p>{error}</p>
  }

  return (
    <StoryList
      stories={stories}
      onSelect={(id) => navigate(`/stories/${id}`)}
    />
  )
}

export default StoriesPage
