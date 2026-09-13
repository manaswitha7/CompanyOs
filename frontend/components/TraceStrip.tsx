type TraceStripProps = {
  sourceCount: number;
  chunkCount: number;
  model?: string;
};

const NODES = ["Retrieved", "Ranked", "Generated", "Cited"] as const;

export function TraceStrip({ sourceCount, chunkCount, model = "gemini" }: TraceStripProps) {
  return (
    <div className="flex flex-wrap items-center gap-x-1 gap-y-2 border-t border-paper-line bg-paper px-6 py-3 font-mono text-[11px] text-graphite-muted">
      <span className="mr-2 text-graphite-muted/70">trace</span>

      {NODES.map((node, index) => (
        <span key={node} className="flex items-center gap-1">
          <span className="rounded border border-paper-line bg-paper-raised px-2 py-1 text-graphite">
            {node}
          </span>
          {index < NODES.length - 1 && <span className="text-signal">&rarr;</span>}
        </span>
      ))}

      <span className="ml-3 text-graphite-muted/70">
        {chunkCount} chunks &middot; {sourceCount} {sourceCount === 1 ? "source" : "sources"} &middot; {model}
      </span>
    </div>
  );
}
