import { randomId } from '@privacy-sync/shared';

export function useBookmarks(state, setState) {
  function addBookmark(bookmark) {
    const now = new Date().toISOString();
    setState((current) => ({
      ...current,
      bookmarks: [
        ...current.bookmarks,
        { bookmarkId: randomId('bookmark_'), title: bookmark.title, url: bookmark.url, createdAt: now, updatedAt: now }
      ]
    }));
  }

  function editBookmark(bookmarkId, updates) {
    setState((current) => ({
      ...current,
      bookmarks: current.bookmarks.map((bookmark) => (
        bookmark.bookmarkId === bookmarkId ? { ...bookmark, ...updates, updatedAt: new Date().toISOString() } : bookmark
      ))
    }));
  }

  function deleteBookmark(bookmarkId) {
    setState((current) => ({
      ...current,
      bookmarks: current.bookmarks.filter((bookmark) => bookmark.bookmarkId !== bookmarkId)
    }));
  }

  return { bookmarks: state.bookmarks, addBookmark, editBookmark, deleteBookmark };
}
