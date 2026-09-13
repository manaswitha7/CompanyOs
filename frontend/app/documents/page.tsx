"use client";

import {
  Upload,
  FileText,
  Trash2,
  RefreshCw,
  Search,
  CheckCircle2,
  Clock3,
  AlertCircle,
  Database,
} from "lucide-react";

import { useEffect, useState } from "react";

import AppShell from "@/components/AppShell";

import {
  getDocuments,
  uploadDocument,
  deleteDocument,
  ApiError,
} from "@/lib/api";

import type {
  DocumentItem,
} from "@/lib/types";


export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  async function loadDocuments() {
    try {
      setLoading(true);
      setError("");

      const response = await getDocuments();

      setDocuments(response.documents || []);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to load documents.");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleUpload(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    try {
      setUploading(true);
      setError("");

      await uploadDocument(file);

      await loadDocuments();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to upload document.");
      }
    } finally {
      setUploading(false);

      event.target.value = "";
    }
  }

  async function handleDelete(documentId: number) {
    const confirmed = window.confirm(
      "Delete this document?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      await deleteDocument(documentId);

      setDocuments((current) =>
        current.filter(
          (doc) => doc.document_id !== documentId
        )
      );
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to delete document.");
      }
    }
  }

  const filteredDocuments = documents.filter(
    (document) =>
      document.filename
        .toLowerCase()
        .includes(search.toLowerCase())
  );

  const completedCount = documents.filter(
    (doc) => doc.status === "completed"
  ).length;

  const processingCount = documents.filter(
    (doc) =>
      doc.status === "processing" ||
      doc.status === "queued"
  ).length;

  const failedCount = documents.filter(
    (doc) => doc.status === "failed"
  ).length;

  return (
    <AppShell>
      <div className="min-h-[calc(100vh-76px)] bg-[#f8f9fc] px-8 py-8">

        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <div className="mx-auto max-w-7xl">

          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">

            <div>
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1.5 text-[11px] font-medium uppercase tracking-wider text-indigo-600">
                <Database size={13} />
                Knowledge base
              </div>

              <h1 className="text-3xl font-semibold tracking-tight text-[#111827]">
                Documents
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-[#73798a]">
                Upload and manage the documents that power
                Company OS retrieval and grounded answers.
              </p>
            </div>

            {/* UPLOAD */}

            <label
              className={`inline-flex cursor-pointer items-center justify-center gap-2 rounded-xl bg-[#111827] px-5 py-3 text-sm font-medium text-white shadow-lg shadow-slate-900/10 transition hover:bg-[#1c2434] ${
                uploading
                  ? "pointer-events-none opacity-50"
                  : ""
              }`}
            >
              <Upload size={17} />

              {uploading
                ? "Uploading..."
                : "Upload document"}

              <input
                type="file"
                className="hidden"
                accept=".pdf,.txt,.md,.doc,.docx,.csv,.xlsx,.xls"
                onChange={handleUpload}
                disabled={uploading}
              />
            </label>
          </div>


          {/* ================================================= */}
          {/* STATS */}
          {/* ================================================= */}

          <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-4">

            <StatCard
              label="Total documents"
              value={documents.length}
              icon={<FileText size={18} />}
            />

            <StatCard
              label="Indexed"
              value={completedCount}
              icon={<CheckCircle2 size={18} />}
            />

            <StatCard
              label="Processing"
              value={processingCount}
              icon={<Clock3 size={18} />}
            />

            <StatCard
              label="Failed"
              value={failedCount}
              icon={<AlertCircle size={18} />}
            />

          </div>


          {/* ================================================= */}
          {/* ERROR */}
          {/* ================================================= */}

          {error && (
            <div className="mt-6 flex items-start gap-3 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
              <AlertCircle
                size={18}
                className="mt-0.5 shrink-0"
              />

              <div>
                <div className="font-medium">
                  Something went wrong
                </div>

                <div className="mt-0.5 text-red-600/80">
                  {error}
                </div>
              </div>
            </div>
          )}


          {/* ================================================= */}
          {/* DOCUMENT PANEL */}
          {/* ================================================= */}

          <div className="mt-8 overflow-hidden rounded-2xl border border-[#e5e7eb] bg-white shadow-sm">

            {/* TOOLBAR */}

            <div className="flex flex-col gap-4 border-b border-[#edf0f4] p-5 md:flex-row md:items-center md:justify-between">

              <div className="relative max-w-md flex-1">
                <Search
                  size={17}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9aa0ae]"
                />

                <input
                  value={search}
                  onChange={(event) =>
                    setSearch(event.target.value)
                  }
                  placeholder="Search documents..."
                  className="h-11 w-full rounded-xl border border-[#e3e6ec] bg-[#fafbfc] pl-10 pr-4 text-sm outline-none transition placeholder:text-[#a5abb8] focus:border-indigo-300 focus:bg-white"
                />
              </div>

              <button
                onClick={loadDocuments}
                disabled={loading}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-[#e3e6ec] px-4 text-sm font-medium text-[#4b5563] transition hover:bg-[#f8f9fc] disabled:opacity-50"
              >
                <RefreshCw
                  size={16}
                  className={
                    loading
                      ? "animate-spin"
                      : ""
                  }
                />

                Refresh
              </button>

            </div>


            {/* TABLE */}

            {loading ? (
              <LoadingState />
            ) : filteredDocuments.length === 0 ? (
              <EmptyState
                hasSearch={Boolean(search)}
              />
            ) : (
              <div className="divide-y divide-[#edf0f4]">

                {filteredDocuments.map(
                  (document) => (
                    <DocumentRow
                      key={document.document_id}
                      document={document}
                      onDelete={handleDelete}
                    />
                  )
                )}

              </div>
            )}

          </div>

        </div>
      </div>
    </AppShell>
  );
}


/* ========================================================= */
/* STAT CARD */
/* ========================================================= */

function StatCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-[#e5e7eb] bg-white p-5 shadow-sm">

      <div className="flex items-center justify-between">

        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#f1f3f7] text-[#667085]">
          {icon}
        </div>

      </div>

      <div className="mt-4 text-2xl font-semibold tracking-tight">
        {value}
      </div>

      <div className="mt-1 text-xs text-[#8a92a3]">
        {label}
      </div>

    </div>
  );
}


/* ========================================================= */
/* DOCUMENT ROW */
/* ========================================================= */

function DocumentRow({
  document,
  onDelete,
}: {
  document: DocumentItem;
  onDelete: (id: number) => void;
}) {
  return (
    <div className="group flex flex-col gap-4 px-5 py-5 transition hover:bg-[#fafbfc] md:flex-row md:items-center">

      <div className="flex min-w-0 flex-1 items-center gap-4">

        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
          <FileText size={20} />
        </div>

        <div className="min-w-0">

          <div className="truncate text-sm font-semibold text-[#1f2937]">
            {document.filename}
          </div>

          <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-[#9aa0ae]">

            <span>
              {document.file_type}
            </span>

            <span>•</span>

            <span>
              {formatDate(document.created_at)}
            </span>

          </div>

        </div>

      </div>


      <StatusBadge status={document.status} />


      <button
        onClick={() =>
          onDelete(document.document_id)
        }
        className="flex h-9 w-9 items-center justify-center rounded-lg text-[#a1a8b5] opacity-100 transition hover:bg-red-50 hover:text-red-500 md:opacity-0 md:group-hover:opacity-100"
        title="Delete document"
      >
        <Trash2 size={16} />
      </button>

    </div>
  );
}


/* ========================================================= */
/* STATUS */
/* ========================================================= */

function StatusBadge({
  status,
}: {
  status: DocumentItem["status"];
}) {
  const config = {
    completed: {
      label: "Indexed",
      className:
        "border-emerald-100 bg-emerald-50 text-emerald-700",
      icon: <CheckCircle2 size={13} />,
    },

    processing: {
      label: "Processing",
      className:
        "border-blue-100 bg-blue-50 text-blue-700",
      icon: <Clock3 size={13} />,
    },

    queued: {
      label: "Queued",
      className:
        "border-amber-100 bg-amber-50 text-amber-700",
      icon: <Clock3 size={13} />,
    },

    failed: {
      label: "Failed",
      className:
        "border-red-100 bg-red-50 text-red-700",
      icon: <AlertCircle size={13} />,
    },
  };

  const current = config[status];

  return (
    <div
      className={`inline-flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-[11px] font-medium ${current.className}`}
    >
      {current.icon}
      {current.label}
    </div>
  );
}


/* ========================================================= */
/* LOADING */
/* ========================================================= */

function LoadingState() {
  return (
    <div className="space-y-4 p-6">

      {[1, 2, 3].map((item) => (
        <div
          key={item}
          className="flex items-center gap-4"
        >
          <div className="h-11 w-11 animate-pulse rounded-xl bg-[#eef0f4]" />

          <div className="flex-1 space-y-2">
            <div className="h-4 w-1/3 animate-pulse rounded bg-[#eef0f4]" />
            <div className="h-3 w-1/4 animate-pulse rounded bg-[#f2f3f6]" />
          </div>
        </div>
      ))}

    </div>
  );
}


/* ========================================================= */
/* EMPTY */
/* ========================================================= */

function EmptyState({
  hasSearch,
}: {
  hasSearch: boolean;
}) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center px-6 text-center">

      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#f1f3f7] text-[#8a92a3]">
        <FileText size={25} />
      </div>

      <h3 className="mt-5 text-sm font-semibold">
        {hasSearch
          ? "No documents found"
          : "No documents yet"}
      </h3>

      <p className="mt-2 max-w-sm text-xs leading-5 text-[#8a92a3]">
        {hasSearch
          ? "Try a different document name."
          : "Upload your first company document to start building the knowledge base."}
      </p>

    </div>
  );
}


/* ========================================================= */
/* DATE */
/* ========================================================= */

function formatDate(value: string) {
  try {
    return new Date(value).toLocaleDateString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }
    );
  } catch {
    return value;
  }
}