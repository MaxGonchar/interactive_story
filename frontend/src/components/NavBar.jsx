import { Link } from 'react-router-dom'
import { StoriesIcon } from './icons'

function NavBar() {
  return (
    <nav className="nav-bar">
      <Link to="/stories" title="Stories" className="nav-bar__link">
        <StoriesIcon className="nav-bar__icon" />
      </Link>
    </nav>
  )
}

export default NavBar
