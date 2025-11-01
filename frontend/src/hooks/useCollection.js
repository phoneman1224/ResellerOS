import { useEffect, useState, useCallback } from 'react';
import { useApi } from '../context/ApiContext.jsx';

export function useCollection (resource) {
  const api = useApi();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.list(resource);
      setItems(data);
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [api, resource]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { items, loading, error, refresh, setItems };
}
