import React, { useEffect } from "react";
import { createPortal } from "react-dom";
import { FiX } from "react-icons/fi";

export function Modal({ open, onClose, title, children, footer, size = "md" }) {
  useEffect(() => {
    function onKeyDown(e) {
      if (e.key === "Escape") onClose?.();
    }
    if (open) document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  const widths = { sm: "max-w-sm", md: "max-w-lg", lg: "max-w-2xl", xl: "max-w-4xl" };

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="absolute inset-0 bg-ink-900/40 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={`relative w-full ${widths[size]} card animate-slide-up max-h-[90vh] flex flex-col`}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/[0.06] dark:border-white/[0.06]">
          <h2 className="font-display font-semibold text-base">{title}</h2>
          <button
            onClick={onClose}
            aria-label="Close dialog"
            className="rounded-md p-1.5 text-ink-400 hover:bg-ink-50 dark:hover:bg-white/5"
          >
            <FiX size={18} />
          </button>
        </div>
        <div className="px-5 py-4 overflow-y-auto">{children}</div>
        {footer && (
          <div className="px-5 py-3 border-t border-black/[0.06] dark:border-white/[0.06] flex justify-end gap-2">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}
