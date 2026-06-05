import { useState } from 'react';
import { BookmarkList } from '../components/BookmarkList.jsx';

export function Bookmarks({ bookmarksApi }) {
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');

  function submit(event) {
    event.preventDefault();
    bookmarksApi.addBookmark({ title, url });
    setTitle('');
    setUrl('');
  }

  return (
    <main className="card">
      <h1>Bookmarks</h1>
      <form onSubmit={submit} className="form inline-form">
        <label>Title<input value={title} onChange={(event) => setTitle(event.target.value)} required /></label>
        <label>URL<input type="url" value={url} onChange={(event) => setUrl(event.target.value)} required /></label>
        <button type="submit">Add bookmark</button>
      </form>
      <BookmarkList bookmarks={bookmarksApi.bookmarks} onDelete={bookmarksApi.deleteBookmark} />
    </main>
  );
}
