import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import NavBar from './components/NavBar'
import StoriesPage from './pages/StoriesPage'
import StoryPage from './pages/StoryPage'
import ScenePage from './pages/ScenePage'
import NewScenePage from './pages/NewScenePage'
import ChoiceDrivenStoryPage from './pages/ChoiceDrivenStoryPage'

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <NavBar />
        <div className="app-content">
          <Routes>
            <Route path="/" element={<Navigate to="/stories" replace />} />
            <Route path="/stories" element={<StoriesPage />} />
            <Route path="/stories/:storyId" element={<StoryPage />} />
            <Route path="/stories/:storyId/play" element={<ChoiceDrivenStoryPage />} />
            <Route path="/stories/:storyId/scenes/new" element={<NewScenePage />} />
            <Route path="/stories/:storyId/scenes/:sceneId" element={<ScenePage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App

