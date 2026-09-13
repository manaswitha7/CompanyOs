"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";

import {
  getSystemStats,
  getIngestionStats,
  getDocuments,
} from "@/lib/api";

import type {
  SystemStats,
  IngestionStats,
  DocumentItem,
} from "@/lib/types";

export default function DataPage() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [ingestion, setIngestion] =
    useState<IngestionStats | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>(
    []
  );

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    setError("");

    try {
      const [statsData, ingestionData, documentsData] =
        await Promise.all([
          getSystemStats(),
          getIngestionStats(),
          getDocuments(),
        ]);

      setStats(statsData);
      setIngestion(ingestionData);
      setDocuments(documentsData.documents);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load data overview."
      );
    } finally {
      setLoading(false);
    }
  }

  const cards = [
    { label: "Total documents", value: stats?.total_documents },
    { label: "Completed", value: stats?.completed_documents },
    { label: "Processing", value: stats?.processing_documents },
    { label: "Queued", value: stats?.queued_documents },
    { label: "Failed", value: stats?.failed_documents },
  ];

  return (
    <AppShell>
      <div className="min-h-full bg-[#09090b] text-white">
        <div className="mx-auto max-w-[1200px] px-6 py-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">Data</h1>
              <p className="mt-1 text-sm text-zinc-400">
                Document ingestion &amp; system status
              </p>
            </div>

            <button
              onClick={load}
              className="rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-zinc-200 transition hover:bg-white/[0.08]"
            >
              Refresh
            </button>
          </div>

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-300">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex min-h-[200px] items-center justify-center text-sm text-zinc-400">
              Loading data overview...
            </div>
          ) : (
            <div className="space-y-8">
              <div>
                <h2 className="mb-3 text-sm font-medium text-zinc-300">
                  Documents
                </h2>
                <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
                  {cards.map((card) => (
                    <div
                      key={card.label}
                      className="rounded-xl border border-white/10 bg-white/[0.03] p-5"
                    >
                      <div className="text-sm text-zinc-400">
                        {card.label}
                      </div>
                      <div className="mt-3 text-2xl font-semibold text-white">
                        {typeof card.value === "number"
                          ? card.value
                          : "—"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {ingestion && (
                <div>
                  <h2 className="mb-3 text-sm font-medium text-zinc-300">
                    Ingestion queue
                  </h2>
                  <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                    <StatCard
                      label="Queued"
                      value={ingestion.queued}
                    />
                    <StatCard
                      label="Processing"
                      value={ingestion.processing}
                    />
                    <StatCard
                      label="Completed"
                      value={ingestion.completed}
                    />
                    <StatCard
                      label="Failed"
                      value={ingestion.failed}
                    />
                  </div>
                </div>
              )}

              <div>
                <h2 className="mb-3 text-sm font-medium text-zinc-300">
                  Recent documents
                </h2>

                {documents.length === 0 ? (
                  <div className="rounded-xl border border-dashed border-white/10 p-10 text-center text-sm text-zinc-400">
                    No documents uploaded yet.
                  </div>
                ) : (
                  <div className="overflow-hidden rounded-xl border border-white/10">
                    <table className="w-full text-left text-sm">
                      <thead className="border-b border-white/10 bg-white/[0.03]">
                        <tr>
                          <th className="px-5 py-3 font-medium text-zinc-400">
                            Filename
                          </th>
                          <th className="px-5 py-3 font-medium text-zinc-400">
                            Type
                          </th>
                          <th className="px-5 py-3 font-medium text-zinc-400">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {documents.slice(0, 25).map((doc) => (
                          <tr
                            key={doc.document_id}
                            className="border-b border-white/[0.06] last:border-0 hover:bg-white/[0.025]"
                          >
                            <td className="px-5 py-4 text-zinc-100">
                              {doc.filename}
                            </td>
                            <td className="px-5 py-4 text-zinc-300">
                              {doc.file_type}
                            </td>
                            <td className="px-5 py-4 text-zinc-300">
                              {doc.status}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

function StatCard({
  label,
  value,
}: {
  label: string;
  value: number | undefined;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-5">
      <div className="text-sm text-zinc-400">{label}</div>
      <div className="mt-3 text-2xl font-semibold text-white">
        {typeof value === "number" ? value : "—"}
      </div>
    </div>
  );
}
