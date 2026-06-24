import React, { createContext, useCallback, useContext, useState } from "react";
import { FiCheckCircle, FiAlertTriangle, FiInfo } from "react-icons/fi";

const ToastContext = createContext(null);

const ICONS = {
  success: <FiCheckCircle className="text-brand" size={18} />,
  error: <FiAlertTriangle className="text-critical" size={18} />,
  info: <FiInfo className="text-ink-400" size={18} />,
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = "info") => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-80">
        {toasts.map((t) => (
          <div key={t.id} className="card flex items-start gap-2 px-4 py-3 animate-slide-up">
            {ICONS[t.type]}
            <p className="text-sm flex-1">{t.message}</p>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within a ToastProvider");
  return ctx;
}
