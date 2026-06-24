import { useEffect, useRef } from "react";

/**
 * Subscribes to /ws/board/{projectId} and invokes onEvent for every message.
 * Used by the Kanban board page to reflect other users' changes live.
 */
export function useBoardSocket(projectId, onEvent) {
  const handlerRef = useRef(onEvent);
  handlerRef.current = onEvent;

  useEffect(() => {
    if (!projectId) return undefined;

    const token = localStorage.getItem("access_token");
    const wsBase = (import.meta.env.VITE_WS_URL || `ws://${window.location.host}`).replace(/^http/, "ws");
    const socket = new WebSocket(`${wsBase}/ws/board/${projectId}?token=${token}`);

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        handlerRef.current?.(payload);
      } catch {
        // ignore malformed frames
      }
    };

    return () => socket.close();
  }, [projectId]);
}
