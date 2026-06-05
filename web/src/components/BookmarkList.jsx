export function BookmarkList({ bookmarks, onDelete }) {
  if (!bookmarks.length) return <p>No bookmarks yet. Add one to test encrypted sync.</p>;
  return (
    <ul className="bookmark-list">
      {bookmarks.map((bookmark) => (
        <li key={bookmark.bookmarkId}>
          <div>
            <strong>{bookmark.title}</strong>
            <a href={bookmark.url} target="_blank" rel="noreferrer">{bookmark.url}</a>
          </div>
          <button className="danger" onClick={() => onDelete(bookmark.bookmarkId)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
