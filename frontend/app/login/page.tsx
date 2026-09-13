"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      await login(email, password);

      router.push("/");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Unable to login."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-ink px-6">
      <div className="w-full max-w-sm">

        {/* =====================================================
            BRAND
        ====================================================== */}

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

        {/* =====================================================
            LOGIN CARD
        ====================================================== */}

        <div className="rounded-xl border border-ink-line bg-ink-soft p-7 shadow-2xl">

          <form
            onSubmit={handleLogin}
            className="space-y-4"
          >

            {/* =================================================
                EMAIL
            ================================================== */}

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

            {/* =================================================
                PASSWORD
            ================================================== */}

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
                placeholder="••••••••"
                required
                disabled={loading}
                className="w-full rounded-lg border border-ink-line bg-ink px-3.5 py-2.5 text-sm text-white outline-none transition placeholder:text-white/30 focus:border-signal disabled:opacity-50"
              />

            </div>

            {/* =================================================
                ERROR
            ================================================== */}

            {error && (
              <div
                className="rounded-lg px-3.5 py-2.5 text-sm"
                style={{
                  background: "rgba(176,54,44,0.15)",
                  color: "#ff8a80",
                }}
              >
                {error}
              </div>
            )}

            {/* =================================================
                LOGIN BUTTON
            ================================================== */}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-signal px-4 py-2.5 text-sm font-medium text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Signing in…"
                : "Sign in"}
            </button>

          </form>

          {/* ===================================================
              REGISTER LINK
          ==================================================== */}

          <div className="mt-6 border-t border-ink-line pt-5 text-center">

            <p className="text-sm text-white/40">
              Don't have an account?
            </p>

            <button
              type="button"
              onClick={() => router.push("/register")}
              className="mt-1 text-sm font-medium text-signal transition hover:opacity-80"
            >
              Create an account
            </button>

          </div>

        </div>

      </div>
    </main>
  );
}