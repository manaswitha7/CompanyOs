"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";

import {
  getCurrentUser,
  getCompanies,
  getPeople,
  getProjects,
  getTasks,
} from "@/lib/api";

import type {
  Company,
  Person,
  Project,
  Task,
} from "@/lib/types";

// ============================================================
// NOTE
// ============================================================
//
// The backend's /crm router does NOT expose /crm/companies,
// /crm/people, /crm/projects, /crm/tasks, /crm/deals or
// /crm/tickets (those paths don't exist). It only exposes
// generic relationships between existing objects
// (/crm/relationships, /crm/object-types). The actual company,
// people and project records live under /organization/*, and
// tasks under /tasks. Deals and tickets have database models
// but no API routes yet, so those tabs are shown as
// "not available" rather than silently failing.
// ============================================================

type Tab =
  | "overview"
  | "companies"
  | "people"
  | "projects"
  | "tasks"
  | "deals"
  | "tickets";

const tabs: { id: Tab; label: string; available: boolean }[] = [
  { id: "overview", label: "Overview", available: true },
  { id: "companies", label: "Companies", available: true },
  { id: "people", label: "People", available: true },
  { id: "projects", label: "Projects", available: true },
  { id: "tasks", label: "Tasks", available: true },
  { id: "deals", label: "Deals", available: false },
  { id: "tickets", label: "Tickets", available: false },
];

type CRMData = {
  companies: Company[];
  people: Person[];
  projects: Project[];
  tasks: Task[];
};

export default function CRMPage() {
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  const [data, setData] = useState<CRMData>({
    companies: [],
    people: [],
    projects: [],
    tasks: [],
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadCRMData();
  }, []);

  async function loadCRMData() {
    setLoading(true);
    setError("");

    try {
      const user = await getCurrentUser();

      if (user.workspace_id == null) {
        throw new Error(
          "Your account is not assigned to a workspace."
        );
      }

      const [companies, people, projects, tasks] =
        await Promise.all([
          getCompanies(user.workspace_id),
          getPeople(user.workspace_id),
          getProjects(user.workspace_id),
          getTasks(),
        ]);

      setData({ companies, people, projects, tasks });
    } catch (err) {
      console.error(err);
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load CRM data. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  function renderOverview() {
    const cards: { label: string; value: number; tab: Tab }[] = [
      { label: "Companies", value: data.companies.length, tab: "companies" },
      { label: "People", value: data.people.length, tab: "people" },
      { label: "Projects", value: data.projects.length, tab: "projects" },
      { label: "Tasks", value: data.tasks.length, tab: "tasks" },
    ];

    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-white">
            CRM Overview
          </h2>

          <p className="mt-1 text-sm text-zinc-400">
            Manage your company relationships, projects and
            operational work.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {cards.map((card) => (
            <button
              key={card.label}
              onClick={() => setActiveTab(card.tab)}
              className="rounded-xl border border-white/10 bg-white/[0.03] p-5 text-left transition hover:border-white/20 hover:bg-white/[0.06]"
            >
              <div className="text-sm text-zinc-400">
                {card.label}
              </div>

              <div className="mt-3 text-3xl font-semibold text-white">
                {card.value}
              </div>
            </button>
          ))}
        </div>

        <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-6">
          <h3 className="text-sm font-medium text-amber-200">
            Deals &amp; Tickets not yet available
          </h3>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-amber-200/70">
            The backend has database models for deals and
            tickets but no API routes exposing them yet. Add
            routes under a new /deals and /tickets router (or
            extend /crm) to light these tabs up.
          </p>
        </div>
      </div>
    );
  }

  function getTitle() {
    return tabs.find((tab) => tab.id === activeTab)?.label || "CRM";
  }

  function renderTable(rows: Record<string, unknown>[], emptyLabel: string) {
    if (!rows.length) {
      return (
        <div className="rounded-xl border border-dashed border-white/10 p-10 text-center">
          <div className="text-sm text-zinc-400">
            No {emptyLabel} found.
          </div>
        </div>
      );
    }

    const columns = Object.keys(rows[0]).filter(
      (key) => !["created_at", "updated_at", "workspace_id"].includes(key)
    );

    return (
      <div className="overflow-hidden rounded-xl border border-white/10">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-white/10 bg-white/[0.03]">
              <tr>
                {columns.slice(0, 6).map((column) => (
                  <th
                    key={column}
                    className="px-5 py-3 font-medium text-zinc-400"
                  >
                    {formatColumn(column)}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {rows.map((row, index) => (
                <tr
                  key={(row.id as number) ?? index}
                  className="border-b border-white/[0.06] last:border-0 hover:bg-white/[0.025]"
                >
                  {columns.slice(0, 6).map((column) => (
                    <td
                      key={column}
                      className="max-w-[280px] truncate px-5 py-4 text-zinc-200"
                    >
                      {formatValue(row[column])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  function formatColumn(value: string) {
    return value
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  function formatValue(value: unknown) {
    if (value === null || value === undefined) {
      return "—";
    }

    if (typeof value === "object") {
      return JSON.stringify(value);
    }

    return String(value);
  }

  function renderActiveContent() {
    if (activeTab === "overview") {
      return renderOverview();
    }

    const tab = tabs.find((t) => t.id === activeTab);

    if (tab && !tab.available) {
      return (
        <div className="rounded-xl border border-dashed border-white/10 p-10 text-center">
          <div className="text-sm text-zinc-400">
            {tab.label} isn&apos;t wired up on the backend yet.
          </div>
        </div>
      );
    }

    const rows =
      activeTab === "companies"
        ? (data.companies as unknown as Record<string, unknown>[])
        : activeTab === "people"
        ? (data.people as unknown as Record<string, unknown>[])
        : activeTab === "projects"
        ? (data.projects as unknown as Record<string, unknown>[])
        : activeTab === "tasks"
        ? (data.tasks as unknown as Record<string, unknown>[])
        : [];

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">
              {getTitle()}
            </h2>

            <p className="mt-1 text-sm text-zinc-400">
              {rows.length} records
            </p>
          </div>

          <button
            onClick={loadCRMData}
            className="rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-zinc-200 transition hover:bg-white/[0.08]"
          >
            Refresh
          </button>
        </div>

        {renderTable(rows, activeTab)}
      </div>
    );
  }

  return (
    <AppShell>
      <div className="min-h-full bg-[#09090b] text-white">
        <div className="mx-auto max-w-[1600px] px-6 py-6">
          <div className="mb-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.05]">
                <span className="text-lg">⌘</span>
              </div>

              <div>
                <h1 className="text-2xl font-semibold">CRM</h1>

                <p className="text-sm text-zinc-400">
                  Company relationships and operational context
                </p>
              </div>
            </div>
          </div>

          <div className="mb-7 overflow-x-auto">
            <div className="flex min-w-max gap-1 rounded-xl border border-white/10 bg-white/[0.025] p-1">
              {tabs.map((tab) => {
                const active = activeTab === tab.id;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={[
                      "rounded-lg px-4 py-2 text-sm transition",
                      active
                        ? "bg-white/10 text-white"
                        : "text-zinc-400 hover:bg-white/[0.05] hover:text-zinc-200",
                      !tab.available ? "opacity-50" : "",
                    ].join(" ")}
                  >
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-300">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex min-h-[300px] items-center justify-center">
              <div className="text-sm text-zinc-400">Loading CRM...</div>
            </div>
          ) : (
            renderActiveContent()
          )}
        </div>
      </div>
    </AppShell>
  );
}
