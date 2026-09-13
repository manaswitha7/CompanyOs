"use client";

import { FormEvent, useRef, useState } from "react";
import {
  ApiError,
  deleteDocument,
  uploadDocument,
} from "@/lib/api";

import type {
  DocumentItem,
  UploadResponse,
} from "@/lib/types";

import { StatusBadge } from "./StatusBadge";
import { ConfirmDialog } from "./ConfirmDialog";
import { useToast } from "./Toast";

const ALLOWED_EXTENSIONS = [
  ".pdf",
  ".txt",
  ".csv",
  ".xlsx",
  ".xls",
  ".docx",
  ".md",
  ".yaml",
  ".yml",
];

const PIPELINE = [
  "Upload",
  "Store original",
  "Detect format",
  "Extract content",
  "Chunk / normalize",
  "Embed",
  "Index",
];

type DocumentsViewProps = {
  documents: DocumentItem[];
  documentsLoading: boolean;
  onRefresh: () => void;
};

export function DocumentsView({
  documents,
  documentsLoading,
  onRefresh,
}: DocumentsViewProps) {
  const { showToast } = useToast();

  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [uploadLoading, setUploadLoading] =
    useState(false);

  const [uploadError, setUploadError] =
    useState("");

  const [uploadSuccess, setUploadSuccess] =
    useState<UploadResponse | null>(null);

  const [pendingDeleteId, setPendingDeleteId] =
    useState<number | null>(null);

  function getExtension(filename: string) {
    const index = filename.lastIndexOf(".");

    if (index === -1) {
      return "";
    }

    return filename
      .slice(index)
      .toLowerCase();
  }

  function getFileCategory(filename: string) {
    const extension =
      getExtension(filename);

    if (
      [".xlsx", ".xls", ".csv"].includes(
        extension
      )
    ) {
      return "Structured";
    }

    if (
      [".md", ".yaml", ".yml"].includes(
        extension
      )
    ) {
      return "Knowledge";
    }

    if (
      [".pdf", ".txt", ".docx"].includes(
        extension
      )
    ) {
      return "Document";
    }

    return "Unknown";
  }

  function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file =
      event.target.files?.[0] || null;

    setSelectedFile(file);
    setUploadError("");
    setUploadSuccess(null);

    if (!file) {
      return;
    }

    const extension =
      getExtension(file.name);

    if (
      !ALLOWED_EXTENSIONS.includes(
        extension
      )
    ) {
      setUploadError(
        "Unsupported file type."
      );

      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  async function handleUpload(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!selectedFile) {
      setUploadError(
        "Please select a file."
      );

      return;
    }

    const extension =
      getExtension(selectedFile.name);

    if (
      !ALLOWED_EXTENSIONS.includes(
        extension
      )
    ) {
      setUploadError(
        "Unsupported file type."
      );

      return;
    }

    setUploadLoading(true);
    setUploadError("");
    setUploadSuccess(null);

    try {
      const result =
        await uploadDocument(
          selectedFile
        );

      setUploadSuccess(result);
      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      onRefresh();

      showToast(
        "Document uploaded successfully.",
        "success"
      );
    } catch (err) {
      setUploadError(
        err instanceof ApiError
          ? err.message
          : "Unable to upload the document."
      );
    } finally {
      setUploadLoading(false);
    }
  }

  async function confirmDelete() {
    if (
      pendingDeleteId === null
    ) {
      return;
    }

    try {
      await deleteDocument(
        pendingDeleteId
      );

      onRefresh();

      showToast(
        "Document deleted.",
        "success"
      );
    } catch (err) {
      showToast(
        err instanceof ApiError
          ? err.message
          : "Failed to delete the document.",
        "error"
      );
    } finally {
      setPendingDeleteId(null);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">

      {/* HEADER */}

      <div className="mb-7">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-ink text-sm font-semibold text-white">
            KB
          </div>

          <div>
            <h1 className="font-display text-2xl font-semibold tracking-tight text-graphite">
              Knowledge Base
            </h1>

            <p className="mt-1 text-sm text-graphite-muted">
              Documents, structured data and knowledge
              sources used by Company OS.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">

        {/* MAIN */}

        <div className="space-y-6">

          {/* UPLOAD */}

          <section className="rounded-xl border border-paper-line bg-paper-raised p-5 shadow-sm">

            <div className="flex items-start justify-between gap-4">

              <div>
                <h2 className="font-display text-sm font-semibold text-graphite">
                  Add knowledge
                </h2>

                <p className="mt-1 text-xs text-graphite-muted">
                  Upload documents or structured data
                  into Company OS.
                </p>
              </div>

              <div className="rounded-md bg-paper px-2 py-1 font-mono text-[10px] text-graphite-muted">
                {ALLOWED_EXTENSIONS.join(" ")}
              </div>

            </div>

            <form
              onSubmit={handleUpload}
              className="mt-5"
            >

              <input
                ref={fileInputRef}
                type="file"
                accept={ALLOWED_EXTENSIONS.join(",")}
                onChange={handleFileChange}
                className="block w-full rounded-xl border border-dashed border-paper-line bg-paper p-6 font-mono text-xs text-graphite-muted file:mr-4 file:rounded-md file:border-0 file:bg-ink file:px-4 file:py-2 file:text-xs file:font-medium file:text-white hover:border-graphite-muted"
              />

              {selectedFile && (
                <div className="mt-4 rounded-xl border border-paper-line bg-paper px-4 py-3">

                  <div className="flex items-center justify-between gap-4">

                    <div className="min-w-0">

                      <p className="truncate text-sm font-medium text-graphite">
                        {selectedFile.name}
                      </p>

                      <p className="mt-1 font-mono text-[11px] text-graphite-muted">
                        {getFileCategory(
                          selectedFile.name
                        )}{" "}
                        ·{" "}
                        {(
                          selectedFile.size /
                          1024 /
                          1024
                        ).toFixed(2)}{" "}
                        MB
                      </p>

                    </div>

                    <button
                      type="button"
                      onClick={() => {
                        setSelectedFile(null);

                        if (
                          fileInputRef.current
                        ) {
                          fileInputRef.current.value =
                            "";
                        }
                      }}
                      className="text-xs text-graphite-muted hover:text-graphite"
                    >
                      remove
                    </button>

                  </div>

                </div>
              )}

              <button
                type="submit"
                disabled={
                  uploadLoading ||
                  !selectedFile
                }
                className="mt-4 w-full rounded-lg bg-signal px-4 py-2.5 text-sm font-medium text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {uploadLoading
                  ? "Uploading..."
                  : "Upload to Company OS"}
              </button>

            </form>

            {uploadError && (
              <div
                className="mt-4 rounded-lg px-4 py-3 text-sm"
                style={{
                  background:
                    "var(--status-failed-bg)",
                  color:
                    "var(--status-failed)",
                }}
              >
                {uploadError}
              </div>
            )}

            {uploadSuccess && (
              <div
                className="mt-4 rounded-lg px-4 py-3 text-sm"
                style={{
                  background:
                    "var(--status-done-bg)",
                  color:
                    "var(--status-done)",
                }}
              >
                <p className="font-medium">
                  {uploadSuccess.filename} uploaded
                </p>

                <p className="mt-1 font-mono text-xs opacity-80">
                  doc_id{" "}
                  {uploadSuccess.document_id}
                  {" · "}
                  queued for ingestion
                </p>
              </div>
            )}

          </section>

          {/* SUPPORTED FORMATS */}

          <section className="rounded-xl border border-paper-line bg-paper-raised p-5">

            <h2 className="font-display text-sm font-semibold text-graphite">
              Supported knowledge sources
            </h2>

            <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">

              <FormatCard
                title="Documents"
                formats="PDF · TXT · DOCX"
                description="Text-based company knowledge."
              />

              <FormatCard
                title="Structured Data"
                formats="CSV · XLS · XLSX"
                description="Tables, spreadsheets and business data."
              />

              <FormatCard
                title="Configuration"
                formats="MD · YAML · YML"
                description="Documentation and machine-readable knowledge."
              />

            </div>

          </section>

          {/* DOCUMENT LIST */}

          <section className="overflow-hidden rounded-xl border border-paper-line bg-paper-raised shadow-sm">

            <div className="flex items-center justify-between border-b border-paper-line px-5 py-3.5">

              <div>
                <h2 className="font-display text-sm font-semibold text-graphite">
                  All knowledge
                </h2>

                <p className="mt-0.5 text-xs text-graphite-muted">
                  {documents.length} source
                  {documents.length === 1
                    ? ""
                    : "s"}
                </p>
              </div>

              <button
                type="button"
                onClick={onRefresh}
                className="font-mono text-[11px] text-graphite-muted hover:text-signal"
              >
                refresh
              </button>

            </div>

            <div className="divide-y divide-paper-line">

              {documentsLoading ? (
                <EmptyRow text="Loading documents..." />
              ) : documents.length === 0 ? (
                <EmptyRow text="No documents uploaded yet." />
              ) : (
                documents.map(
                  (document) => {
                    const category =
                      getFileCategory(
                        document.filename
                      );

                    return (
                      <div
                        key={
                          document.document_id
                        }
                        className="flex items-center justify-between gap-4 px-5 py-4"
                      >

                        <div className="flex min-w-0 items-center gap-3">

                          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-paper font-mono text-[9px] font-semibold uppercase text-graphite-muted">
                            {document.file_type}
                          </div>

                          <div className="min-w-0">

                            <p className="truncate text-sm font-medium text-graphite">
                              {document.filename}
                            </p>

                            <p className="mt-0.5 font-mono text-[10px] text-graphite-muted">
                              {category}
                              {" · "}
                              doc_id{" "}
                              {document.document_id}
                            </p>

                          </div>

                        </div>

                        <div className="flex shrink-0 items-center gap-3">

                          <StatusBadge
                            status={
                              document.status
                            }
                          />

                          <button
                            type="button"
                            onClick={() =>
                              setPendingDeleteId(
                                document.document_id
                              )
                            }
                            className="font-mono text-[11px] text-graphite-muted hover:text-[var(--status-failed)]"
                          >
                            delete
                          </button>

                        </div>

                      </div>
                    );
                  }
                )
              )}

            </div>

          </section>

        </div>

        {/* PIPELINE */}

        <aside className="h-fit rounded-xl border border-paper-line bg-paper-raised p-5">

          <h2 className="font-display text-sm font-semibold text-graphite">
            Knowledge pipeline
          </h2>

          <p className="mt-1 text-xs leading-5 text-graphite-muted">
            Every source moves through the same
            ingestion architecture.
          </p>

          <div className="mt-5 space-y-4">

            {PIPELINE.map(
              (step, index) => (
                <div
                  key={step}
                  className="flex items-center gap-3"
                >

                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-ink font-mono text-[10px] font-semibold text-white">
                    {index + 1}
                  </span>

                  <span className="text-sm text-graphite">
                    {step}
                  </span>

                </div>
              )
            )}

          </div>

          <div className="mt-6 rounded-lg bg-paper p-4">

            <p className="font-mono text-[10px] uppercase tracking-wide text-graphite-muted">
              Architecture
            </p>

            <p className="mt-2 text-xs leading-5 text-graphite-muted">
              Original files remain in object
              storage while searchable knowledge
              is indexed separately.
            </p>

          </div>

        </aside>

      </div>

      <ConfirmDialog
        open={
          pendingDeleteId !== null
        }
        title="Delete document"
        description="This will remove the document and its indexed chunks. This can't be undone."
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        onCancel={() =>
          setPendingDeleteId(null)
        }
      />

    </div>
  );
}

function FormatCard({
  title,
  formats,
  description,
}: {
  title: string;
  formats: string;
  description: string;
}) {
  return (
    <div className="rounded-lg border border-paper-line bg-paper p-4">
      <p className="text-sm font-medium text-graphite">
        {title}
      </p>

      <p className="mt-2 font-mono text-[10px] text-signal">
        {formats}
      </p>

      <p className="mt-2 text-xs leading-5 text-graphite-muted">
        {description}
      </p>
    </div>
  );
}

function EmptyRow({
  text,
}: {
  text: string;
}) {
  return (
    <div className="px-5 py-10 text-center text-sm text-graphite-muted">
      {text}
    </div>
  );
}