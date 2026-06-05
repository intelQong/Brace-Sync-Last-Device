import { useState } from 'react';
import { Nav } from './components/Nav.jsx';
import { useAuth } from './hooks/useAuth.js';
import { useBookmarks } from './hooks/useBookmarks.js';
import { useLocalStorageState } from './hooks/useLocalStorage.js';
import { useSync } from './hooks/useSync.js';
import { Bookmarks } from './pages/Bookmarks.jsx';
import { Dashboard } from './pages/Dashboard.jsx';
import { Login } from './pages/Login.jsx';
import { Settings } from './pages/Settings.jsx';

export default function App() {
  const [state, setState] = useLocalStorageState();
  const [currentPage, setCurrentPage] = useState('dashboard');
  const auth = useAuth(state, setState);
  const sync = useSync(state, setState);
  const bookmarksApi = useBookmarks(state, setState);

  if (!auth.user) {
    return <Login onSignIn={auth.signIn} />;
  }

  return (
    <>
      <Nav currentPage={currentPage} setCurrentPage={setCurrentPage} signedIn={Boolean(auth.user)} />
      {currentPage === 'dashboard' && <Dashboard state={state} sync={sync} />}
      {currentPage === 'bookmarks' && <Bookmarks bookmarksApi={bookmarksApi} />}
      {currentPage === 'settings' && <Settings state={state} setState={setState} auth={auth} />}
    </>
  );
}
