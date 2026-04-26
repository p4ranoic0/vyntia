import { useCallback, useEffect, useState } from "react";

/**
 * Hook que detecta si el usuario ha hecho scroll.
 * Útil para mostrar/ocultar sombras en el header.
 */
export function useScrolled(threshold = 10) {
  const [isScrolled, setIsScrolled] = useState(false);

  const handleScroll = useCallback(() => {
    setIsScrolled(window.scrollY > threshold);
  }, [threshold]);

  useEffect(() => {
    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, [handleScroll]);

  return isScrolled;
}
