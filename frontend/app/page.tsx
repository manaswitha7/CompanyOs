"use client";

import { useEffect, useState } from "react";
import {
  Search,
  Sparkles,
  FileText,
  Loader2,
  GitBranch,
  MessageSquare,
  HardDrive,
  Cable,
  Building2,
  CheckCircle2,
  FolderKanban,
  DollarSign,
  Ticket,
  ThumbsUp,
  RefreshCw,
} from "lucide-react";

import Link from "next/link";

import AppShell from "@/components/AppShell";

import {
  ApiError,
  askQuestion,
  getCurrentUser,
  getDocuments,
  getWorkspaceAnalytics,
} from "@/lib/api";

import type {
  ChatResponse,
  CurrentUser,
  DocumentItem,
} from "@/lib/types";

/* ============================================================ */
/* TYPES */
/* ============================================================ */

type WorkspaceAnalytics = {
  workspace_id: number;

  tasks: {
    total: number;
    [key: string]: number;
  };

  projects: {
    total: number;
    [key: string]: number;
  };

  deals: {
    total: number;
    total_value: number;
    [key: string]: number;
  };

  tickets: {
    total: number;
    [key: string]: number;
  };

  documents: {
    total: number;
    [key: string]: number;
  };

  feedback: {
    total: number;
    average_rating: number;
    [key: string]: number;
  };
};


/* ============================================================ */
/* HOME PAGE */
/* ============================================================ */

export default function HomePage() {

  const [question, setQuestion] = useState("");

  const [loading, setLoading] =
    useState(false);

  const [answer, setAnswer] =
    useState<ChatResponse | null>(null);

  const [error, setError] =
    useState("");

  const [documents, setDocuments] =
    useState<DocumentItem[]>([]);

  const [selectedDocument, setSelectedDocument] =
    useState<number | null>(null);

  /* ========================================================== */
  /* WORKSPACE ANALYTICS */
  /* ========================================================== */

  const [analytics, setAnalytics] =
    useState<WorkspaceAnalytics | null>(null);

  const [analyticsLoading, setAnalyticsLoading] =
    useState(true);

  const [analyticsError, setAnalyticsError] =
    useState("");

  const [currentUser, setCurrentUser] =
    useState<CurrentUser | null>(null);


  /* ========================================================== */
  /* LOAD CURRENT USER */
  /* ========================================================== */

  async function loadCurrentUser() {

    try {

      const user = await getCurrentUser();

      setCurrentUser(user);

      return user;

    } catch {

      return null;

    }

  }


  /* ========================================================== */
  /* LOAD DOCUMENTS */
  /* ========================================================== */

  async function loadDocuments() {

    try {

      const response =
        await getDocuments();

      setDocuments(
        response.documents
      );

    } catch {

      // Don't block chat if document loading fails.

    }

  }


  /* ========================================================== */
  /* LOAD WORKSPACE ANALYTICS */
  /* ========================================================== */

  async function loadWorkspaceAnalytics() {

    setAnalyticsLoading(true);
    setAnalyticsError("");

    try {

      // The workspace id used to be a hardcoded constant (1)
      // regardless of who was logged in — every user saw
      // workspace 1's analytics. Use the real user's
      // workspace instead.
      const user =
        currentUser || (await loadCurrentUser());

      if (!user || user.workspace_id == null) {

        throw new Error(
          "Your account is not assigned to a workspace."
        );

      }

      const response =
        await getWorkspaceAnalytics(
          user.workspace_id
        );

      setAnalytics(
        response as WorkspaceAnalytics
      );

    } catch (err) {

      if (err instanceof ApiError) {

        setAnalyticsError(
          err.message
        );

      } else if (err instanceof Error) {

        setAnalyticsError(
          err.message
        );

      } else {

        setAnalyticsError(
          "Unable to load workspace analytics."
        );

      }

    } finally {

      setAnalyticsLoading(false);

    }

  }


  /* ========================================================== */
  /* INITIAL LOAD */
  /* ========================================================== */

  useEffect(() => {

    loadWorkspaceAnalytics();

  }, []);


  /* ========================================================== */
  /* ASK QUESTION */
  /* ========================================================== */

  async function handleAsk() {

    const trimmed =
      question.trim();

    if (!trimmed) {

      return;

    }

    setLoading(true);
    setError("");
    setAnswer(null);

    try {

      const response =
        await askQuestion(
          trimmed,
          5,
          selectedDocument
        );

      setAnswer(response);

    } catch (err) {

      if (err instanceof ApiError) {

        setError(
          err.message
        );

      } else {

        setError(
          "Unable to get an answer from Company OS."
        );

      }

    } finally {

      setLoading(false);

    }

  }


  return (

    <AppShell>

      <main className="min-h-[calc(100vh-76px)] bg-[#f8f9fc]">

        <div className="mx-auto max-w-[1180px] px-10 py-12">


          {/* ================================================= */}
          {/* HERO */}
          {/* ================================================= */}

          <div className="mb-10">

            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-[#dddfff] bg-[#f1f2ff] px-4 py-2 text-xs font-medium uppercase tracking-[0.12em] text-[#5b5cf6]">

              <Sparkles size={14} />

              Grounded AI

            </div>


            <h1 className="text-[48px] font-semibold leading-[1.05] tracking-[-0.035em] text-[#111827]">

              Ask your company.

            </h1>


            <p className="mt-5 max-w-[720px] text-[18px] leading-8 text-[#697386]">

              Search across your company knowledge base and get
              answers grounded in your documents, with
              traceable citations.

            </p>

          </div>


          {/* ================================================= */}
          {/* WORKSPACE OVERVIEW */}
          {/* ================================================= */}

          <section className="mb-10">

            <div className="mb-5 flex items-center justify-between">

              <div>

                <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.14em] text-[#8992a3]">

                  <Building2 size={14} />

                  Active Workspace

                </div>

                <h2 className="mt-2 text-2xl font-semibold tracking-[-0.02em] text-[#111827]">

                  {currentUser?.workspace_name ||
                    (currentUser?.workspace_id != null
                      ? `Workspace ${currentUser.workspace_id}`
                      : "Loading workspace...")}

                </h2>

              </div>


              <div className="flex items-center gap-3">

                <button
                  type="button"
                  onClick={loadWorkspaceAnalytics}
                  disabled={analyticsLoading}
                  className="flex items-center gap-2 rounded-xl border border-[#e1e4eb] bg-white px-4 py-2.5 text-sm font-medium text-[#4b5563] transition hover:border-[#cfd3ff] hover:text-[#5b5cf6] disabled:cursor-not-allowed disabled:opacity-50"
                >

                  <RefreshCw
                    size={15}
                    className={
                      analyticsLoading
                        ? "animate-spin"
                        : ""
                    }
                  />

                  Refresh

                </button>


                <Link
                  href="/workspaces"
                  className="rounded-xl bg-[#111827] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[#1f2937]"
                >
                  Workspace
                </Link>

              </div>

            </div>


            {/* ANALYTICS ERROR */}

            {analyticsError && (

              <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

                {analyticsError}

              </div>

            )}


            {/* ANALYTICS CARDS */}

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">

              {/* TASKS */}

              <AnalyticsCard
                icon={<CheckCircle2 size={19} />}
                label="Tasks"
                value={
                  analyticsLoading
                    ? "—"
                    : String(
                        analytics?.tasks.total ?? 0
                      )
                }
                description="Total tasks"
              />


              {/* PROJECTS */}

              <AnalyticsCard
                icon={<FolderKanban size={19} />}
                label="Projects"
                value={
                  analyticsLoading
                    ? "—"
                    : String(
                        analytics?.projects.total ?? 0
                      )
                }
                description="Active workspace"
              />


              {/* DEALS */}

              <AnalyticsCard
                icon={<DollarSign size={19} />}
                label="Deals"
                value={
                  analyticsLoading
                    ? "—"
                    : String(
                        analytics?.deals.total ?? 0
                      )
                }
                description={
                  analyticsLoading
                    ? "Loading..."
                    : `$${Number(
                        analytics?.deals.total_value ?? 0
                      ).toLocaleString()} value`
                }
              />


              {/* TICKETS */}

              <AnalyticsCard
                icon={<Ticket size={19} />}
                label="Tickets"
                value={
                  analyticsLoading
                    ? "—"
                    : String(
                        analytics?.tickets.total ?? 0
                      )
                }
                description="Total tickets"
              />


              {/* DOCUMENTS */}

              <AnalyticsCard
                icon={<FileText size={19} />}
                label="Documents"
                value={
                  analyticsLoading
                    ? "—"
                    : String(
                        analytics?.documents.total ?? 0
                      )
                }
                description="Knowledge sources"
              />

            </div>


            {/* AI FEEDBACK */}

            {analytics && (

              <div className="mt-4 rounded-2xl border border-[#e1e4eb] bg-white p-5 shadow-[0_6px_24px_rgba(15,23,42,0.04)]">

                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                  <div className="flex items-center gap-3">

                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#eef0ff]">

                      <ThumbsUp
                        size={18}
                        className="text-[#5b5cf6]"
                      />

                    </div>

                    <div>

                      <div className="text-sm font-semibold text-[#111827]">

                        AI Feedback

                      </div>

                      <div className="text-xs text-[#8992a3]">

                        User feedback across this workspace

                      </div>

                    </div>

                  </div>


                  <div className="flex items-center gap-6">

                    <div>

                      <div className="text-lg font-semibold text-[#111827]">

                        {analytics.feedback.total}

                      </div>

                      <div className="text-[11px] uppercase tracking-wide text-[#9aa2b1]">

                        Responses

                      </div>

                    </div>


                    <div>

                      <div className="text-lg font-semibold text-[#111827]">

                        {analytics.feedback.average_rating.toFixed(
                          1
                        )}

                        /5

                      </div>

                      <div className="text-[11px] uppercase tracking-wide text-[#9aa2b1]">

                        Average rating

                      </div>

                    </div>

                  </div>

                </div>

              </div>

            )}

          </section>


          {/* ================================================= */}
          {/* SEARCH CARD */}
          {/* ================================================= */}

          <div className="overflow-hidden rounded-2xl border border-[#e1e4eb] bg-white shadow-[0_12px_40px_rgba(15,23,42,0.06)]">

            {/* SEARCH HEADER */}

            <div className="flex items-center justify-between border-b border-[#edf0f4] px-6 py-4">

              <div className="flex items-center gap-3">

                <Search
                  size={19}
                  className="text-[#7b8497]"
                />

                <span className="font-mono text-xs uppercase tracking-[0.12em] text-[#6f7788]">

                  Knowledge search

                </span>

              </div>


              <select
                value={selectedDocument ?? ""}
                onChange={(event) => {

                  const value =
                    event.target.value;

                  setSelectedDocument(
                    value
                      ? Number(value)
                      : null
                  );

                }}
                onFocus={loadDocuments}
                className="rounded-xl border border-[#e1e4eb] bg-white px-4 py-2.5 text-sm text-[#4b5563] outline-none transition focus:border-[#5b5cf6]"
              >

                <option value="">
                  All documents
                </option>

                {documents.map(
                  (document) => (

                    <option
                      key={
                        document.document_id
                      }
                      value={
                        document.document_id
                      }
                    >
                      {document.filename}
                    </option>

                  )
                )}

              </select>

            </div>


            {/* QUESTION */}

            <div className="p-6">

              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }
                onKeyDown={(event) => {

                  if (
                    event.key === "Enter" &&
                    !event.shiftKey
                  ) {

                    event.preventDefault();

                    handleAsk();

                  }

                }}
                placeholder="Ask anything about your company..."
                rows={7}
                disabled={loading}
                className="w-full resize-none border-none bg-transparent text-[20px] leading-8 text-[#111827] outline-none placeholder:text-[#a4adbd] disabled:opacity-60"
              />


              {/* SEARCH FOOTER */}

              <div className="mt-5 flex items-center justify-between border-t border-[#edf0f4] pt-5">

                <div className="flex items-center gap-3 text-xs text-[#8992a3]">

                  <span className="font-mono">
                    HYBRID SEARCH
                  </span>

                  <span>•</span>

                  <span className="font-mono">
                    GEMINI
                  </span>

                  <span>•</span>

                  <span className="font-mono">
                    CITED
                  </span>

                </div>


                <button
                  type="button"
                  onClick={handleAsk}
                  disabled={
                    loading ||
                    !question.trim()
                  }
                  className="flex items-center gap-2 rounded-xl bg-[#111827] px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/10 transition hover:-translate-y-0.5 hover:bg-[#1f2937] disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:translate-y-0"
                >

                  {loading ? (

                    <>

                      <Loader2
                        size={16}
                        className="animate-spin"
                      />

                      Thinking...

                    </>

                  ) : (

                    "Ask"

                  )}

                </button>

              </div>

            </div>

          </div>


          {/* ================================================= */}
          {/* ERROR */}
          {/* ================================================= */}

          {error && (

            <div className="mt-5 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

              {error}

            </div>

          )}


          {/* ================================================= */}
          {/* ANSWER */}
          {/* ================================================= */}

          {answer && (

            <div className="mt-8 overflow-hidden rounded-2xl border border-[#e1e4eb] bg-white shadow-[0_8px_30px_rgba(15,23,42,0.04)]">

              <div className="border-b border-[#edf0f4] px-6 py-4">

                <div className="flex items-center gap-2 text-sm font-semibold text-[#111827]">

                  <Sparkles
                    size={16}
                    className="text-[#5b5cf6]"
                  />

                  Company OS answer

                </div>

              </div>


              <div className="px-6 py-7">

                <div className="whitespace-pre-wrap text-[16px] leading-8 text-[#374151]">

                  {answer.answer}

                </div>


                {/* CITATIONS */}

                {answer.citations?.length > 0 && (

                  <div className="mt-8 border-t border-[#edf0f4] pt-6">

                    <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.12em] text-[#8992a3]">

                      Sources

                    </div>


                    <div className="grid gap-3 sm:grid-cols-2">

                      {answer.citations.map(
                        (
                          citation,
                          index
                        ) => (

                          <div
                            key={`${citation.chunk_id}-${index}`}
                            className="flex items-center gap-3 rounded-xl border border-[#e5e8ee] bg-[#fafbfc] px-4 py-3"
                          >

                            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#eef0ff]">

                              <FileText
                                size={16}
                                className="text-[#5b5cf6]"
                              />

                            </div>


                            <div className="min-w-0">

                              <div className="truncate text-sm font-medium text-[#374151]">

                                {citation.filename}

                              </div>


                              <div className="mt-0.5 text-xs text-[#8b93a3]">

                                {citation.page_number
                                  ? `Page ${citation.page_number}`
                                  : "Document source"}

                              </div>

                            </div>

                          </div>

                        )
                      )}

                    </div>

                  </div>

                )}


                {/* METRICS */}

                {answer.metrics && (

                  <div className="mt-6 flex flex-wrap gap-2">

                    <Metric
                      label="Retrieved"
                      value={`${answer.metrics.retrieved_chunks ?? 0} chunks`}
                    />

                    <Metric
                      label="Citations"
                      value={`${answer.metrics.citation_count ?? 0}`}
                    />

                    <Metric
                      label="Latency"
                      value={`${Math.round(
                        answer.metrics
                          .total_latency_ms ?? 0
                      )} ms`}
                    />

                  </div>

                )}

              </div>

            </div>

          )}


          {/* ================================================= */}
          {/* EMPTY STATE */}
          {/* ================================================= */}

          {!answer && !error && (

            <div className="mt-8 rounded-2xl border border-dashed border-[#d9dde6] bg-white/50 px-8 py-14 text-center">

              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[#eef0ff]">

                <Search
                  size={21}
                  className="text-[#5b5cf6]"
                />

              </div>


              <h2 className="text-sm font-semibold text-[#374151]">

                Ask a question to search your knowledge base

              </h2>


              <p className="mt-2 text-sm text-[#8a93a4]">

                Company OS will retrieve relevant documents
                and return a cited answer.

              </p>

            </div>

          )}


          {/* ================================================= */}
          {/* SERVICES / INTEGRATIONS */}
          {/* ================================================= */}

          <div className="mt-12">

            <div className="mb-6">

              <div className="font-mono text-[11px] uppercase tracking-[0.14em] text-[#8992a3]">

                Services / Integrations

              </div>


              <h2 className="mt-2 text-2xl font-semibold tracking-[-0.02em] text-[#111827]">

                Connect your company tools

              </h2>


              <p className="mt-2 max-w-[700px] text-sm leading-6 text-[#697386]">

                Bring your external company data into Company OS
                and make it available across your knowledge,
                search and AI workflows.

              </p>

            </div>


            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">


              {/* CONNECTORS */}

              <IntegrationCard
                href="/connectors"
                icon={
                  <Cable
                    size={21}
                    className="text-[#5b5cf6]"
                  />
                }
                iconBackground="bg-[#eef0ff]"
                badge="Integrations"
                title="Connectors"
                description="Connect GitHub, Slack, Google Drive, Jira and other external company data sources."
                action="Manage connectors →"
              />


              {/* GITHUB */}

              <IntegrationCard
                href="/connectors"
                icon={
                  <GitBranch
                    size={22}
                    className="text-[#111827]"
                  />
                }
                iconBackground="bg-[#f3f4f6]"
                title="GitHub"
                description="Connect repositories and bring engineering knowledge into Company OS."
                action="Configure →"
              />


              {/* SLACK */}

              <IntegrationCard
                href="/connectors"
                icon={
                  <MessageSquare
                    size={22}
                    className="text-[#7c3aed]"
                  />
                }
                iconBackground="bg-[#f8f1ff]"
                title="Slack"
                description="Bring team conversations, decisions and communication into the company knowledge layer."
                action="Coming soon →"
              />


              {/* GOOGLE DRIVE */}

              <IntegrationCard
                href="/connectors"
                icon={
                  <HardDrive
                    size={21}
                    className="text-[#2563eb]"
                  />
                }
                iconBackground="bg-[#eff6ff]"
                title="Google Drive"
                description="Connect company documents and files stored in Google Drive."
                action="Coming soon →"
              />


              {/* DOCUMENTS */}

              <IntegrationCard
                href="/documents"
                icon={
                  <FileText
                    size={21}
                    className="text-[#5b5cf6]"
                  />
                }
                iconBackground="bg-[#eef0ff]"
                title="Documents"
                description="Upload and manage company documents that power the Company OS knowledge base."
                action="Manage documents →"
              />

            </div>

          </div>

        </div>

      </main>

    </AppShell>

  );
}


/* ============================================================ */
/* ANALYTICS CARD */
/* ============================================================ */

function AnalyticsCard({
  icon,
  label,
  value,
  description,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  description: string;
}) {

  return (

    <div className="rounded-2xl border border-[#e1e4eb] bg-white p-5 shadow-[0_6px_24px_rgba(15,23,42,0.04)]">

      <div className="flex items-center justify-between">

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#eef0ff] text-[#5b5cf6]">

          {icon}

        </div>

        <span className="h-2 w-2 rounded-full bg-emerald-400" />

      </div>


      <div className="mt-5">

        <div className="text-xs font-medium uppercase tracking-wide text-[#8992a3]">

          {label}

        </div>


        <div className="mt-1 text-3xl font-semibold tracking-tight text-[#111827]">

          {value}

        </div>


        <div className="mt-1 text-xs text-[#9aa2b1]">

          {description}

        </div>

      </div>

    </div>

  );

}


/* ============================================================ */
/* INTEGRATION CARD */
/* ============================================================ */

function IntegrationCard({
  href,
  icon,
  iconBackground,
  badge,
  title,
  description,
  action,
}: {
  href: string;
  icon: React.ReactNode;
  iconBackground: string;
  badge?: string;
  title: string;
  description: string;
  action: string;
}) {

  return (

    <Link
      href={href}
      className="group rounded-2xl border border-[#e1e4eb] bg-white p-6 shadow-[0_6px_24px_rgba(15,23,42,0.04)] transition hover:-translate-y-0.5 hover:border-[#cfd3ff] hover:shadow-[0_12px_30px_rgba(15,23,42,0.07)]"
    >

      <div className="flex items-start justify-between">

        <div
          className={`flex h-11 w-11 items-center justify-center rounded-xl ${iconBackground}`}
        >

          {icon}

        </div>


        {badge && (

          <span className="rounded-full bg-[#eef0ff] px-2.5 py-1 text-[10px] font-medium uppercase tracking-wide text-[#5b5cf6]">

            {badge}

          </span>

        )}

      </div>


      <h3 className="mt-5 text-lg font-semibold text-[#111827]">

        {title}

      </h3>


      <p className="mt-2 text-sm leading-6 text-[#697386]">

        {description}

      </p>


      <div className="mt-5 text-sm font-medium text-[#5b5cf6] transition group-hover:translate-x-1">

        {action}

      </div>

    </Link>

  );

}


/* ============================================================ */
/* METRIC */
/* ============================================================ */

function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (

    <div className="rounded-lg border border-[#e5e8ee] bg-[#fafbfc] px-3 py-2">

      <span className="text-[10px] uppercase tracking-wide text-[#9aa2b1]">

        {label}

      </span>


      <span className="ml-2 text-xs font-medium text-[#4b5563]">

        {value}

      </span>

    </div>

  );

}