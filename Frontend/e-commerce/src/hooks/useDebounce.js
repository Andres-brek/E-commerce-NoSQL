import { useEffect, useState } from 'react';

// Devuelve el valor solo después de que pasen `delay` ms sin cambios.
// Cada nueva pulsación cancela el timer previo, evitando llamadas
// innecesarias al backend mientras el usuario escribe.
export function useDebounce(value, delay = 350) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);

  return debounced;
}
