"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  createTask,
  deleteTask,
  getTasks,
  updateTask,
} from "@/lib/api";

import type {
  CreateTaskRequest,
  Task,
  UpdateTaskRequest,
} from "@/lib/types";


// ============================================================
// TYPES
// ============================================================

type TaskResponse =
  | Task[]
  | {
      tasks?: Task[];
      count?: number;
    };


// ============================================================
// PAGE
// ============================================================

export default function TasksPage() {
  // ----------------------------------------------------------
  // STATE
  // ----------------------------------------------------------

  const [tasks, setTasks] = useState<Task[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [creating, setCreating] =
    useState(false);

  const [newTitle, setNewTitle] =
    useState("");

  const [newDescription, setNewDescription] =
    useState("");

  const [editingTaskId, setEditingTaskId] =
    useState<number | null>(null);

  const [editingTitle, setEditingTitle] =
    useState("");

  const [editingDescription, setEditingDescription] =
    useState("");

  const [editingStatus, setEditingStatus] =
    useState("todo");

  const [savingTaskId, setSavingTaskId] =
    useState<number | null>(null);

  const [deletingTaskId, setDeletingTaskId] =
    useState<number | null>(null);


  // ==========================================================
  // LOAD TASKS
  // ==========================================================

  async function loadTasks() {
    try {
      setLoading(true);
      setError(null);

      const response =
        (await getTasks()) as TaskResponse;

      /*
       * The frontend normally expects:
       *
       * [
       *   {...},
       *   {...}
       * ]
       *
       * But if the backend returns:
       *
       * {
       *   "tasks": [...],
       *   "count": 4
       * }
       *
       * we normalize it here.
       */

      let normalizedTasks: Task[] = [];

      if (Array.isArray(response)) {
        normalizedTasks = response;
      } else if (
        response &&
        Array.isArray(response.tasks)
      ) {
        normalizedTasks = response.tasks;
      }

      setTasks(normalizedTasks);

    } catch (err) {
      console.error(
        "Failed to load tasks:",
        err
      );

      setTasks([]);

      setError(
        err instanceof Error
          ? err.message
          : "Failed to load tasks."
      );

    } finally {
      setLoading(false);
    }
  }


  // ==========================================================
  // INITIAL LOAD
  // ==========================================================

  useEffect(() => {
    loadTasks();
  }, []);


  // ==========================================================
  // CREATE TASK
  // ==========================================================

  async function handleCreateTask(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const title =
      newTitle.trim();

    const description =
      newDescription.trim();

    if (!title) {
      return;
    }

    try {
      setCreating(true);
      setError(null);

      const payload: CreateTaskRequest = {
        title,
        description:
          description || undefined,
      };

      const created =
        await createTask(payload);

      /*
       * Add the newly-created task immediately
       * instead of making the user wait for another
       * GET request.
       */

      setTasks((previous) => [
        created,
        ...previous,
      ]);

      setNewTitle("");
      setNewDescription("");

    } catch (err) {
      console.error(
        "Failed to create task:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Failed to create task."
      );

    } finally {
      setCreating(false);
    }
  }


  // ==========================================================
  // START EDITING
  // ==========================================================

  function startEditing(task: Task) {
    setEditingTaskId(task.id);

    setEditingTitle(
      task.title ?? ""
    );

    setEditingDescription(
      task.description ?? ""
    );

    setEditingStatus(
      task.status ?? "todo"
    );

    setError(null);
  }


  // ==========================================================
  // CANCEL EDITING
  // ==========================================================

  function cancelEditing() {
    setEditingTaskId(null);

    setEditingTitle("");
    setEditingDescription("");
    setEditingStatus("todo");
  }


  // ==========================================================
  // SAVE TASK
  // ==========================================================

  async function handleSaveTask(
    taskId: number
  ) {
    const title =
      editingTitle.trim();

    const description =
      editingDescription.trim();

    if (!title) {
      setError(
        "Task title cannot be empty."
      );

      return;
    }

    try {
      setSavingTaskId(taskId);
      setError(null);

      const payload: UpdateTaskRequest = {
        title,
        description:
          description || undefined,
        status:
          editingStatus,
      };

      const updated =
        await updateTask(
          taskId,
          payload
        );

      setTasks((previous) =>
        previous.map((task) =>
          task.id === taskId
            ? updated
            : task
        )
      );

      cancelEditing();

    } catch (err) {
      console.error(
        "Failed to update task:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Failed to update task."
      );

    } finally {
      setSavingTaskId(null);
    }
  }


  // ==========================================================
  // DELETE TASK
  // ==========================================================

  async function handleDeleteTask(
    taskId: number
  ) {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this task?"
      );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingTaskId(taskId);
      setError(null);

      await deleteTask(taskId);

      setTasks((previous) =>
        previous.filter(
          (task) =>
            task.id !== taskId
        )
      );

      if (
        editingTaskId === taskId
      ) {
        cancelEditing();
      }

    } catch (err) {
      console.error(
        "Failed to delete task:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete task."
      );

    } finally {
      setDeletingTaskId(null);
    }
  }


  // ==========================================================
  // STATUS STYLE
  // ==========================================================

  function getStatusClass(
    status?: string
  ) {
    switch (status) {
      case "completed":
        return "bg-emerald-100 text-emerald-700";

      case "in_progress":
        return "bg-blue-100 text-blue-700";

      case "cancelled":
        return "bg-red-100 text-red-700";

      case "todo":
      default:
        return "bg-slate-100 text-slate-700";
    }
  }


  // ==========================================================
  // STATUS LABEL
  // ==========================================================

  function getStatusLabel(
    status?: string
  ) {
    switch (status) {
      case "in_progress":
        return "In Progress";

      case "completed":
        return "Completed";

      case "cancelled":
        return "Cancelled";

      case "todo":
      default:
        return "To Do";
    }
  }


  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <main className="min-h-screen bg-[#0b0e13] px-6 py-10 text-white">

      <div className="mx-auto max-w-6xl">

        {/* ================================================== */}
        {/* HEADER */}
        {/* ================================================== */}

        <div className="mb-8 flex items-start justify-between gap-6">

          <div>

            <div className="mb-2 text-xs uppercase tracking-[0.22em] text-[#73798a]">
              Company OS
            </div>

            <h1 className="text-4xl font-semibold tracking-tight">
              Tasks
            </h1>

            <p className="mt-2 text-sm text-[#8f96a8]">
              Create, manage and track work
              across your workspace.
            </p>

          </div>

          <div className="rounded-full border border-[#2a2f39] bg-[#171a20] px-4 py-2 text-xs text-[#9aa0ae]">
            {tasks.length}{" "}
            {tasks.length === 1
              ? "task"
              : "tasks"}
          </div>

        </div>


        {/* ================================================== */}
        {/* ERROR */}
        {/* ================================================== */}

        {error && (
          <div className="mb-6 rounded-xl border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}


        {/* ================================================== */}
        {/* CREATE TASK */}
        {/* ================================================== */}

        <section className="mb-8 rounded-2xl border border-[#292e38] bg-[#15181e] p-6">

          <div className="mb-5">

            <h2 className="text-lg font-medium">
              Create task
            </h2>

            <p className="mt-1 text-sm text-[#73798a]">
              Add a new task to your workspace.
            </p>

          </div>


          <form
            onSubmit={handleCreateTask}
            className="space-y-4"
          >

            {/* TITLE */}

            <input
              type="text"
              value={newTitle}
              onChange={(event) =>
                setNewTitle(
                  event.target.value
                )
              }
              placeholder="Task title"
              disabled={creating}
              className="
                w-full
                rounded-xl
                border border-[#303641]
                bg-[#0e1116]
                px-4 py-3
                text-sm
                text-white
                outline-none
                placeholder:text-[#555c6c]
                focus:border-[#5965ff]
              "
            />


            {/* DESCRIPTION */}

            <textarea
              value={newDescription}
              onChange={(event) =>
                setNewDescription(
                  event.target.value
                )
              }
              placeholder="Description (optional)"
              disabled={creating}
              rows={3}
              className="
                w-full
                resize-none
                rounded-xl
                border border-[#303641]
                bg-[#0e1116]
                px-4 py-3
                text-sm
                text-white
                outline-none
                placeholder:text-[#555c6c]
                focus:border-[#5965ff]
              "
            />


            {/* BUTTON */}

            <div className="flex justify-end">

              <button
                type="submit"
                disabled={
                  creating ||
                  !newTitle.trim()
                }
                className="
                  rounded-xl
                  bg-white
                  px-5 py-2.5
                  text-sm
                  font-medium
                  text-black
                  transition
                  hover:bg-[#e8e8e8]
                  disabled:cursor-not-allowed
                  disabled:opacity-40
                "
              >
                {creating
                  ? "Creating..."
                  : "Create Task"}
              </button>

            </div>

          </form>

        </section>


        {/* ================================================== */}
        {/* TASK LIST */}
        {/* ================================================== */}

        <section className="rounded-2xl border border-[#292e38] bg-[#15181e]">

          {/* SECTION HEADER */}

          <div className="flex items-center justify-between border-b border-[#292e38] px-6 py-5">

            <div>

              <h2 className="text-lg font-medium">
                Your Tasks
              </h2>

              <p className="mt-1 text-sm text-[#73798a]">
                Tasks belonging to your workspace.
              </p>

            </div>

            <button
              type="button"
              onClick={loadTasks}
              disabled={loading}
              className="
                rounded-lg
                border border-[#303641]
                px-3 py-2
                text-xs
                text-[#a7adbb]
                transition
                hover:bg-[#1c2028]
                disabled:opacity-40
              "
            >
              {loading
                ? "Loading..."
                : "Refresh"}
            </button>

          </div>


          {/* LOADING */}

          {loading && (
            <div className="px-6 py-12 text-center text-sm text-[#73798a]">
              Loading tasks...
            </div>
          )}


          {/* EMPTY */}

          {!loading &&
            tasks.length === 0 && (
              <div className="px-6 py-16 text-center">

                <div className="text-lg text-[#a7adbb]">
                  No tasks yet
                </div>

                <p className="mt-2 text-sm text-[#666d7d]">
                  Create your first task above.
                </p>

              </div>
            )}


          {/* TASKS */}

          {!loading &&
            tasks.length > 0 && (

              <div className="divide-y divide-[#292e38]">

                {tasks.map((task) => (

                  <div
                    key={task.id}
                    className="
                      px-6 py-5
                      transition
                      hover:bg-[#181b22]
                    "
                  >

                    {/* ================================================= */}
                    {/* EDIT MODE */}
                    {/* ================================================= */}

                    {editingTaskId ===
                    task.id ? (

                      <div className="space-y-4">

                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(event) =>
                            setEditingTitle(
                              event.target.value
                            )
                          }
                          className="
                            w-full
                            rounded-xl
                            border border-[#303641]
                            bg-[#0e1116]
                            px-4 py-3
                            text-sm
                            text-white
                            outline-none
                            focus:border-[#5965ff]
                          "
                        />


                        <textarea
                          value={
                            editingDescription
                          }
                          onChange={(event) =>
                            setEditingDescription(
                              event.target.value
                            )
                          }
                          rows={3}
                          className="
                            w-full
                            resize-none
                            rounded-xl
                            border border-[#303641]
                            bg-[#0e1116]
                            px-4 py-3
                            text-sm
                            text-white
                            outline-none
                            focus:border-[#5965ff]
                          "
                        />


                        <div className="flex flex-wrap items-center justify-between gap-3">

                          <select
                            value={editingStatus}
                            onChange={(event) =>
                              setEditingStatus(
                                event.target.value
                              )
                            }
                            className="
                              rounded-lg
                              border border-[#303641]
                              bg-[#0e1116]
                              px-3 py-2
                              text-sm
                              text-white
                              outline-none
                            "
                          >

                            <option value="todo">
                              To Do
                            </option>

                            <option value="in_progress">
                              In Progress
                            </option>

                            <option value="completed">
                              Completed
                            </option>

                            <option value="cancelled">
                              Cancelled
                            </option>

                          </select>


                          <div className="flex gap-2">

                            <button
                              type="button"
                              onClick={
                                cancelEditing
                              }
                              disabled={
                                savingTaskId ===
                                task.id
                              }
                              className="
                                rounded-lg
                                border border-[#303641]
                                px-4 py-2
                                text-sm
                                text-[#a7adbb]
                                hover:bg-[#1c2028]
                              "
                            >
                              Cancel
                            </button>


                            <button
                              type="button"
                              onClick={() =>
                                handleSaveTask(
                                  task.id
                                )
                              }
                              disabled={
                                savingTaskId ===
                                  task.id ||
                                !editingTitle.trim()
                              }
                              className="
                                rounded-lg
                                bg-white
                                px-4 py-2
                                text-sm
                                font-medium
                                text-black
                                disabled:opacity-40
                              "
                            >
                              {savingTaskId ===
                              task.id
                                ? "Saving..."
                                : "Save"}
                            </button>

                          </div>

                        </div>

                      </div>

                    ) : (

                      /* =============================================== */
                      /* NORMAL MODE */
                      /* =============================================== */

                      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

                        <div className="min-w-0 flex-1">

                          <div className="flex flex-wrap items-center gap-3">

                            <h3 className="truncate text-base font-medium text-white">
                              {task.title}
                            </h3>

                            <span
                              className={`
                                rounded-full
                                px-3 py-1
                                text-xs
                                font-medium
                                ${getStatusClass(
                                  task.status
                                )}
                              `}
                            >
                              {getStatusLabel(
                                task.status
                              )}
                            </span>

                          </div>


                          {task.description && (
                            <p className="mt-2 text-sm leading-6 text-[#858c9c]">
                              {task.description}
                            </p>
                          )}


                          <div className="mt-3 flex flex-wrap gap-4 text-xs text-[#555d6d]">

                            <span>
                              Task #{task.id}
                            </span>

                            {task.created_at && (
                              <span>
                                Created{" "}
                                {new Date(
                                  task.created_at
                                ).toLocaleDateString()}
                              </span>
                            )}

                          </div>

                        </div>


                        {/* ACTIONS */}

                        <div className="flex shrink-0 items-center gap-2">

                          <button
                            type="button"
                            onClick={() =>
                              startEditing(
                                task
                              )
                            }
                            className="
                              rounded-lg
                              border border-[#303641]
                              px-3 py-2
                              text-xs
                              text-[#a7adbb]
                              transition
                              hover:bg-[#1c2028]
                              hover:text-white
                            "
                          >
                            Edit
                          </button>


                          <button
                            type="button"
                            onClick={() =>
                              handleDeleteTask(
                                task.id
                              )
                            }
                            disabled={
                              deletingTaskId ===
                              task.id
                            }
                            className="
                              rounded-lg
                              border border-red-900/50
                              px-3 py-2
                              text-xs
                              text-red-400
                              transition
                              hover:bg-red-950/30
                              disabled:opacity-40
                            "
                          >
                            {deletingTaskId ===
                            task.id
                              ? "Deleting..."
                              : "Delete"}
                          </button>

                        </div>

                      </div>

                    )}

                  </div>

                ))}

              </div>

            )}

        </section>

      </div>

    </main>
  );
}