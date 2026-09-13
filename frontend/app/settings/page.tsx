"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";

import { getCurrentUser, logout } from "@/lib/api";
import type { CurrentUser } from "@/lib/types";

// ============================================================
// NOTE
// ============================================================
//
// The backend has no settings/preferences endpoints (no
// workspace rename, no notification prefs, no API keys, etc.)
// — only account identity via GET /auth/me. This page shows
// what's actually available rather than mocking controls that
// wouldn't do anything when clicked.
// ============================================================

export default function SettingsPage() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() =>
        setError("Unable to load your account.")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <div className="min-h-full bg-[#09090b] text-white">
        <div className="mx-auto max-w-[720px] px-6 py-6">
          <div className="mb-6">
            <h1 className="text-2xl font-semibold">
              Settings
            </h1>
            <p className="mt-1 text-sm text-zinc-400">
              Your account
            </p>
          </div>

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-300">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex min-h-[200px] items-center justify-center text-sm text-zinc-400">
              Loading account...
            </div>
          ) : (
            user && (
              <div className="space-y-6">
                <div className="rounded-xl border border-white/10 bg-white/[0.03] p-6">
                  <dl className="divide-y divide-white/[0.06]">
                    <Row label="Name" value={user.name} />
                    <Row label="Email" value={user.email} />
                    <Row label="Role" value={user.role} />
                    <Row
                      label="Workspace"
                      value={
                        user.workspace_name ||
                        (user.workspace_id != null
                          ? `Workspace ${user.workspace_id}`
                          : "—")
                      }
                    />
                  </dl>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/[0.03] p-6">
                  <h2 className="text-sm font-medium text-zinc-300">
                    Session
                  </h2>
                  <p className="mt-1 text-sm text-zinc-500">
                    Sign out of this browser.
                  </p>

                  <button
                    onClick={() => logout()}
                    className="mt-4 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-2 text-sm text-red-300 transition hover:bg-red-500/20"
                  >
                    Sign out
                  </button>
                </div>
              </div>
            )
          )}
        </div>
      </div>
    </AppShell>
  );
}

function Row({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
      <dt className="text-sm text-zinc-400">{label}</dt>
      <dd className="text-sm text-zinc-100">{value}</dd>
    </div>
  );
}
