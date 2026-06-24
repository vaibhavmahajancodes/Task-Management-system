import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";
import { notificationService } from "../services/domainServices";

const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const socketRef = useRef(null);

  const refresh = useCallback(async () => {
    if (!user) return;
    try {
      const [list, count] = await Promise.all([notificationService.list(), notificationService.unreadCount()]);
      setNotifications(list);
      setUnreadCount(count.unread_count);
    } catch {
      // Silently ignore; the bell icon will just show stale data until the next poll/socket event.
    }
  }, [user]);

  useEffect(() => {
    if (!user) {
      setNotifications([]);
      setUnreadCount(0);
      return;
    }
    refresh();

    const token = localStorage.getItem("access_token");
    const wsBase = (import.meta.env.VITE_WS_URL || `ws://${window.location.host}`).replace(/^http/, "ws");
    const socket = new WebSocket(`${wsBase}/ws/notifications?token=${token}`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.event === "notification") {
          setNotifications((prev) => [payload.data, ...prev].slice(0, 50));
          setUnreadCount((c) => c + 1);
        }
      } catch {
        // ignore malformed frames
      }
    };

    return () => socket.close();
  }, [user, refresh]);

  const markRead = async (id) => {
    await notificationService.markRead(id);
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    setUnreadCount((c) => Math.max(0, c - 1));
  };

  const markAllRead = async () => {
    await notificationService.markAllRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    setUnreadCount(0);
  };

  return (
    <NotificationContext.Provider value={{ notifications, unreadCount, refresh, markRead, markAllRead }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error("useNotifications must be used within a NotificationProvider");
  return ctx;
}
