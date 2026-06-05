import { useEffect, useState } from 'react';
import { loadState, saveState } from '../services/storage.js';

export function useLocalStorageState() {
  const [state, setState] = useState(() => loadState());

  useEffect(() => {
    saveState(state);
  }, [state]);

  return [state, setState];
}
