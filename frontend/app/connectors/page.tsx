"use client";

import React, { useEffect, useState } from "react";

// ============================================================
// API CONFIG
// ============================================================

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

function apiUrl(path: string) {
  return `${API_BASE}${path}`;
}

// ============================================================
// AUTH
// ============================================================

function getAuthToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("token") ||
    localStorage.getItem("auth_token") ||
    localStorage.getItem("jwt") ||
    null
  );
}

// ============================================================
// AUTHENTICATED FETCH
// ============================================================

async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
) {
  const token = getAuthToken();

  const headers = new Headers(
    options.headers || {}
  );

  headers.set(
    "Content-Type",
    "application/json"
  );

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`
    );
  }

  return fetch(url, {
    ...options,
    headers,
    credentials: "include",
  });
}

// ============================================================
// TYPES
// ============================================================

type Connector = {
  name: string;
  display_name: string;
};

type ConnectorState = {
  connected: boolean;
  loading: boolean;
  testing: boolean;
  disconnecting: boolean;
  error: string;
  message: string;
};

type GitHubRecord = {
  id?: number;
  number?: number;
  name?: string;
  title?: string;
  description?: string;
  text?: string;
  state?: string;
  url?: string;
  author?: string;
  created_at?: string;
  updated_at?: string;
  type?: string;
  labels?: string[];
  repository?: string;
};

type IngestResult = {
  success?: boolean;
  message?: string;
  document_id?: number;
  filename?: string;
  total_chunks?: number;
  embedding_dimension?: number;
  [key: string]: any;
};

// ============================================================
// CONNECTOR DESCRIPTIONS
// ============================================================

const connectorDescriptions: Record<
  string,
  string
> = {
  github:
    "Connect GitHub to retrieve repositories, issues and pull requests.",

  slack:
    "Connect Slack to retrieve company conversations and messages.",

  google_drive:
    "Connect Google Drive to access company documents and files.",

  email:
    "Connect Email to access company communication.",

  confluence:
    "Connect Confluence to access company knowledge and documentation.",

  jira:
    "Bring projects, tickets, issues and engineering workflows into Company OS.",
};

// ============================================================
// CONNECTOR DISPLAY ORDER
// ============================================================

const CONNECTOR_ORDER = [
  "github",
  "slack",
  "google_drive",
  "email",
  "confluence",
  "jira",
];

// ============================================================
// INITIAL CONNECTOR STATE
// ============================================================

function createInitialState(): ConnectorState {
  return {
    connected: false,
    loading: false,
    testing: false,
    disconnecting: false,
    error: "",
    message: "",
  };
}

// ============================================================
// PAGE
// ============================================================

export default function ConnectorsPage() {
  // ==========================================================
  // CONNECTORS
  // ==========================================================

  const [connectors, setConnectors] =
    useState<Connector[]>([]);

  const [connectorStates, setConnectorStates] =
    useState<
      Record<string, ConnectorState>
    >({});

  const [credentials, setCredentials] =
    useState<
      Record<
        string,
        Record<string, string>
      >
    >({});

  const [loadingConnectors, setLoadingConnectors] =
    useState(true);

  const [pageError, setPageError] =
    useState("");

  // ==========================================================
  // GITHUB STATE
  // ==========================================================

  const [repository, setRepository] =
    useState("octocat/Hello-World");

  const [githubState, setGithubState] =
    useState("open");

  const [githubLimit, setGithubLimit] =
    useState(10);

  const [githubRecords, setGithubRecords] =
    useState<GitHubRecord[]>([]);

  const [githubFetching, setGithubFetching] =
    useState(false);

  const [githubIngesting, setGithubIngesting] =
    useState(false);

  const [githubIngestResult, setGithubIngestResult] =
    useState<IngestResult | null>(null);

  // ==========================================================
  // LOAD CONNECTORS
  // ==========================================================

  useEffect(() => {
    loadConnectors();
  }, []);

  async function loadConnectors() {
    try {
      setLoadingConnectors(true);
      setPageError("");

      const response =
        await authenticatedFetch(
          apiUrl("/connectors"),
          {
            method: "GET",
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `Failed to load connectors (${response.status})`
        );
      }

      let loadedConnectors: Connector[] =
        Array.isArray(data?.connectors)
          ? data.connectors
          : [];

      // ------------------------------------------------------
      // Keep the expected connector list.
      // This prevents GitHub-only backend changes from
      // removing the other cards from the UI.
      // ------------------------------------------------------

      const existingNames = new Set(
        loadedConnectors.map(
          (connector) => connector.name
        )
      );

      for (const name of CONNECTOR_ORDER) {
        if (!existingNames.has(name)) {
          loadedConnectors.push({
            name,
            display_name:
              name === "github"
                ? "GitHub"
                : name === "google_drive"
                ? "Google Drive"
                : name === "confluence"
                ? "Confluence"
                : name === "slack"
                ? "Slack"
                : name === "email"
                ? "Email"
                : "Jira",
          });
        }
      }

      // ------------------------------------------------------
      // Sort
      // ------------------------------------------------------

      loadedConnectors.sort(
        (a, b) =>
          CONNECTOR_ORDER.indexOf(a.name) -
          CONNECTOR_ORDER.indexOf(b.name)
      );

      setConnectors(
        loadedConnectors
      );

      // ------------------------------------------------------
      // Initialize states
      // ------------------------------------------------------

      const initialStates: Record<
        string,
        ConnectorState
      > = {};

      for (
        const connector of loadedConnectors
      ) {
        initialStates[
          connector.name
        ] = createInitialState();
      }

      setConnectorStates(
        initialStates
      );
    } catch (error: any) {
      console.error(
        "Load connectors error:",
        error
      );

      setPageError(
        error?.message ||
          "Failed to load connectors."
      );
    } finally {
      setLoadingConnectors(false);
    }
  }

  // ==========================================================
  // UPDATE CONNECTOR STATE
  // ==========================================================

  function updateConnectorState(
    name: string,
    updates: Partial<ConnectorState>
  ) {
    setConnectorStates(
      (previous) => ({
        ...previous,

        [name]: {
          ...(previous[name] ||
            createInitialState()),
          ...updates,
        },
      })
    );
  }

  // ==========================================================
  // UPDATE CREDENTIAL
  // ==========================================================

  function updateCredential(
    connectorName: string,
    key: string,
    value: string
  ) {
    setCredentials(
      (previous) => ({
        ...previous,

        [connectorName]: {
          ...(previous[
            connectorName
          ] || {}),

          [key]: value,
        },
      })
    );
  }

  // ==========================================================
  // GET CREDENTIAL
  // ==========================================================

  function getCredential(
    connectorName: string
  ) {
    return (
      credentials[
        connectorName
      ] || {}
    );
  }

  // ==========================================================
  // CONNECT GENERIC CONNECTOR
  // ==========================================================

  async function handleConnect(
    connector: Connector
  ) {
    const name =
      connector.name;

    // GitHub has its own custom connection
    // flow because we also need the username.
    if (name === "github") {
      await handleGitHubConnect();
      return;
    }

    const connectorCredentials =
      getCredential(name);

    updateConnectorState(
      name,
      {
        loading: true,
        error: "",
        message: "",
      }
    );

    try {
      const response =
        await authenticatedFetch(
          apiUrl(
            `/connectors/${name}/connect`
          ),
          {
            method: "POST",

            body: JSON.stringify({
              credentials:
                connectorCredentials,
            }),
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `Failed to connect ${connector.display_name} (${response.status})`
        );
      }

      updateConnectorState(
        name,
        {
          connected: true,
          loading: false,
          message:
            data?.message ||
            `${connector.display_name} connected successfully.`,
        }
      );
    } catch (error: any) {
      console.error(
        `${name} connect error:`,
        error
      );

      updateConnectorState(
        name,
        {
          connected: false,
          loading: false,
          error:
            error?.message ||
            `Failed to connect ${connector.display_name}.`,
        }
      );
    }
  }

  // ==========================================================
  // GITHUB CONNECT
  // ==========================================================

  async function handleGitHubConnect() {
    const token =
      getCredential("github")
        .token?.trim() || "";

    updateConnectorState(
      "github",
      {
        loading: true,
        error: "",
        message: "",
      }
    );

    try {
      if (!token) {
        throw new Error(
          "Please enter your GitHub token."
        );
      }

      const response =
        await authenticatedFetch(
          apiUrl(
            "/connectors/github/connect"
          ),
          {
            method: "POST",

            body: JSON.stringify({
              credentials: {
                token,
              },
            }),
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `GitHub connection failed (${response.status})`
        );
      }

      updateConnectorState(
        "github",
        {
          connected: true,
          loading: false,
          message:
            data?.message ||
            data?.username
              ? `GitHub connected as ${
                  data?.username ||
                  "your account"
                }.`
              : "GitHub connected successfully.",
        }
      );

      // Test immediately after connection.
      await handleGitHubTest();
    } catch (error: any) {
      console.error(
        "GitHub connect error:",
        error
      );

      updateConnectorState(
        "github",
        {
          connected: false,
          loading: false,
          error:
            error?.message ||
            "Failed to connect GitHub.",
        }
      );
    }
  }

  // ==========================================================
  // TEST GENERIC CONNECTOR
  // ==========================================================

  async function handleTest(
    connector: Connector
  ) {
    const name =
      connector.name;

    if (name === "github") {
      await handleGitHubTest();
      return;
    }

    updateConnectorState(
      name,
      {
        testing: true,
        error: "",
        message: "",
      }
    );

    try {
      const response =
        await authenticatedFetch(
          apiUrl(
            `/connectors/${name}/test`
          ),
          {
            method: "POST",
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `Connection test failed (${response.status})`
        );
      }

      const connected =
        data?.connected === true ||
        data?.status ===
          "connected" ||
        data?.status ===
          "healthy";

      updateConnectorState(
        name,
        {
          connected,
          testing: false,
          message: connected
            ? "Connection is healthy."
            : "Connector is not connected.",
        }
      );
    } catch (error: any) {
      console.error(
        `${name} test error:`,
        error
      );

      updateConnectorState(
        name,
        {
          testing: false,
          error:
            error?.message ||
            "Connection test failed.",
        }
      );
    }
  }

  // ==========================================================
  // GITHUB TEST
  // ==========================================================

  async function handleGitHubTest() {
    const token =
      getCredential("github")
        .token?.trim() || "";

    updateConnectorState(
      "github",
      {
        testing: true,
        error: "",
        message: "",
      }
    );

    try {
      if (!token) {
        throw new Error(
          "Please enter your GitHub token."
        );
      }

      const response =
        await authenticatedFetch(
          apiUrl(
            "/connectors/github/test"
          ),
          {
            method: "POST",

            body: JSON.stringify({
              credentials: {
                token,
              },
            }),
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `GitHub test failed (${response.status})`
        );
      }

      const connected =
        data?.connected === true ||
        data?.status ===
          "connected" ||
        data?.status ===
          "healthy";

      updateConnectorState(
        "github",
        {
          connected,
          testing: false,
          message:
            connected
              ? data?.username
                ? `GitHub connected as ${data.username}.`
                : "GitHub connection is healthy."
              : "GitHub is not connected.",
        }
      );
    } catch (error: any) {
      console.error(
        "GitHub test error:",
        error
      );

      updateConnectorState(
        "github",
        {
          connected: false,
          testing: false,
          error:
            error?.message ||
            "GitHub connection test failed.",
        }
      );
    }
  }

  // ==========================================================
  // DISCONNECT GENERIC
  // ==========================================================

  async function handleDisconnect(
    connector: Connector
  ) {
    const name =
      connector.name;

    if (name === "github") {
      await handleGitHubDisconnect();
      return;
    }

    updateConnectorState(
      name,
      {
        disconnecting: true,
        error: "",
        message: "",
      }
    );

    try {
      const response =
        await authenticatedFetch(
          apiUrl(
            `/connectors/${name}/disconnect`
          ),
          {
            method: "POST",
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `Disconnect failed (${response.status})`
        );
      }

      updateConnectorState(
        name,
        {
          connected: false,
          disconnecting: false,
          message:
            data?.message ||
            `${connector.display_name} disconnected.`,
        }
      );
    } catch (error: any) {
      console.error(
        `${name} disconnect error:`,
        error
      );

      updateConnectorState(
        name,
        {
          disconnecting: false,
          error:
            error?.message ||
            `Failed to disconnect ${connector.display_name}.`,
        }
      );
    }
  }

  // ==========================================================
  // GITHUB DISCONNECT
  // ==========================================================

  async function handleGitHubDisconnect() {
    updateConnectorState(
      "github",
      {
        disconnecting: true,
        error: "",
        message: "",
      }
    );

    try {
      /*
       * Your current backend route is:
       *
       * DELETE /connectors/{connector_name}
       *
       * Therefore GitHub uses DELETE here.
       */

      const response =
        await authenticatedFetch(
          apiUrl(
            "/connectors/github"
          ),
          {
            method: "DELETE",
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `GitHub disconnect failed (${response.status})`
        );
      }

      updateConnectorState(
        "github",
        {
          connected: false,
          disconnecting: false,
          message:
            data?.message ||
            "GitHub disconnected.",
        }
      );

      setGithubRecords([]);
      setGithubIngestResult(null);
    } catch (error: any) {
      console.error(
        "GitHub disconnect error:",
        error
      );

      updateConnectorState(
        "github",
        {
          disconnecting: false,
          error:
            error?.message ||
            "Failed to disconnect GitHub.",
        }
      );
    }
  }

  // ==========================================================
  // GITHUB FETCH
  // ==========================================================

  async function handleGitHubFetch() {
    setGithubFetching(true);

    updateConnectorState(
      "github",
      {
        error: "",
        message: "",
      }
    );

    setGithubRecords([]);

    try {
      const token =
        getCredential("github")
          .token?.trim() || "";

      if (!token) {
        throw new Error(
          "Please connect GitHub first."
        );
      }

      if (!repository.trim()) {
        throw new Error(
          "Repository is required."
        );
      }

      const response =
        await authenticatedFetch(
          apiUrl(
            "/connectors/github/fetch"
          ),
          {
            method: "POST",

            body: JSON.stringify({
              credentials: {
                token,
              },

              options: {
                repository:
                  repository.trim(),

                state:
                  githubState,

                limit:
                  Number(
                    githubLimit
                  ),
              },
            }),
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `GitHub fetch failed (${response.status})`
        );
      }

      const fetchedRecords =
        Array.isArray(
          data?.records
        )
          ? data.records
          : [];

      setGithubRecords(
        fetchedRecords
      );

      updateConnectorState(
        "github",
        {
          message:
            `Fetched ${fetchedRecords.length} GitHub records.`,
        }
      );
    } catch (error: any) {
      console.error(
        "GitHub fetch error:",
        error
      );

      updateConnectorState(
        "github",
        {
          error:
            error?.message ||
            "Failed to fetch GitHub data.",
        }
      );
    } finally {
      setGithubFetching(false);
    }
  }

  // ==========================================================
  // GITHUB → RAG
  // ==========================================================

  async function handleGitHubIngest() {
    setGithubIngesting(true);

    updateConnectorState(
      "github",
      {
        error: "",
        message: "",
      }
    );

    setGithubIngestResult(null);

    try {
      const token =
        getCredential("github")
          .token?.trim() || "";

      if (!token) {
        throw new Error(
          "Please connect GitHub first."
        );
      }

      if (!repository.trim()) {
        throw new Error(
          "Repository is required."
        );
      }

      const authToken =
        getAuthToken();

      if (!authToken) {
        throw new Error(
          "Company OS session expired. Please log in again."
        );
      }

      /*
       * IMPORTANT:
       *
       * This endpoint is NOT the generic connector
       * fetch endpoint.
       *
       * Your backend explicitly defines:
       *
       * POST /connectors/github/ingest
       */

      const response =
        await authenticatedFetch(
          apiUrl(
            "/connectors/github/ingest"
          ),
          {
            method: "POST",

            body: JSON.stringify({
              credentials: {
                token,
              },

              repository:
                repository.trim(),

              state:
                githubState,

              limit:
                Number(
                  githubLimit
                ),
            }),
          }
        );

      const data =
        await response.json();

      console.log(
        "GitHub ingestion response:",
        data
      );

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `GitHub ingestion failed (${response.status})`
        );
      }

      setGithubIngestResult(
        data
      );

      updateConnectorState(
        "github",
        {
          message:
            data?.message ||
            "GitHub data successfully added to RAG.",
        }
      );
    } catch (error: any) {
      console.error(
        "GitHub ingestion error:",
        error
      );

      updateConnectorState(
        "github",
        {
          error:
            error?.message ||
            "GitHub ingestion failed.",
        }
      );
    } finally {
      setGithubIngesting(false);
    }
  }

  // ==========================================================
  // LOADING
  // ==========================================================

  if (loadingConnectors) {
    return (
      <main
        style={{
          minHeight: "100vh",
          padding: "40px",
          background: "#f8fafc",
          fontFamily:
            "Arial, Helvetica, sans-serif",
        }}
      >
        <h1
          style={{
            fontSize: "32px",
            fontWeight: 700,
          }}
        >
          Connectors
        </h1>

        <p
          style={{
            color: "#64748b",
          }}
        >
          Loading connectors...
        </p>
      </main>
    );
  }

  // ==========================================================
  // PAGE
  // ==========================================================

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        padding: "40px 20px",
        fontFamily:
          "Arial, Helvetica, sans-serif",
        color: "#111827",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
        }}
      >
        {/* ================================================== */}
        {/* HEADER */}
        {/* ================================================== */}

        <div
          style={{
            marginBottom: "32px",
          }}
        >
          <h1
            style={{
              fontSize: "36px",
              margin: 0,
              marginBottom: "10px",
            }}
          >
            Connectors
          </h1>

          <p
            style={{
              margin: 0,
              color: "#64748b",
              fontSize: "17px",
            }}
          >
            Connect Company OS to your
            external company systems.
          </p>
        </div>

        {/* ================================================== */}
        {/* PAGE ERROR */}
        {/* ================================================== */}

        {pageError && (
          <div
            style={{
              marginBottom: "25px",
              padding: "16px",
              borderRadius: "12px",
              border:
                "1px solid #fecaca",
              background: "#fef2f2",
              color: "#b91c1c",
            }}
          >
            {pageError}
          </div>
        )}

        {/* ================================================== */}
        {/* CONNECTOR GRID */}
        {/* ================================================== */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(480px, 1fr))",
            gap: "24px",
          }}
        >
          {connectors.map(
            (connector) => {
              const name =
                connector.name;

              const state =
                connectorStates[
                  name
                ] ||
                createInitialState();

              const isGitHub =
                name === "github";

              const isJira =
                name === "jira";

              const credential =
                getCredential(name);

              return (
                <section
                  key={name}
                  style={{
                    background:
                      "white",
                    border:
                      "1px solid #d1d5db",
                    borderRadius:
                      "18px",
                    padding:
                      "30px",
                    boxShadow:
                      "0 8px 25px rgba(0,0,0,0.04)",
                  }}
                >
                  {/* ======================================== */}
                  {/* TITLE */}
                  {/* ======================================== */}

                  <div
                    style={{
                      display:
                        "flex",
                      justifyContent:
                        "space-between",
                      alignItems:
                        "flex-start",
                      gap: "20px",
                      marginBottom:
                        "25px",
                    }}
                  >
                    <div>
                      <h2
                        style={{
                          fontSize:
                            "26px",
                          margin: 0,
                          marginBottom:
                            "8px",
                        }}
                      >
                        {
                          connector.display_name
                        }
                      </h2>

                      <p
                        style={{
                          margin: 0,
                          color:
                            "#64748b",
                          fontSize:
                            "15px",
                          lineHeight:
                            1.5,
                        }}
                      >
                        {connectorDescriptions[
                          name
                        ] ||
                          "Connect this service to Company OS."}
                      </p>
                    </div>

                    {/* STATUS */}

                    <span
                      style={{
                        flexShrink: 0,
                        padding:
                          "8px 14px",
                        borderRadius:
                          "999px",
                        background:
                          state.connected
                            ? "#dcfce7"
                            : "#f1f5f9",
                        color:
                          state.connected
                            ? "#166534"
                            : "#475569",
                        fontSize:
                          "13px",
                        fontWeight:
                          600,
                      }}
                    >
                      {state.connected
                        ? "Connected"
                        : "Not connected"}
                    </span>
                  </div>

                  {/* ======================================== */}
                  {/* JIRA COMING SOON */}
                  {/* ======================================== */}

                  {isJira && (
                    <div
                      style={{
                        padding:
                          "15px",
                        borderRadius:
                          "10px",
                        background:
                          "#f8fafc",
                        border:
                          "1px solid #e2e8f0",
                        color:
                          "#64748b",
                        marginBottom:
                          "20px",
                      }}
                    >
                      Jira integration is
                      coming soon.
                    </div>
                  )}

                  {/* ======================================== */}
                  {/* CREDENTIAL INPUT */}
                  {/* ======================================== */}

                  {!isJira &&
                    !state.connected && (
                      <div
                        style={{
                          marginBottom:
                            "20px",
                        }}
                      >
                        <label
                          style={{
                            display:
                              "block",
                            fontSize:
                              "15px",
                            fontWeight:
                              600,
                            marginBottom:
                              "9px",
                          }}
                        >
                          Credentials
                        </label>

                        <input
                          type="password"
                          value={
                            credential.token ||
                            ""
                          }
                          onChange={(
                            event
                          ) =>
                            updateCredential(
                              name,
                              "token",
                              event
                                .target
                                .value
                            )
                          }
                          placeholder={
                            name ===
                            "github"
                              ? "GitHub Personal Access Token"
                              : "Credential / token"
                          }
                          style={{
                            width:
                              "100%",
                            boxSizing:
                              "border-box",
                            padding:
                              "14px",
                            border:
                              "1px solid #cbd5e1",
                            borderRadius:
                              "10px",
                            fontSize:
                              "15px",
                          }}
                        />
                      </div>
                    )}

                  {/* ======================================== */}
                  {/* ACTIONS */}
                  {/* ======================================== */}

                  {!isJira && (
                    <div
                      style={{
                        display:
                          "flex",
                        flexWrap:
                          "wrap",
                        gap: "10px",
                        marginBottom:
                          "20px",
                      }}
                    >
                      {/* CONNECT */}

                      {!state.connected && (
                        <button
                          type="button"
                          onClick={() =>
                            handleConnect(
                              connector
                            )
                          }
                          disabled={
                            state.loading
                          }
                          style={{
                            background:
                              state.loading
                                ? "#64748b"
                                : "#000000",
                            color:
                              "white",
                            border:
                              "none",
                            borderRadius:
                              "10px",
                            padding:
                              "13px 22px",
                            fontSize:
                              "15px",
                            fontWeight:
                              600,
                            cursor:
                              state.loading
                                ? "not-allowed"
                                : "pointer",
                          }}
                        >
                          {state.loading
                            ? "Connecting..."
                            : "Connect"}
                        </button>
                      )}

                      {/* TEST */}

                      {state.connected && (
                        <button
                          type="button"
                          onClick={() =>
                            handleTest(
                              connector
                            )
                          }
                          disabled={
                            state.testing
                          }
                          style={{
                            background:
                              "white",
                            color:
                              "#111827",
                            border:
                              "1px solid #cbd5e1",
                            borderRadius:
                              "10px",
                            padding:
                              "13px 22px",
                            fontSize:
                              "15px",
                            fontWeight:
                              600,
                            cursor:
                              state.testing
                                ? "not-allowed"
                                : "pointer",
                          }}
                        >
                          {state.testing
                            ? "Testing..."
                            : "Test Connection"}
                        </button>
                      )}

                      {/* DISCONNECT */}

                      {state.connected && (
                        <button
                          type="button"
                          onClick={() =>
                            handleDisconnect(
                              connector
                            )
                          }
                          disabled={
                            state.disconnecting
                          }
                          style={{
                            background:
                              "white",
                            color:
                              "#dc2626",
                            border:
                              "1px solid #fecaca",
                            borderRadius:
                              "10px",
                            padding:
                              "13px 22px",
                            fontSize:
                              "15px",
                            fontWeight:
                              600,
                            cursor:
                              state.disconnecting
                                ? "not-allowed"
                                : "pointer",
                          }}
                        >
                          {state.disconnecting
                            ? "Disconnecting..."
                            : "Disconnect"}
                        </button>
                      )}
                    </div>
                  )}

                  {/* ======================================== */}
                  {/* GITHUB FETCH SECTION */}
                  {/* ======================================== */}

                  {isGitHub &&
                    state.connected && (
                      <div
                        style={{
                          marginTop:
                            "25px",
                          paddingTop:
                            "25px",
                          borderTop:
                            "1px solid #e2e8f0",
                        }}
                      >
                        <h3
                          style={{
                            fontSize:
                              "23px",
                            margin:
                              "0 0 8px",
                          }}
                        >
                          Fetch GitHub Data
                        </h3>

                        <p
                          style={{
                            color:
                              "#64748b",
                            fontSize:
                              "15px",
                            margin:
                              "0 0 20px",
                          }}
                        >
                          Fetch issues and
                          pull requests from
                          a repository.
                        </p>

                        {/* REPOSITORY */}

                        <label
                          style={{
                            display:
                              "block",
                            fontWeight:
                              600,
                            marginBottom:
                              "9px",
                          }}
                        >
                          Repository
                        </label>

                        <input
                          type="text"
                          value={
                            repository
                          }
                          onChange={(
                            event
                          ) =>
                            setRepository(
                              event
                                .target
                                .value
                            )
                          }
                          placeholder="owner/repository"
                          style={{
                            width:
                              "100%",
                            boxSizing:
                              "border-box",
                            padding:
                              "14px",
                            border:
                              "1px solid #cbd5e1",
                            borderRadius:
                              "10px",
                            fontSize:
                              "15px",
                            marginBottom:
                              "18px",
                          }}
                        />

                        {/* STATE + LIMIT */}

                        <div
                          style={{
                            display:
                              "flex",
                            gap: "15px",
                            flexWrap:
                              "wrap",
                            marginBottom:
                              "20px",
                          }}
                        >
                          <div>
                            <label
                              style={{
                                display:
                                  "block",
                                fontWeight:
                                  600,
                                marginBottom:
                                  "8px",
                              }}
                            >
                              State
                            </label>

                            <select
                              value={
                                githubState
                              }
                              onChange={(
                                event
                              ) =>
                                setGithubState(
                                  event
                                    .target
                                    .value
                                )
                              }
                              style={{
                                padding:
                                  "13px 15px",
                                border:
                                  "1px solid #cbd5e1",
                                borderRadius:
                                  "10px",
                                fontSize:
                                  "15px",
                              }}
                            >
                              <option value="open">
                                Open
                              </option>

                              <option value="closed">
                                Closed
                              </option>

                              <option value="all">
                                All
                              </option>
                            </select>
                          </div>

                          <div>
                            <label
                              style={{
                                display:
                                  "block",
                                fontWeight:
                                  600,
                                marginBottom:
                                  "8px",
                              }}
                            >
                              Limit
                            </label>

                            <input
                              type="number"
                              min={1}
                              max={100}
                              value={
                                githubLimit
                              }
                              onChange={(
                                event
                              ) =>
                                setGithubLimit(
                                  Math.min(
                                    100,
                                    Math.max(
                                      1,
                                      Number(
                                        event
                                          .target
                                          .value
                                      )
                                    )
                                  )
                                )
                              }
                              style={{
                                width:
                                  "100px",
                                padding:
                                  "13px",
                                border:
                                  "1px solid #cbd5e1",
                                borderRadius:
                                  "10px",
                                fontSize:
                                  "15px",
                              }}
                            />
                          </div>
                        </div>

                        {/* BUTTONS */}

                        <div
                          style={{
                            display:
                              "flex",
                            flexWrap:
                              "wrap",
                            gap: "10px",
                          }}
                        >
                          <button
                            type="button"
                            onClick={
                              handleGitHubFetch
                            }
                            disabled={
                              githubFetching ||
                              githubIngesting
                            }
                            style={{
                              background:
                                githubFetching
                                  ? "#64748b"
                                  : "#111827",
                              color:
                                "white",
                              border:
                                "none",
                              borderRadius:
                                "10px",
                              padding:
                                "13px 22px",
                              fontSize:
                                "15px",
                              fontWeight:
                                600,
                            }}
                          >
                            {githubFetching
                              ? "Fetching..."
                              : "Fetch"}
                          </button>

                          <button
                            type="button"
                            onClick={
                              handleGitHubIngest
                            }
                            disabled={
                              githubIngesting
                            }
                            style={{
                              background:
                                githubIngesting
                                  ? "#64748b"
                                  : "#4f46e5",
                              color:
                                "white",
                              border:
                                "none",
                              borderRadius:
                                "10px",
                              padding:
                                "13px 22px",
                              fontSize:
                                "15px",
                              fontWeight:
                                600,
                            }}
                          >
                            {githubIngesting
                              ? "Adding to RAG..."
                              : "Fetch & Add to RAG"}
                          </button>
                        </div>
                      </div>
                    )}

                  {/* ======================================== */}
                  {/* GITHUB RAG RESULT */}
                  {/* ======================================== */}

                  {isGitHub &&
                    githubIngestResult && (
                      <div
                        style={{
                          marginTop:
                            "22px",
                          padding:
                            "18px",
                          background:
                            "#eef2ff",
                          border:
                            "1px solid #c7d2fe",
                          borderRadius:
                            "12px",
                        }}
                      >
                        <strong>
                          RAG Ingestion Complete
                        </strong>

                        {githubIngestResult
                          .document_id && (
                          <p>
                            Document ID:{" "}
                            {
                              githubIngestResult
                                .document_id
                            }
                          </p>
                        )}

                        {githubIngestResult
                          .total_chunks !==
                          undefined && (
                          <p>
                            Chunks:{" "}
                            {
                              githubIngestResult
                                .total_chunks
                            }
                          </p>
                        )}

                        {githubIngestResult
                          .embedding_dimension !==
                          undefined && (
                          <p>
                            Embedding dimension:{" "}
                            {
                              githubIngestResult
                                .embedding_dimension
                            }
                          </p>
                        )}
                      </div>
                    )}

                  {/* ======================================== */}
                  {/* GITHUB RECORDS */}
                  {/* ======================================== */}

                  {isGitHub &&
                    githubRecords.length >
                      0 && (
                      <div
                        style={{
                          marginTop:
                            "25px",
                          paddingTop:
                            "25px",
                          borderTop:
                            "1px solid #e2e8f0",
                        }}
                      >
                        <h3
                          style={{
                            fontSize:
                              "20px",
                            margin:
                              "0 0 15px",
                          }}
                        >
                          GitHub Records (
                          {
                            githubRecords.length
                          }
                          )
                        </h3>

                        <div
                          style={{
                            display:
                              "flex",
                            flexDirection:
                              "column",
                            gap:
                              "12px",
                          }}
                        >
                          {githubRecords.map(
                            (
                              record,
                              index
                            ) => (
                              <div
                                key={
                                  record.id ??
                                  index
                                }
                                style={{
                                  border:
                                    "1px solid #e2e8f0",
                                  borderRadius:
                                    "10px",
                                  padding:
                                    "15px",
                                }}
                              >
                                <div
                                  style={{
                                    display:
                                      "flex",
                                    justifyContent:
                                      "space-between",
                                    gap:
                                      "10px",
                                  }}
                                >
                                  <div>
                                    <strong>
                                      {record.title ||
                                        record.name ||
                                        "Untitled"}
                                    </strong>

                                    <div
                                      style={{
                                        color:
                                          "#64748b",
                                        fontSize:
                                          "13px",
                                        marginTop:
                                          "5px",
                                      }}
                                    >
                                      {record.type ||
                                        "issue"}

                                      {record.number
                                        ? ` #${record.number}`
                                        : ""}

                                      {record.author
                                        ? ` • ${record.author}`
                                        : ""}
                                    </div>
                                  </div>

                                  {record.state && (
                                    <span
                                      style={{
                                        padding:
                                          "5px 9px",
                                        borderRadius:
                                          "999px",
                                        background:
                                          record.state ===
                                          "open"
                                            ? "#dcfce7"
                                            : "#f1f5f9",
                                        color:
                                          record.state ===
                                          "open"
                                            ? "#166534"
                                            : "#475569",
                                        fontSize:
                                          "12px",
                                      }}
                                    >
                                      {
                                        record.state
                                      }
                                    </span>
                                  )}
                                </div>

                                {record.description && (
                                  <p
                                    style={{
                                      color:
                                        "#475569",
                                      fontSize:
                                        "14px",
                                      lineHeight:
                                        1.5,
                                    }}
                                  >
                                    {
                                      record.description
                                    }
                                  </p>
                                )}

                                {record.url && (
                                  <a
                                    href={
                                      record.url
                                    }
                                    target="_blank"
                                    rel="noreferrer"
                                    style={{
                                      color:
                                        "#4f46e5",
                                      fontWeight:
                                        600,
                                      fontSize:
                                        "13px",
                                    }}
                                  >
                                    Open on GitHub →
                                  </a>
                                )}
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}

                  {/* ======================================== */}
                  {/* SUCCESS MESSAGE */}
                  {/* ======================================== */}

                  {state.message && (
                    <div
                      style={{
                        marginTop:
                          "18px",
                        padding:
                          "14px",
                        borderRadius:
                          "10px",
                        background:
                          "#f0fdf4",
                        border:
                          "1px solid #bbf7d0",
                        color:
                          "#166534",
                        fontSize:
                          "14px",
                      }}
                    >
                      {state.message}
                    </div>
                  )}

                  {/* ======================================== */}
                  {/* ERROR MESSAGE */}
                  {/* ======================================== */}

                  {state.error && (
                    <div
                      style={{
                        marginTop:
                          "18px",
                        padding:
                          "14px",
                        borderRadius:
                          "10px",
                        background:
                          "#fef2f2",
                        border:
                          "1px solid #fecaca",
                        color:
                          "#b91c1c",
                        fontSize:
                          "14px",
                      }}
                    >
                      {state.error}
                    </div>
                  )}
                </section>
              );
            }
          )}
        </div>
      </div>
    </main>
  );
}