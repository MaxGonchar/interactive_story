import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import StoriesPage from './pages/StoriesPage'
import StoryPage from './pages/StoryPage'
import ScenePage from './pages/ScenePage'
import ChoiceDrivenStoryPage from './pages/ChoiceDrivenStoryPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/stories" replace />} />
        <Route path="/stories" element={<StoriesPage />} />
        <Route path="/stories/:storyId" element={<StoryPage />} />
        <Route path="/stories/:storyId/play" element={<ChoiceDrivenStoryPage />} />
        <Route path="/stories/:storyId/scenes/:sceneId" element={<ScenePage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
