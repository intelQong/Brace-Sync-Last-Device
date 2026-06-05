export function Nav({ currentPage, setCurrentPage, signedIn }) {
  const items = [
    ['dashboard', 'Dashboard'],
    ['bookmarks', 'Bookmarks'],
    ['settings', 'Settings']
  ];
  return (
    <nav className="nav">
      <strong>Privacy Sync</strong>
      <div className="nav-links">
        {items.map(([key, label]) => (
          <button key={key} className={currentPage === key ? 'active' : ''} disabled={!signedIn} onClick={() => setCurrentPage(key)}>
            {label}
          </button>
        ))}
      </div>
    </nav>
  );
}
