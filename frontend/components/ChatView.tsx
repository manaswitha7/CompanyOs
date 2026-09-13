"use client";

import {
  ArrowUp,
  Check,
  FileText,
  Filter,
  History,
  MessageSquare,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
  Zap,
} from "lucide-react";
import { useState } from "react";

const suggestions = [
  {
    icon: FileText,
    text: "What is our leave policy?",
  },
  {
    icon: Target,
    text: "What are the company goals?",
  },
  {
    icon: Search,
    text: "Find our travel policy",
  },
  {
    icon: MessageSquare,
    text: "Summarize the onboarding process",
  },
];

export default function ChatView() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  async function askQuestion() {
    if (!question.trim()) return;

    setLoading(true);

    try {
      // Connect this to your existing API function later.
      console.log("Question:", question);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-76px)] bg-[#f8f9fc]">
      <div className="mx-auto max-w-[1180px] px-8 py-12">

        {/* HERO */}
        <section className="relative">
          <div className="absolute -left-20 -top-20 h-64 w-64 rounded-full bg-indigo-200/20 blur-3xl" />

          <div className="relative flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
            <div>
              <div className="mb-4 flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                  <Sparkles size={16} />
                </div>

                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-indigo-500">
                  AI Knowledge Assistant
                </span>
              </div>

              <h1 className="text-4xl font-semibold tracking-[-0.035em] text-[#111827] md:text-5xl">
                Ask Company OS
              </h1>

              <p className="mt-4 max-w-[650px] text-[15px] leading-7 text-[#73798a]">
                Get accurate answers grounded in your company&apos;s
                documents — with every response backed by a verifiable source.
              </p>
            </div>

            {/* Document filter */}
            <button className="flex h-12 min-w-[220px] items-center justify-between rounded-xl border border-[#e1e4eb] bg-white px-4 text-sm shadow-sm transition hover:border-[#cdd2de]">
              <span className="flex items-center gap-2.5">
                <Filter size={16} className="text-[#7d8494]" />
                <span>All documents</span>
              </span>

              <span className="text-[#9aa0ae]">⌄</span>
            </button>
          </div>
        </section>

        {/* QUERY BOX */}
        <section className="mt-10">
          <div
            className={`overflow-hidden rounded-2xl border bg-white shadow-[0_18px_60px_rgba(28,35,70,0.08)] transition ${
              question
                ? "border-indigo-300 ring-4 ring-indigo-50"
                : "border-[#e0e3eb]"
            }`}
          >
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  askQuestion();
                }
              }}
              placeholder="Ask anything about your company..."
              className="min-h-[155px] w-full resize-none bg-transparent px-6 py-6 text-[16px] text-[#111827] outline-none placeholder:text-[#a6adbb]"
            />

            {/* Controls */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-t border-[#edf0f4] px-5 py-4">
              <div className="flex flex-wrap items-center gap-2">
                <StatusPill
                  icon={<Target size={14} />}
                  text="Hybrid search"
                />

                <span className="text-[#d4d7df]">•</span>

                <StatusPill
                  icon={<Sparkles size={14} />}
                  text="Gemini 3.6 Flash"
                />

                <span className="text-[#d4d7df]">•</span>

                <StatusPill
                  icon={<Check size={14} />}
                  text="Citations on"
                  green
                />
              </div>

              <button
                onClick={askQuestion}
                disabled={!question.trim() || loading}
                className="flex h-11 items-center gap-2 rounded-xl bg-gradient-to-r from-[#315efb] to-[#5b5cf6] px-6 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:-translate-y-0.5 hover:shadow-indigo-500/30 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:translate-y-0"
              >
                {loading ? "Thinking..." : "Ask"}
                {!loading && <ArrowUp size={16} />}
              </button>
            </div>
          </div>
        </section>

        {/* SUGGESTIONS */}
        <section className="mt-7">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[#9aa0ae]">
              Try asking
            </span>

            <button className="flex items-center gap-1.5 text-xs text-[#9aa0ae] transition hover:text-[#4f596c]">
              <History size={13} />
              Recent
            </button>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            {suggestions.map((item) => {
              const Icon = item.icon;

              return (
                <button
                  key={item.text}
                  onClick={() => setQuestion(item.text)}
                  className="group flex items-center gap-3 rounded-xl border border-[#e6e8ef] bg-white px-4 py-3.5 text-left text-sm text-[#596174] shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-md"
                >
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#f4f5fa] text-[#7b8498] transition group-hover:bg-indigo-50 group-hover:text-indigo-600">
                    <Icon size={15} />
                  </span>

                  <span>{item.text}</span>

                  <ArrowUp
                    size={14}
                    className="ml-auto rotate-45 text-[#c5c9d3] transition group-hover:text-indigo-500"
                  />
                </button>
              );
            })}
          </div>
        </section>

        {/* TRUST PANEL */}
        <section className="mt-10">
          <div className="relative overflow-hidden rounded-2xl border border-indigo-100 bg-gradient-to-br from-white via-white to-indigo-50/50 p-7">
            <div className="absolute right-0 top-0 h-48 w-48 rounded-full bg-indigo-200/20 blur-3xl" />

            <div className="relative flex flex-col justify-between gap-7 md:flex-row md:items-center">
              <div className="flex gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
                  <ShieldCheck size={24} />
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-[#182033]">
                    Cited. Verifiable. Trusted.
                  </h2>

                  <p className="mt-1 max-w-[520px] text-sm leading-6 text-[#73798a]">
                    Company OS grounds responses in indexed company documents
                    and provides document and page-level citations.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3">
                <Check size={16} className="text-emerald-600" />

                <div>
                  <div className="text-xs font-semibold text-emerald-700">
                    Grounded AI
                  </div>
                  <div className="text-[10px] text-emerald-600/70">
                    Retrieval enabled
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* METRICS */}
        <section className="mt-5 grid overflow-hidden rounded-2xl border border-[#e6e8ef] bg-white shadow-sm md:grid-cols-4">
          <Metric
            icon={<FileText size={18} />}
            label="Documents"
            value="24"
            description="Indexed"
          />

          <Metric
            icon={<Zap size={18} />}
            label="Chunks"
            value="1,248"
            description="Indexed"
          />

          <Metric
            icon={<Sparkles size={18} />}
            label="Avg. response"
            value="6.2s"
            description="This session"
          />

          <Metric
            icon={<ShieldCheck size={18} />}
            label="Citations"
            value="98%"
            description="Accuracy"
            last
          />
        </section>
      </div>
    </div>
  );
}

function StatusPill({
  icon,
  text,
  green = false,
}: {
  icon: React.ReactNode;
  text: string;
  green?: boolean;
}) {
  return (
    <div
      className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-xs ${
        green
          ? "border-emerald-100 bg-emerald-50/60 text-emerald-700"
          : "border-[#e8eaf0] bg-[#fafbfc] text-[#697287]"
      }`}
    >
      {icon}
      {text}
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
  description,
  last = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  description: string;
  last?: boolean;
}) {
  return (
    <div
      className={`flex items-center gap-4 px-6 py-5 ${
        !last ? "border-b md:border-b-0 md:border-r border-[#edf0f4]" : ""
      }`}
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-500">
        {icon}
      </div>

      <div>
        <div className="text-[11px] text-[#8b92a2]">{label}</div>

        <div className="mt-0.5 flex items-baseline gap-2">
          <span className="text-xl font-semibold tracking-tight text-[#172033]">
            {value}
          </span>

          <span className="text-[10px] text-[#a2a8b5]">
            {description}
          </span>
        </div>
      </div>
    </div>
  );
}