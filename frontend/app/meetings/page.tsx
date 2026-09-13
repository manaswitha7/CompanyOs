"use client";

import { FormEvent, useEffect, useState } from "react";
import AppShell from "@/components/AppShell";

import {
  getMeetings as apiGetMeetings,
  getMeeting as apiGetMeeting,
  createMeeting as apiCreateMeeting,
} from "@/lib/api";

type Meeting = {
  id: number;
  title: string;
  description?: string | null;
  meeting_type?: string | null;
  source_type?: string | null;
  source_uri?: string | null;
  status?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

type Participant = {
  id: number;
  name: string;
  email?: string | null;
  speaker_label?: string | null;
  user_id?: number | null;
};

type Transcript = {
  id: number;
  text: string;
  sequence_number: number;
  speaker_label?: string | null;
  start_time_seconds?: number | null;
  end_time_seconds?: number | null;
};

type Decision = {
  id: number;
  decision: string;
  context?: string | null;
  speaker_label?: string | null;
};

type ActionItem = {
  id: number;
  description: string;
  assignee_name?: string | null;
  assignee_user_id?: number | null;
  due_at?: string | null;
};

type Summary = {
  id: number;
  summary: string;
  key_points?: string | null;
  follow_ups?: string | null;
  generated_by?: string | null;
};

type MeetingDetails = Meeting & {
  participants?: Participant[];
  transcripts?: Transcript[];
  transcript?: Transcript[];
  decisions?: Decision[];
  action_items?: ActionItem[];
  summary?: Summary | null;
};

type Tab =
  | "overview"
  | "participants"
  | "transcript"
  | "summary"
  | "decisions"
  | "actions";

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [selectedMeeting, setSelectedMeeting] =
    useState<MeetingDetails | null>(null);

  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState("");

  const [showCreate, setShowCreate] = useState(false);

  const [activeTab, setActiveTab] =
    useState<Tab>("overview");

  const [search, setSearch] = useState("");

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [meetingType, setMeetingType] = useState("");
  const [sourceType, setSourceType] = useState("upload");
  const [sourceUri, setSourceUri] = useState("");

  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadMeetings();
  }, []);

  async function loadMeetings() {
    setLoading(true);
    setError("");

    try {
      const items = await apiGetMeetings();

      setMeetings(items);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to load meetings. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadMeeting(id: number) {
    setDetailsLoading(true);
    setError("");

    try {
      // GET /meetings/{id} returns { meeting, participants,
      // transcript, decisions, action_items, summary } —
      // flatten it into the shape the UI below expects.
      const data = await apiGetMeeting(id);

      setSelectedMeeting({
        ...data.meeting,
        participants: data.participants,
        transcript: data.transcript,
        decisions: data.decisions,
        action_items: data.action_items,
        summary: data.summary,
      });

      setActiveTab("overview");
    } catch (err) {
      console.error(err);

      setError(
        "Unable to load the selected meeting."
      );
    } finally {
      setDetailsLoading(false);
    }
  }

  async function createMeeting(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!title.trim()) {
      return;
    }

    setCreating(true);
    setError("");

    try {
      const meeting = await apiCreateMeeting({
        title: title.trim(),
        description: description.trim() || null,
        meeting_type: meetingType.trim() || null,
        source_type: sourceType,
        source_uri: sourceUri.trim() || null,
      });

      setMeetings((current) => [
        meeting,
        ...current,
      ]);

      resetCreateForm();

      // Fetch full details (participants/transcript/etc. are
      // empty right after creation, but this keeps the shape
      // consistent with loadMeeting rather than setting a
      // partial object directly).
      await loadMeeting(meeting.id);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to create meeting."
      );
    } finally {
      setCreating(false);
    }
  }

  function resetCreateForm() {
    setTitle("");
    setDescription("");
    setMeetingType("");
    setSourceType("upload");
    setSourceUri("");
    setShowCreate(false);
  }

  const filteredMeetings = meetings.filter(
    (meeting) =>
      meeting.title
        ?.toLowerCase()
        .includes(search.toLowerCase()) ||
      meeting.description
        ?.toLowerCase()
        .includes(search.toLowerCase())
  );

  if (selectedMeeting) {
    return (
      <AppShell>
        <MeetingDetailsView
          meeting={selectedMeeting}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onBack={() => {
            setSelectedMeeting(null);
            setActiveTab("overview");
          }}
          loading={detailsLoading}
          error={error}
          onRefresh={() =>
            loadMeeting(selectedMeeting.id)
          }
        />
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="min-h-full bg-[#09090b] text-white">
        <div className="mx-auto max-w-[1500px] px-6 py-6">

          {/* HEADER */}

          <div className="mb-7 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">
                Meetings
              </h1>

              <p className="mt-1 text-sm text-zinc-400">
                Capture conversations, decisions and follow-up
                actions.
              </p>
            </div>

            <button
              onClick={() => setShowCreate(true)}
              className="rounded-lg bg-white px-4 py-2.5 text-sm font-medium text-black transition hover:bg-zinc-200"
            >
              + New Meeting
            </button>
          </div>

          {/* ERROR */}

          {error && (
            <div className="mb-5 rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-300">
              {error}
            </div>
          )}

          {/* SEARCH */}

          <div className="mb-6 flex items-center gap-3">
            <div className="relative flex-1">
              <input
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
                placeholder="Search meetings..."
                className="w-full rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-500 focus:border-white/20"
              />
            </div>

            <button
              onClick={loadMeetings}
              className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-zinc-300 hover:bg-white/[0.06]"
            >
              Refresh
            </button>
          </div>

          {/* CONTENT */}

          {loading ? (
            <div className="flex min-h-[350px] items-center justify-center">
              <div className="text-sm text-zinc-400">
                Loading meetings...
              </div>
            </div>
          ) : filteredMeetings.length === 0 ? (
            <EmptyMeetings
              onCreate={() =>
                setShowCreate(true)
              }
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {filteredMeetings.map(
                (meeting) => (
                  <MeetingCard
                    key={meeting.id}
                    meeting={meeting}
                    onOpen={() =>
                      loadMeeting(meeting.id)
                    }
                  />
                )
              )}
            </div>
          )}
        </div>

        {/* CREATE MODAL */}

        {showCreate && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
            <div className="w-full max-w-lg rounded-2xl border border-white/10 bg-[#111113] shadow-2xl">

              <div className="flex items-center justify-between border-b border-white/10 px-6 py-5">
                <div>
                  <h2 className="text-lg font-semibold">
                    Create Meeting
                  </h2>

                  <p className="mt-1 text-xs text-zinc-500">
                    Add a meeting to Company OS.
                  </p>
                </div>

                <button
                  onClick={resetCreateForm}
                  className="text-zinc-500 hover:text-white"
                >
                  ✕
                </button>
              </div>

              <form
                onSubmit={createMeeting}
                className="space-y-5 p-6"
              >

                <div>
                  <label className="mb-2 block text-sm text-zinc-300">
                    Title
                  </label>

                  <input
                    value={title}
                    onChange={(event) =>
                      setTitle(event.target.value)
                    }
                    placeholder="Weekly product meeting"
                    required
                    className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 text-sm outline-none placeholder:text-zinc-600 focus:border-white/20"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm text-zinc-300">
                    Description
                  </label>

                  <textarea
                    value={description}
                    onChange={(event) =>
                      setDescription(
                        event.target.value
                      )
                    }
                    rows={3}
                    placeholder="What is this meeting about?"
                    className="w-full resize-none rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 text-sm outline-none placeholder:text-zinc-600 focus:border-white/20"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">

                  <div>
                    <label className="mb-2 block text-sm text-zinc-300">
                      Meeting Type
                    </label>

                    <input
                      value={meetingType}
                      onChange={(event) =>
                        setMeetingType(
                          event.target.value
                        )
                      }
                      placeholder="Standup"
                      className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 text-sm outline-none placeholder:text-zinc-600 focus:border-white/20"
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-sm text-zinc-300">
                      Source
                    </label>

                    <select
                      value={sourceType}
                      onChange={(event) =>
                        setSourceType(
                          event.target.value
                        )
                      }
                      className="w-full rounded-lg border border-white/10 bg-[#111113] px-3 py-2.5 text-sm outline-none"
                    >
                      <option value="upload">
                        Upload
                      </option>

                      <option value="manual">
                        Manual
                      </option>

                      <option value="zoom">
                        Zoom
                      </option>

                      <option value="google_meet">
                        Google Meet
                      </option>
                    </select>
                  </div>

                </div>

                <div>
                  <label className="mb-2 block text-sm text-zinc-300">
                    Source URI
                  </label>

                  <input
                    value={sourceUri}
                    onChange={(event) =>
                      setSourceUri(
                        event.target.value
                      )
                    }
                    placeholder="Optional recording/file URL"
                    className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 text-sm outline-none placeholder:text-zinc-600 focus:border-white/20"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-2">

                  <button
                    type="button"
                    onClick={resetCreateForm}
                    className="rounded-lg border border-white/10 px-4 py-2.5 text-sm text-zinc-300 hover:bg-white/[0.05]"
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    disabled={
                      creating || !title.trim()
                    }
                    className="rounded-lg bg-white px-5 py-2.5 text-sm font-medium text-black disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {creating
                      ? "Creating..."
                      : "Create Meeting"}
                  </button>

                </div>

              </form>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}


/* =========================================================
   MEETING CARD
========================================================= */

function MeetingCard({
  meeting,
  onOpen,
}: {
  meeting: Meeting;
  onOpen: () => void;
}) {
  return (
    <button
      onClick={onOpen}
      className="group rounded-2xl border border-white/10 bg-white/[0.025] p-5 text-left transition hover:border-white/20 hover:bg-white/[0.045]"
    >
      <div className="mb-5 flex items-start justify-between gap-4">

        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/[0.05] text-sm">
          🎙
        </div>

        <StatusBadge
          status={meeting.status}
        />

      </div>

      <h3 className="line-clamp-2 text-base font-medium text-white">
        {meeting.title}
      </h3>

      {meeting.description && (
        <p className="mt-2 line-clamp-2 text-sm leading-5 text-zinc-500">
          {meeting.description}
        </p>
      )}

      <div className="mt-5 flex items-center justify-between border-t border-white/[0.06] pt-4 text-xs text-zinc-500">

        <span>
          {meeting.meeting_type ||
            "General meeting"}
        </span>

        <span>
          {formatDate(meeting.created_at)}
        </span>

      </div>
    </button>
  );
}


/* =========================================================
   MEETING DETAILS
========================================================= */

function MeetingDetailsView({
  meeting,
  activeTab,
  setActiveTab,
  onBack,
  loading,
  error,
  onRefresh,
}: {
  meeting: MeetingDetails;
  activeTab: Tab;
  setActiveTab: (tab: Tab) => void;
  onBack: () => void;
  loading: boolean;
  error: string;
  onRefresh: () => void;
}) {
  const participants =
    meeting.participants || [];

  const transcripts =
    meeting.transcripts ||
    meeting.transcript ||
    [];

  const decisions =
    meeting.decisions || [];

  const actionItems =
    meeting.action_items || [];

  const tabs: {
    id: Tab;
    label: string;
  }[] = [
    {
      id: "overview",
      label: "Overview",
    },
    {
      id: "participants",
      label: "Participants",
    },
    {
      id: "transcript",
      label: "Transcript",
    },
    {
      id: "summary",
      label: "Summary",
    },
    {
      id: "decisions",
      label: "Decisions",
    },
    {
      id: "actions",
      label: "Action Items",
    },
  ];

  return (
    <div className="min-h-full bg-[#09090b] text-white">
      <div className="mx-auto max-w-[1500px] px-6 py-6">

        {/* TOP BAR */}

        <div className="mb-6 flex items-center justify-between">

          <button
            onClick={onBack}
            className="text-sm text-zinc-400 hover:text-white"
          >
            ← Back to Meetings
          </button>

          <button
            onClick={onRefresh}
            className="rounded-lg border border-white/10 px-3 py-2 text-sm text-zinc-300 hover:bg-white/[0.05]"
          >
            Refresh
          </button>

        </div>

        {/* HEADER */}

        <div className="mb-7">

          <div className="flex items-start gap-4">

            <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-white/10 bg-white/[0.05] text-xl">
              🎙
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-semibold">
                  {meeting.title}
                </h1>

                <StatusBadge
                  status={meeting.status}
                />
              </div>

              <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-sm text-zinc-500">

                <span>
                  {meeting.meeting_type ||
                    "General meeting"}
                </span>

                <span>
                  Source:{" "}
                  {meeting.source_type ||
                    "unknown"}
                </span>

                <span>
                  {formatDate(
                    meeting.created_at
                  )}
                </span>

              </div>
            </div>

          </div>

          {meeting.description && (
            <p className="mt-5 max-w-3xl text-sm leading-6 text-zinc-400">
              {meeting.description}
            </p>
          )}

        </div>

        {/* ERROR */}

        {error && (
          <div className="mb-5 rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* TABS */}

        <div className="mb-6 overflow-x-auto">
          <div className="flex min-w-max gap-1 rounded-xl border border-white/10 bg-white/[0.025] p-1">

            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() =>
                  setActiveTab(tab.id)
                }
                className={[
                  "rounded-lg px-4 py-2 text-sm transition",
                  activeTab === tab.id
                    ? "bg-white/10 text-white"
                    : "text-zinc-500 hover:bg-white/[0.05] hover:text-zinc-300",
                ].join(" ")}
              >
                {tab.label}
              </button>
            ))}

          </div>
        </div>

        {loading ? (
          <div className="flex min-h-[300px] items-center justify-center">
            <div className="text-sm text-zinc-400">
              Loading meeting...
            </div>
          </div>
        ) : (
          <div>

            {activeTab === "overview" && (
              <OverviewTab
                meeting={meeting}
                participants={participants}
                transcripts={transcripts}
                decisions={decisions}
                actionItems={actionItems}
              />
            )}

            {activeTab === "participants" && (
              <ParticipantsTab
                participants={participants}
              />
            )}

            {activeTab === "transcript" && (
              <TranscriptTab
                transcripts={transcripts}
              />
            )}

            {activeTab === "summary" && (
              <SummaryTab
                summary={meeting.summary}
              />
            )}

            {activeTab === "decisions" && (
              <DecisionsTab
                decisions={decisions}
              />
            )}

            {activeTab === "actions" && (
              <ActionsTab
                actionItems={actionItems}
              />
            )}

          </div>
        )}
      </div>
    </div>
  );
}


/* =========================================================
   OVERVIEW
========================================================= */

function OverviewTab({
  meeting,
  participants,
  transcripts,
  decisions,
  actionItems,
}: {
  meeting: MeetingDetails;
  participants: Participant[];
  transcripts: Transcript[];
  decisions: Decision[];
  actionItems: ActionItem[];
}) {
  const summary = meeting.summary;

  return (
    <div className="grid gap-5 lg:grid-cols-3">

      <MetricCard
        label="Participants"
        value={participants.length}
      />

      <MetricCard
        label="Transcript segments"
        value={transcripts.length}
      />

      <MetricCard
        label="Action items"
        value={actionItems.length}
      />

      <div className="lg:col-span-2 rounded-xl border border-white/10 bg-white/[0.025] p-6">

        <h2 className="text-sm font-medium text-white">
          Meeting Summary
        </h2>

        {summary?.summary ? (
          <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-zinc-400">
            {summary.summary}
          </p>
        ) : (
          <EmptyState text="No summary has been generated yet." />
        )}

      </div>

      <div className="rounded-xl border border-white/10 bg-white/[0.025] p-6">

        <h2 className="text-sm font-medium text-white">
          Decisions
        </h2>

        {decisions.length ? (
          <div className="mt-4 space-y-3">
            {decisions.slice(0, 5).map(
              (decision) => (
                <div
                  key={decision.id}
                  className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3"
                >
                  <p className="text-sm text-zinc-300">
                    {decision.decision}
                  </p>
                </div>
              )
            )}
          </div>
        ) : (
          <EmptyState text="No decisions recorded." />
        )}

      </div>

    </div>
  );
}


/* =========================================================
   PARTICIPANTS
========================================================= */

function ParticipantsTab({
  participants,
}: {
  participants: Participant[];
}) {
  if (!participants.length) {
    return (
      <EmptyState text="No participants have been added yet." />
    );
  }

  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {participants.map((participant) => (
        <div
          key={participant.id}
          className="rounded-xl border border-white/10 bg-white/[0.025] p-5"
        >
          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 text-sm font-medium">
              {participant.name
                ?.charAt(0)
                ?.toUpperCase()}
            </div>

            <div>
              <div className="text-sm font-medium text-white">
                {participant.name}
              </div>

              {participant.email && (
                <div className="text-xs text-zinc-500">
                  {participant.email}
                </div>
              )}
            </div>

          </div>

          {participant.speaker_label && (
            <div className="mt-4 text-xs text-zinc-500">
              Speaker:{" "}
              {participant.speaker_label}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}


/* =========================================================
   TRANSCRIPT
========================================================= */

function TranscriptTab({
  transcripts,
}: {
  transcripts: Transcript[];
}) {
  if (!transcripts.length) {
    return (
      <EmptyState text="No transcript has been added yet." />
    );
  }

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.025]">

      <div className="divide-y divide-white/[0.06]">

        {transcripts.map((segment) => (
          <div
            key={segment.id}
            className="flex gap-5 px-6 py-5"
          >

            <div className="w-24 shrink-0 text-xs text-zinc-600">
              {formatSeconds(
                segment.start_time_seconds
              )}
            </div>

            <div>
              {segment.speaker_label && (
                <div className="mb-1 text-xs font-medium text-zinc-400">
                  {segment.speaker_label}
                </div>
              )}

              <p className="text-sm leading-6 text-zinc-300">
                {segment.text}
              </p>
            </div>

          </div>
        ))}

      </div>
    </div>
  );
}


/* =========================================================
   SUMMARY
========================================================= */

function SummaryTab({
  summary,
}: {
  summary?: Summary | null;
}) {
  if (!summary) {
    return (
      <EmptyState text="No AI summary has been generated yet." />
    );
  }

  return (
    <div className="space-y-5">

      <section className="rounded-xl border border-white/10 bg-white/[0.025] p-6">

        <h2 className="text-sm font-medium text-white">
          Summary
        </h2>

        <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-zinc-300">
          {summary.summary}
        </p>

      </section>

      {summary.key_points && (
        <section className="rounded-xl border border-white/10 bg-white/[0.025] p-6">

          <h2 className="text-sm font-medium text-white">
            Key Points
          </h2>

          <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-zinc-400">
            {summary.key_points}
          </p>

        </section>
      )}

      {summary.follow_ups && (
        <section className="rounded-xl border border-white/10 bg-white/[0.025] p-6">

          <h2 className="text-sm font-medium text-white">
            Follow-ups
          </h2>

          <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-zinc-400">
            {summary.follow_ups}
          </p>

        </section>
      )}

    </div>
  );
}


/* =========================================================
   DECISIONS
========================================================= */

function DecisionsTab({
  decisions,
}: {
  decisions: Decision[];
}) {
  if (!decisions.length) {
    return (
      <EmptyState text="No decisions have been recorded yet." />
    );
  }

  return (
    <div className="space-y-3">

      {decisions.map((decision, index) => (
        <div
          key={decision.id}
          className="rounded-xl border border-white/10 bg-white/[0.025] p-5"
        >

          <div className="flex gap-4">

            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white/10 text-xs text-zinc-300">
              {index + 1}
            </div>

            <div>

              <p className="text-sm leading-6 text-zinc-200">
                {decision.decision}
              </p>

              {decision.context && (
                <p className="mt-2 text-xs leading-5 text-zinc-500">
                  {decision.context}
                </p>
              )}

              {decision.speaker_label && (
                <p className="mt-3 text-xs text-zinc-600">
                  {decision.speaker_label}
                </p>
              )}

            </div>

          </div>

        </div>
      ))}

    </div>
  );
}


/* =========================================================
   ACTION ITEMS
========================================================= */

function ActionsTab({
  actionItems,
}: {
  actionItems: ActionItem[];
}) {
  if (!actionItems.length) {
    return (
      <EmptyState text="No action items have been recorded yet." />
    );
  }

  return (
    <div className="space-y-3">

      {actionItems.map((item) => (
        <div
          key={item.id}
          className="rounded-xl border border-white/10 bg-white/[0.025] p-5"
        >

          <p className="text-sm text-zinc-200">
            {item.description}
          </p>

          <div className="mt-3 flex flex-wrap gap-4 text-xs text-zinc-500">

            {item.assignee_name && (
              <span>
                Assignee: {item.assignee_name}
              </span>
            )}

            {item.due_at && (
              <span>
                Due: {formatDate(item.due_at)}
              </span>
            )}

          </div>

        </div>
      ))}

    </div>
  );
}


/* =========================================================
   SMALL COMPONENTS
========================================================= */

function MetricCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.025] p-5">
      <div className="text-sm text-zinc-500">
        {label}
      </div>

      <div className="mt-3 text-3xl font-semibold">
        {value}
      </div>
    </div>
  );
}


function StatusBadge({
  status,
}: {
  status?: string | null;
}) {
  const value =
    status?.replace(/_/g, " ") ||
    "unknown";

  return (
    <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[11px] capitalize text-zinc-400">
      {value}
    </span>
  );
}


function EmptyMeetings({
  onCreate,
}: {
  onCreate: () => void;
}) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-white/[0.015]">

      <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04] text-2xl">
        🎙
      </div>

      <h2 className="mt-5 text-base font-medium">
        No meetings yet
      </h2>

      <p className="mt-2 max-w-sm text-center text-sm text-zinc-500">
        Create a meeting to start capturing transcripts,
        summaries, decisions and action items.
      </p>

      <button
        onClick={onCreate}
        className="mt-6 rounded-lg bg-white px-4 py-2.5 text-sm font-medium text-black hover:bg-zinc-200"
      >
        + Create Meeting
      </button>

    </div>
  );
}


function EmptyState({
  text,
}: {
  text: string;
}) {
  return (
    <div className="rounded-xl border border-dashed border-white/10 p-10 text-center text-sm text-zinc-500">
      {text}
    </div>
  );
}


function formatDate(
  value?: string | null
) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString(
    undefined,
    {
      year: "numeric",
      month: "short",
      day: "numeric",
    }
  );
}


function formatSeconds(
  value?: number | null
) {
  if (
    value === null ||
    value === undefined
  ) {
    return "";
  }

  const minutes = Math.floor(value / 60);
  const seconds = Math.floor(value % 60);

  return `${minutes}:${String(seconds).padStart(
    2,
    "0"
  )}`;
}