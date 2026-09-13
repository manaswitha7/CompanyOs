"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";

import { getCurrentUser, getWorkspaceAnalytics } from "@/lib/api";

type WorkspaceAnalytics = {
  workspace_id: number;
  tasks: { total: number; [key: string]: number };
  projects: { total: number; [key: string]: number };
  deals: {
    total: number;
    total_value: number;
    [key: string]: number;
  };
  tickets: { total: number; [key: string]: number };
  documents: { total: number; [key: string]: number };
  feedback: {
    total: number;
    average_rating: number;
    [key: string]: number;
  };
};

export default function AnalyticsPage() {
  const [analytics, setAnalytics] =
    useState<WorkspaceAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    setError("");

    try {
      const user = await getCurrentUser();

      if (user.workspace_id == null) {
        throw new Error(
          "Your account is not assigned to a workspace."
        );
      }

      const data = await getWorkspaceAnalytics(
        user.workspace_id
      );

      setAnalytics(data as WorkspaceAnalytics);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load analytics."
      );
    } finally {
      setLoading(false);
    }
  }

  const cards = analytics
    ? [
        { label: "Tasks", value: analytics.tasks.total },
        { label: "Projects", value: analytics.projects.total },
        { label: "Deals", value: analytics.deals.total },
        {
          label: "Deal value",
          value: `$${analytics.deals.total_value.toLocaleString()}`,
        },
        { label: "Tickets", value: analytics.tickets.total },
        {
          label: "Documents",
          value: analytics.documents.total,
        },
        {
          label: "Feedback responses",
          value: analytics.feedback.total,
        },
        {
          label: "Avg. rating",
          value: analytics.feedback.average_rating.toFixed(1),
        },
      ]
    : [];

  return (
    <AppShell>
      <div className="min-h-full bg-[#09090b] text-white">
        <div className="mx-auto max-w-[1200px] px-6 py-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">
                Analytics
              </h1>
              <p className="mt-1 text-sm text-zinc-400">
                Workspace activity at a glance
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
              Loading analytics...
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {cards.map((card) => (
                <div
                  key={card.label}
                  className="rounded-xl border border-white/10 bg-white/[0.03] p-5"
                >
                  <div className="text-sm text-zinc-400">
                    {card.label}
                  </div>
                  <div className="mt-3 text-2xl font-semibold text-white">
                    {card.value}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
