"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";

import { getCurrentUser, getProjects } from "@/lib/api";
import type { Project } from "@/lib/types";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
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

      const data = await getProjects(user.workspace_id);
      setProjects(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load projects."
      );
    } finally {
      setLoading(false);
    }
  }

  const filtered = projects.filter(
    (project) =>
      project.name
        .toLowerCase()
        .includes(search.toLowerCase()) ||
      project.description
        ?.toLowerCase()
        .includes(search.toLowerCase())
  );

  return (
    <AppShell>
      <div className="min-h-full bg-[#09090b] text-white">
        <div className="mx-auto max-w-[1200px] px-6 py-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">
                Projects
              </h1>
              <p className="mt-1 text-sm text-zinc-400">
                {projects.length} projects across your
                workspace
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
            placeholder="Search projects..."
            className="mb-6 w-full max-w-md rounded-lg border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm text-white placeholder:text-zinc-500 focus:border-white/20 focus:outline-none"
          />

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-300">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex min-h-[200px] items-center justify-center text-sm text-zinc-400">
              Loading projects...
            </div>
          ) : filtered.length === 0 ? (
            <div className="rounded-xl border border-dashed border-white/10 p-10 text-center text-sm text-zinc-400">
              No projects found.
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filtered.map((project) => (
                <div
                  key={project.id}
                  className="rounded-xl border border-white/10 bg-white/[0.03] p-5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-medium text-white">
                      {project.name}
                    </h3>

                    {project.status && (
                      <span className="shrink-0 rounded-full border border-white/10 bg-white/[0.05] px-2.5 py-0.5 text-xs text-zinc-300">
                        {project.status}
                      </span>
                    )}
                  </div>

                  {project.description && (
                    <p className="mt-2 text-sm leading-6 text-zinc-400">
                      {project.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
