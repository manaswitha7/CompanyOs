"use client";

import { createContext, useCallback, useContext, useState } from "react";

type ToastKind = "success" | "error";
type ToastItem = { id: number; message: string; kind: ToastKind };
type ToastContextValue = { showToast: (message: string, kind?: ToastKind) => void };

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within <ToastProvider>");
  return ctx;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const showToast = useCallback((message: string, kind: ToastKind = "success") => {
    const id = Date.now() + Math.random();
    setToasts((current) => [...current, { id, message, kind }]);
    setTimeout(() => {
      setToasts((current) => current.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="status"
            className={`flex items-center gap-2.5 rounded-lg border bg-ink px-4 py-3 font-mono text-xs shadow-xl ${
              toast.kind === "success"
                ? "border-status-done text-white"
                : "border-status-failed text-white"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                toast.kind === "success" ? "bg-status-done" : "bg-status-failed"
              }`}
              style={{
                background: toast.kind === "success" ? "var(--status-done)" : "var(--status-failed)",
              }}
            />
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
