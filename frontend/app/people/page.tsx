"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";

import { getCurrentUser, getPeople } from "@/lib/api";
import type { Person } from "@/lib/types";

export default function PeoplePage() {
  const [people, setPeople] = useState<Person[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

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

      const data = await getPeople(user.workspace_id);
      setPeople(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load people."
      );
    } finally {
      setLoading(false);
    }
  }

  const filtered = people.filter(
    (person) =>
      person.name
        .toLowerCase()
        .includes(search.toLowerCase()) ||
      person.email
        ?.toLowerCase()
        .includes(search.toLowerCase()) ||
      person.role
        ?.toLowerCase()
        .includes(search.toLowerCase())
  );

  return (
    <AppShell>
      <div className="min-h-full bg-[#09090b] text-white">
        <div className="mx-auto max-w-[1200px] px-6 py-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">People</h1>
              <p className="mt-1 text-sm text-zinc-400">
                {people.length} people across your workspace
              </p>
            </div>

            <button
              onClick={load}
              className="rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-zinc-200 transition hover:bg-white/[0.08]"
            >
              Refresh
            </button>
          </div>

          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, email, or role..."
            className="mb-6 w-full max-w-md rounded-lg border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm text-white placeholder:text-zinc-500 focus:border-white/20 focus:outline-none"
          />

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-300">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex min-h-[200px] items-center justify-center text-sm text-zinc-400">
              Loading people...
            </div>
          ) : filtered.length === 0 ? (
            <div className="rounded-xl border border-dashed border-white/10 p-10 text-center text-sm text-zinc-400">
              No people found.
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-white/10">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-white/10 bg-white/[0.03]">
                  <tr>
                    <th className="px-5 py-3 font-medium text-zinc-400">
                      Name
                    </th>
                    <th className="px-5 py-3 font-medium text-zinc-400">
                      Email
                    </th>
                    <th className="px-5 py-3 font-medium text-zinc-400">
                      Role
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((person) => (
                    <tr
                      key={person.id}
                      className="border-b border-white/[0.06] last:border-0 hover:bg-white/[0.025]"
                    >
                      <td className="px-5 py-4 text-zinc-100">
                        {person.name}
                      </td>
                      <td className="px-5 py-4 text-zinc-300">
                        {person.email || "—"}
                      </td>
                      <td className="px-5 py-4 text-zinc-300">
                        {person.role || "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
