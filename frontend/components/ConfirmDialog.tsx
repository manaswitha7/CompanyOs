"use client";

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 px-6 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
    >
      <div className="w-full max-w-sm rounded-xl border border-paper-line bg-paper-raised p-6 shadow-2xl">
        <h3 className="font-display text-lg font-semibold text-graphite">{title}</h3>
        <p className="mt-2 text-sm text-graphite-muted">{description}</p>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-paper-line px-4 py-2 text-sm font-medium text-graphite hover:bg-paper"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="rounded-lg px-4 py-2 text-sm font-medium text-white"
            style={{ background: "var(--status-failed)" }}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
