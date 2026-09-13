"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, register } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRegister(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");

    // Password confirmation
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    // Backend requires minimum 8 characters
    if (password.length < 8) {
      setError(
        "Password must be at least 8 characters."
      );
      return;
    }

    setLoading(true);

    try {
      await register(
        name,
        email,
        password
      );

      // register() already stores the JWT
      // in localStorage.

      router.push("/");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Unable to create account."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-ink px-6">
      <div className="w-full max-w-sm">

        {/* BRAND */}
        <div className="mb-8 flex flex-col items-center text-center">

          <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-signal font-display text-base font-bold text-white">
            C
          </div>

          <h1 className="font-display text-2xl font-semibold tracking-tight text-white">
            Company OS
          </h1>

          <p className="mt-1.5 font-mono text-xs text-white/40">
            company knowledge &middot; retrieved &amp; cited
          </p>

        </div>

        {/* REGISTER CARD */}
        <div className="rounded-xl border border-ink-line bg-ink-soft p-7 shadow-2xl">

          <div className="mb-6">
            <h2 className="font-display text-lg font-semibold text-white">
              Create your account
            </h2>

            <p className="mt-1 text-sm text-white/40">
              Set up your Company OS workspace.
            </p>
          </div>

          <form
            onSubmit={handleRegister}
            className="space-y-4"
          >

            {/* NAME */}
            <div>
              <label className="mb-1.5 block font-mono text-[11px] uppercase tracking-wide text-white/50">
                Name
              </label>

              <input
                type="text"
                value={name}
                onChange={(event) =>
                  setName(event.target.value)
                }
                placeholder="Your name"
                required
                disabled={loading}
                className="w-full rounded-lg border border-ink-line bg-ink px-3.5 py-2.5 text-sm text-white outline-none transition placeholder:text-white/30 focus:border-signal disabled:opacity-50"
              />
            </div>

            {/* EMAIL */}
            <div>
              <label className="mb-1.5 block font-mono text-[11px] uppercase tracking-wide text-white/50">
                Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="you@company.com"
                required
                disabled={loading}
                className="w-full rounded-lg border border-ink-line bg-ink px-3.5 py-2.5 text-sm text-white outline-none transition placeholder:text-white/30 focus:border-signal disabled:opacity-50"
              />
            </div>

            {/* PASSWORD */}
            <div>
              <label className="mb-1.5 block font-mono text-[11px] uppercase tracking-wide text-white/50">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Minimum 8 characters"
                required
                disabled={loading}
                minLength={8}
                className="w-full rounded-lg border border-ink-line bg-ink px-3.5 py-2.5 text-sm text-white outline-none transition placeholder:text-white/30 focus:border-signal disabled:opacity-50"
              />
            </div>

            {/* CONFIRM PASSWORD */}
            <div>
              <label className="mb-1.5 block font-mono text-[11px] uppercase tracking-wide text-white/50">
                Confirm password
              </label>

              <input
                type="password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                placeholder="Repeat your password"
                required
                disabled={loading}
                minLength={8}
                className="w-full rounded-lg border border-ink-line bg-ink px-3.5 py-2.5 text-sm text-white outline-none transition placeholder:text-white/30 focus:border-signal disabled:opacity-50"
              />
            </div>

            {/* ERROR */}
            {error && (
              <div
                className="rounded-lg px-3.5 py-2.5 text-sm"
                style={{
                  background:
                    "rgba(176,54,44,0.15)",
                  color: "#ff8a80",
                }}
              >
                {error}
              </div>
            )}

            {/* SUBMIT */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-signal px-4 py-2.5 text-sm font-medium text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Creating account…"
                : "Create account"}
            </button>

          </form>

          {/* LOGIN LINK */}
          <div className="mt-6 border-t border-ink-line pt-5 text-center">

            <p className="text-sm text-white/40">
              Already have an account?
            </p>

            <button
              type="button"
              onClick={() =>
                router.push("/login")
              }
              className="mt-1 text-sm font-medium text-signal transition hover:opacity-80"
            >
              Sign in
            </button>

          </div>

        </div>
      </div>
    </main>
  );
}