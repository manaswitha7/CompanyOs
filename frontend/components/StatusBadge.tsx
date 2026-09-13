import type { DocumentStatus } from "@/lib/types";

const CONFIG: Record<DocumentStatus, { label: string; fg: string; bg: string; dot?: boolean }> = {
  queued: { label: "Queued", fg: "var(--status-queued)", bg: "var(--status-queued-bg)" },
  processing: { label: "Processing", fg: "var(--status-processing)", bg: "var(--status-processing-bg)", dot: true },
  completed: { label: "Completed", fg: "var(--status-done)", bg: "var(--status-done-bg)" },
  failed: { label: "Failed", fg: "var(--status-failed)", bg: "var(--status-failed-bg)" },
};

export function StatusBadge({ status }: { status: DocumentStatus }) {
  const config = CONFIG[status];

  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-mono text-[11px] font-medium"
      style={{ color: config.fg, background: config.bg }}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${config.dot ? "animate-pulse" : ""}`}
        style={{ background: config.fg }}
      />
      {config.label}
    </span>
  );
}
