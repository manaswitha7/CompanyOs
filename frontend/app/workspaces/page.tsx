"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";

import {
  getCurrentUser,
  getOrganizationOverview,
  getSystemStats,
} from "@/lib/api";

import type {
  CurrentUser,
  OrganizationOverview,
  SystemStats,
} from "@/lib/types";

// ============================================================
// NOTE
// ============================================================
//
// The backend has no multi-workspace listing endpoint (no
// GET /workspaces) — a user belongs to exactly one workspace,
// carried on their own record (current_user.workspace_id).
// So this page shows an overview of *that* workspace rather
// than a switcher between many.
// ============================================================

export default function WorkspacePage() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [overview, setOverview] =
    useState<OrganizationOverview | null>(null);
  const [stats, setStats] = useState<SystemStats | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        setError("");

        const currentUser = await getCurrentUser();

        if (cancelled) return;
        setUser(currentUser);

        if (currentUser.workspace_id == null) {
          throw new Error(
            "Your account is not assigned to a workspace."
          );
        }

        const [overviewData, statsData] = await Promise.all([
          getOrganizationOverview(currentUser.workspace_id),
          getSystemStats(),
        ]);

        if (cancelled) return;

        setOverview(overviewData);
        setStats(statsData);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load workspace."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, []);

  const overviewCards = [
    {
      label: "Companies",
      value:
        overview?.companies?.length ??
        (overview?.["companies_count"] as number | undefined),
    },
    {
      label: "People",
      value:
        overview?.people?.length ??
        (overview?.["people_count"] as number | undefined),
    },
    {
      label: "Projects",
      value:
        overview?.projects?.length ??
        (overview?.["projects_count"] as number | undefined),
    },
    {
      label: "Departments",
      value:
        overview?.departments?.length ??
        (overview?.["departments_count"] as number | undefined),
    },
    {
      label: "Teams",
      value:
        overview?.teams?.length ??
        (overview?.["teams_count"] as number | undefined),
    },
  ];

  return (
    <AppShell>
      <div className="min-h-full bg-[#09090b] text-white">
        <div className="mx-auto max-w-[1200px] px-6 py-6">
          <div className="mb-6">
            <h1 className="text-2xl font-semibold">Workspace</h1>
            <p className="mt-1 text-sm text-zinc-400">
              {user
                ? `Signed in as ${user.name} (${user.email})`
                : "Loading account..."}
            </p>
          </div>

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-300">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex min-h-[200px] items-center justify-center text-sm text-zinc-400">
              Loading workspace...
            </div>
          ) : (
            <div className="space-y-8">
              <div>
                <h2 className="mb-3 text-sm font-medium text-zinc-300">
                  Organization
                </h2>
                <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
                  {overviewCards.map((card) => (
                    <div
                      key={card.label}
                      className="rounded-xl border border-white/10 bg-white/[0.03] p-5"
                    >
                      <div className="text-sm text-zinc-400">
                        {card.label}
                      </div>
                      <div className="mt-3 text-3xl font-semibold text-white">
                        {typeof card.value === "number"
                          ? card.value
                          : "—"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h2 className="mb-3 text-sm font-medium text-zinc-300">
                  System
                </h2>
                <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                  <StatCard
                    label="Documents"
                    value={stats?.total_documents}
                  />
                  <StatCard
                    label="Completed"
                    value={stats?.completed_documents}
                  />
                  <StatCard
                    label="Processing"
                    value={stats?.processing_documents}
                  />
                  <StatCard
                    label="Failed"
                    value={stats?.failed_documents}
                  />
                </div>
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
      <div className="mt-3 text-3xl font-semibold text-white">
        {typeof value === "number" ? value : "—"}
      </div>
    </div>
  );
}
