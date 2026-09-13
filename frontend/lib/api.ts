import type {
  AuditLog,
  ChatMessage,
  ChatResponse,
  ChatSession,
  ChatSessionsResponse,
  Company,
  CurrentUser,
  Department,
  DocumentLineage,
  DocumentsResponse,
  EvaluationResponse,
  IngestionStats,
  OrganizationOverview,
  Person,
  Project,
  SearchResponse,
  SystemHealth,
  SystemStats,
  Team,
  ToolsResponse,
  UpdateRoleResponse,
  UploadResponse,
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
} from "./types";


// ============================================================
// CONFIGURATION
// ============================================================

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

const TOKEN_KEY = "access_token";


// ============================================================
// API ERROR
// ============================================================

export class ApiError extends Error {
  status: number;
  data?: unknown;

  constructor(
    message: string,
    status: number,
    data?: unknown
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}


// ============================================================
// TOKEN MANAGEMENT
// ============================================================

export function getToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(
    TOKEN_KEY
  );
}


export function setToken(
  token: string
): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(
      TOKEN_KEY,
      token
    );
  }
}


export function clearToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(
      TOKEN_KEY
    );
  }
}


// ============================================================
// REDIRECT
// ============================================================

function redirectToLogin(): void {
  if (
    typeof window !== "undefined" &&
    window.location.pathname !== "/login"
  ) {
    window.location.href = "/login";
  }
}


// ============================================================
// ERROR MESSAGE
// ============================================================

function getErrorMessage(
  data: unknown
): string {

  if (data == null) {
    return "Request failed.";
  }

  if (typeof data === "string") {
    return data;
  }

  if (
    typeof data === "object" &&
    data !== null &&
    "detail" in data
  ) {

    const detail =
      (data as {
        detail: unknown;
      }).detail;

    if (typeof detail === "string") {
      return detail;
    }

    try {
      return JSON.stringify(detail);
    } catch {
      return String(detail);
    }
  }

  if (
    typeof data === "object" &&
    data !== null &&
    "message" in data
  ) {

    const message =
      (data as {
        message: unknown;
      }).message;

    if (typeof message === "string") {
      return message;
    }

    try {
      return JSON.stringify(message);
    } catch {
      return String(message);
    }
  }

  try {
    return JSON.stringify(data);
  } catch {
    return String(data);
  }
}


// ============================================================
// CORE REQUEST
// ============================================================

type RequestOptions = {
  method?:
    | "GET"
    | "POST"
    | "PUT"
    | "PATCH"
    | "DELETE";

  body?: BodyInit;

  isFormData?: boolean;

  skipAuth?: boolean;
};


async function request<T>(
  path: string,
  {
    method = "GET",
    body,
    isFormData = false,
    skipAuth = false,
  }: RequestOptions = {}
): Promise<T> {

  const headers: HeadersInit = {};


  // ----------------------------------------------------------
  // CONTENT TYPE
  // ----------------------------------------------------------

  if (
    !isFormData &&
    body
  ) {
    headers["Content-Type"] =
      "application/json";
  }


  // ----------------------------------------------------------
  // AUTHENTICATION
  // ----------------------------------------------------------

  if (!skipAuth) {

    const token = getToken();

    if (!token) {

      redirectToLogin();

      throw new ApiError(
        "Not authenticated.",
        401
      );
    }

    headers["Authorization"] =
      `Bearer ${token}`;
  }


  // ----------------------------------------------------------
  // REQUEST
  // ----------------------------------------------------------

  let response: Response;

  try {

    response = await fetch(
      `${API_BASE_URL}${path}`,
      {
        method,
        headers,
        body,
      }
    );

  } catch {

    throw new ApiError(
      "Unable to connect to Company OS backend.",
      0
    );
  }


  // ----------------------------------------------------------
  // SESSION EXPIRED
  // ----------------------------------------------------------

  if (
    response.status === 401
  ) {

    clearToken();

    redirectToLogin();

    throw new ApiError(
      "Session expired. Please sign in again.",
      401
    );
  }


  // ----------------------------------------------------------
  // READ RESPONSE ONLY ONCE
  //
  // IMPORTANT:
  // Do NOT call response.json() after response.text().
  // The response body can only be consumed once.
  // ----------------------------------------------------------

  const text =
    await response.text();

  let data: unknown = null;

  if (text) {

    try {

      data = JSON.parse(text);

    } catch {

      data = text;
    }
  }


  // ----------------------------------------------------------
  // ERROR
  // ----------------------------------------------------------

  if (!response.ok) {

    const message =
      getErrorMessage(data);

    console.error(
      "API request failed:",
      {
        path,
        method,
        status:
          response.status,
        statusText:
          response.statusText,
        response: data,
        message,
      }
    );

    throw new ApiError(
      message,
      response.status,
      data
    );
  }


  // ----------------------------------------------------------
  // SUCCESS
  // ----------------------------------------------------------

  return data as T;
}


// ============================================================
// AUTH
// ============================================================

export async function login(
  email: string,
  password: string
) {

  const data =
    await request<{
      access_token: string;
      token_type?: string;
    }>(
      "/auth/login",
      {
        method: "POST",

        body: JSON.stringify({
          email,
          password,
        }),

        skipAuth: true,
      }
    );

  setToken(
    data.access_token
  );

  return data;
}

export async function register(
  name: string,
  email: string,
  password: string
) {
  const data = await request<{
    access_token: string;
    token_type?: string;
  }>(
    "/auth/register",
    {
      method: "POST",

      body: JSON.stringify({
        name,
        email,
        password,
      }),

      skipAuth: true,
    }
  );

  setToken(data.access_token);

  return data;
}

export function logout(): void {

  clearToken();

  if (
    typeof window !== "undefined"
  ) {
    window.location.href =
      "/login";
  }
}


export function getCurrentUser() {

  return request<CurrentUser>(
    "/auth/me"
  );
}


// ============================================================
// DOCUMENTS
// ============================================================

export function getDocuments() {

  return request<DocumentsResponse>(
    "/documents"
  );
}


export function uploadDocument(
  file: File
) {

  const formData =
    new FormData();

  formData.append(
    "file",
    file
  );

  return request<UploadResponse>(
    "/documents/upload",
    {
      method: "POST",
      body: formData,
      isFormData: true,
    }
  );
}


export function deleteDocument(
  documentId: number
) {

  return request<void>(
    `/documents/${documentId}`,
    {
      method: "DELETE",
    }
  );
}


// ============================================================
// INGESTION
// ============================================================

export function processDocument(
  documentId: number
) {

  return request<{
    message: string;
    document_id: number;
    filename: string;
    status: string;
  }>(
    `/ingestion/process/${documentId}`,
    {
      method: "POST",
    }
  );
}


// ============================================================
// SEARCH
// ============================================================

export function semanticSearch(
  query: string,
  topK: number = 5,
  documentId?: number | null
) {

  const params =
    new URLSearchParams();

  params.set(
    "query",
    query
  );

  params.set(
    "top_k",
    String(topK)
  );

  if (
    documentId != null
  ) {

    params.set(
      "document_id",
      String(documentId)
    );
  }

  return request<SearchResponse>(
    `/search/semantic?${params.toString()}`
  );
}


export function hybridSearch(
  query: string,
  topK: number = 5,
  documentId?: number | null
) {

  const params =
    new URLSearchParams();

  params.set(
    "query",
    query
  );

  params.set(
    "top_k",
    String(topK)
  );

  if (
    documentId != null
  ) {

    params.set(
      "document_id",
      String(documentId)
    );
  }

  return request<SearchResponse>(
    `/search/hybrid?${params.toString()}`
  );
}


// ============================================================
// CHAT / RAG
// ============================================================

export function askQuestion(
  question: string,
  topK: number = 5,
  documentId: number | null = null
) {

  return request<ChatResponse>(
    "/chat",
    {
      method: "POST",

      body: JSON.stringify({
        question,
        top_k: topK,
        document_id:
          documentId,
      }),
    }
  );
}


// ============================================================
// CHAT SESSIONS
// ============================================================

export function getChatSessions() {

  return request<ChatSessionsResponse>(
    "/chat/sessions"
  );
}


export function getChatSession(
  sessionId: number
) {

  return request<ChatSession>(
    `/chat/sessions/${sessionId}`
  );
}


export function getChatMessages(
  sessionId: number
) {

  return request<ChatMessage[]>(
    `/chat/sessions/${sessionId}/messages`
  );
}


// ============================================================
// SYSTEM
// ============================================================

export function getSystemHealth() {

  return request<SystemHealth>(
    "/system/health"
  );
}


export function getSystemStats() {

  return request<SystemStats>(
    "/system/stats"
  );
}


export function getIngestionStats() {

  return request<IngestionStats>(
    "/system/ingestion"
  );
}


export function getAuditLogs() {

  return request<AuditLog[]>(
    "/system/audit"
  );
}


// ============================================================
// TOOLS
// ============================================================

export function getTools() {

  return request<ToolsResponse>(
    "/tools"
  );
}


export function executeTool(
  toolName: string,
  payload: Record<
    string,
    unknown
  > = {}
) {

  return request<
    Record<string, unknown>
  >(
    "/tools/execute",
    {
      method: "POST",

      body: JSON.stringify({
        tool_name: toolName,
        arguments: payload,
      }),
    }
  );
}


// ============================================================
// EVALUATION
// ============================================================

export function runEvaluation(
  payload: Record<
    string,
    unknown
  > = {}
) {

  return request<EvaluationResponse>(
    "/evaluation/run",
    {
      method: "POST",

      body: JSON.stringify(
        payload
      ),
    }
  );
}


// ============================================================
// USERS / RBAC
// ============================================================

export function updateUserRole(
  userId: number,
  role: string
) {

  return request<UpdateRoleResponse>(
    `/users/${userId}/role`,
    {
      method: "PUT",

      body: JSON.stringify({
        role,
      }),
    }
  );
}


// ============================================================
// LINEAGE
// ============================================================

export function getDocumentLineage(
  documentId: number
) {

  return request<DocumentLineage>(
    `/lineage/documents/${documentId}`
  );
}


// ============================================================
// ORGANIZATION
// ============================================================

export function getCompanies(
  workspaceId?: number
) {

  const path =
    workspaceId != null
      ? `/organization/companies?workspace_id=${workspaceId}`
      : "/organization/companies";

  return request<Company[]>(
    path
  );
}


export function getCompany(
  companyId: number,
  workspaceId?: number
) {

  const path =
    workspaceId != null
      ? `/organization/companies/${companyId}?workspace_id=${workspaceId}`
      : `/organization/companies/${companyId}`;

  return request<Company>(
    path
  );
}


export function getPeople(
  workspaceId?: number
) {

  const path =
    workspaceId != null
      ? `/organization/people?workspace_id=${workspaceId}`
      : "/organization/people";

  return request<Person[]>(
    path
  );
}


export function getPerson(
  personId: number,
  workspaceId?: number
) {

  const path =
    workspaceId != null
      ? `/organization/people/${personId}?workspace_id=${workspaceId}`
      : `/organization/people/${personId}`;

  return request<Person>(
    path
  );
}


export function getProjects(
  workspaceId?: number
) {

  const path =
    workspaceId != null
      ? `/organization/projects?workspace_id=${workspaceId}`
      : "/organization/projects";

  return request<Project[]>(
    path
  );
}


export function getProject(
  projectId: number,
  workspaceId?: number
) {

  const path =
    workspaceId != null
      ? `/organization/projects/${projectId}?workspace_id=${workspaceId}`
      : `/organization/projects/${projectId}`;

  return request<Project>(
    path
  );
}


export function getDepartments(
  workspaceId?: number
) {

  const path =
    workspaceId != null
      ? `/organization/departments?workspace_id=${workspaceId}`
      : "/organization/departments";

  return request<Department[]>(
    path
  );
}


export function getTeams(
  workspaceId?: number
) {

  const path =
    workspaceId != null
      ? `/organization/teams?workspace_id=${workspaceId}`
      : "/organization/teams";

  return request<Team[]>(
    path
  );
}


export function getOrganizationOverview(
  workspaceId?: number
) {

  const path =
    workspaceId != null
      ? `/organization/overview?workspace_id=${workspaceId}`
      : "/organization/overview";

  return request<OrganizationOverview>(
    path
  );
}


// ============================================================
// TASKS
// ============================================================

export function getTasks() {

  return request<Task[]>(
    "/tasks"
  );
}


export function getTask(
  taskId: number
) {

  return request<Task>(
    `/tasks/${taskId}`
  );
}


export function createTask(
  data: CreateTaskRequest
) {

  return request<Task>(
    "/tasks",
    {
      method: "POST",

      body: JSON.stringify(
        data
      ),
    }
  );
}


export function updateTask(
  taskId: number,
  data: UpdateTaskRequest
) {

  return request<Task>(
    `/tasks/${taskId}`,
    {
      method: "PUT",

      body: JSON.stringify(
        data
      ),
    }
  );
}


export function deleteTask(
  taskId: number
) {

  return request<void>(
    `/tasks/${taskId}`,
    {
      method: "DELETE",
    }
  );
}


// ============================================================
// ANALYTICS
// ============================================================

export type WorkspaceAnalytics = {
  workspace_id: number;

  tasks: {
    total: number;
    [status: string]: number;
  };

  projects: {
    total: number;
    [status: string]: number;
  };

  deals: {
    total: number;
    total_value: number;
    [status: string]: number;
  };

  tickets: {
    total: number;
    [status: string]: number;
  };

  documents: {
    total: number;
    [status: string]: number;
  };

  feedback: {
    total: number;
    average_rating: number;
    [rating: string]: number;
  };
};


export function getWorkspaceAnalytics(
  workspaceId: number
) {

  return request<WorkspaceAnalytics>(
    `/analytics/${workspaceId}`
  );
}


// ============================================================
// AI FEEDBACK
// ============================================================

export type AIFeedback = {
  id: number;
  workspace_id: number;
  user_id: number | null;
  source_type: string;
  source_id: number | null;
  rating: number;
  feedback: string | null;
  created_at: string;
};


export type CreateAIFeedbackRequest = {
  workspace_id: number;
  user_id?: number | null;
  source_type: string;
  source_id?: number | null;
  rating: number;
  feedback?: string | null;
};


export type AIFeedbackResponse =
  AIFeedback;


export function submitAIFeedback(
  data: CreateAIFeedbackRequest
) {

  return request<AIFeedbackResponse>(
    "/analytics/feedback",
    {
      method: "POST",

      body: JSON.stringify(
        data
      ),
    }
  );
}


export function getAIFeedback(
  workspaceId: number
) {

  return request<AIFeedback[]>(
    `/analytics/feedback/${workspaceId}`
  );
}


// ============================================================
// KNOWLEDGE GOVERNANCE
// ============================================================

export type KnowledgeVersion = {
  id: number;
  document_id: number;
  version: number;
  change_type?: string | null;
  change_summary?: string | null;
  created_at: string;
};


export type KnowledgeLineage = {
  document_id: number;
  versions: KnowledgeVersion[];
  sources?: unknown[];
  edges?: unknown[];
};


export function getKnowledgeVersions(
  workspaceIdOrDocumentId: number,
  resourceType?: string,
  resourceId?: number
) {

  if (
    resourceType !== undefined &&
    resourceId !== undefined
  ) {

    return request<KnowledgeVersion[]>(
      `/knowledge-governance/versions/${workspaceIdOrDocumentId}/${resourceType}/${resourceId}`
    );
  }

  return request<KnowledgeVersion[]>(
    `/knowledge-governance/versions/${workspaceIdOrDocumentId}`
  );
}


export function getKnowledgeLineage(
  documentId: number
) {

  return getDocumentLineage(
    documentId
  );
}


// ============================================================
// CRM RELATIONSHIPS
// ============================================================

export type CRMRelationship = {
  id: number;
  workspace_id: number;

  source: {
    type: string;
    id: number;
  };

  target: {
    type: string;
    id: number;
  };

  relationship_type: string;

  description?: string | null;

  metadata?:
    | Record<string, unknown>
    | null;

  created_at: string;
  updated_at: string;
};


export function getCrmObjectTypes() {

  return request<{
    object_types: string[];
  }>(
    "/crm/object-types",
    {
      skipAuth: true,
    }
  );
}


export function getCrmRelationships(
  workspaceId: number,
  objectType: string,
  objectId: number
) {

  const params =
    new URLSearchParams({
      workspace_id:
        String(workspaceId),

      object_type:
        objectType,

      object_id:
        String(objectId),
    });

  return request<{
    object: {
      type: string;
      id: number;
    };

    count: number;

    relationships:
      CRMRelationship[];

  }>(
    `/crm/relationships?${params.toString()}`,
    {
      skipAuth: true,
    }
  );
}


export function createCrmRelationship(
  payload: {
    workspace_id: number;

    source_type: string;
    source_id: number;

    target_type: string;
    target_id: number;

    relationship_type: string;

    description?: string;

    metadata?:
      Record<string, unknown>;
  }
) {

  return request<CRMRelationship>(
    "/crm/relationships",
    {
      method: "POST",

      body: JSON.stringify(
        payload
      ),

      skipAuth: true,
    }
  );
}


export function deleteCrmRelationship(
  relationshipId: number
) {

  return request<{
    success: boolean;
    relationship_id: number;
  }>(
    `/crm/relationships/${relationshipId}`,
    {
      method: "DELETE",
      skipAuth: true,
    }
  );
}


// ============================================================
// MEETINGS
// ============================================================

export type Meeting = {
  id: number;
  title: string;
  description?: string | null;
  meeting_type?: string | null;
  source_type?: string | null;
  source_uri?: string | null;
  status?: string | null;
  started_at?: string | null;
  ended_at?: string | null;
  duration_seconds?: number | null;
  created_at?: string | null;
};


export type MeetingDetails = {
  meeting: Meeting;

  participants: Array<{
    id: number;
    name: string;
    email?: string | null;
    speaker_label?: string | null;
    user_id?: number | null;
    joined_at?: string | null;
    left_at?: string | null;
  }>;

  transcript: Array<{
    id: number;
    speaker_label?: string | null;
    participant_id?: number | null;
    start_time_seconds?: number | null;
    end_time_seconds?: number | null;
    text: string;
    sequence_number: number;
  }>;

  decisions: Array<{
    id: number;
    decision: string;
    context?: string | null;
    speaker_label?: string | null;
  }>;

  action_items: Array<{
    id: number;
    description: string;
    assignee_name?: string | null;
    assignee_user_id?: number | null;
    due_at?: string | null;
    status?: string | null;
  }>;

  summary: {
    id: number;
    summary: string;
    key_points?: string | null;
    follow_ups?: string | null;
    generated_by?: string | null;
  } | null;
};


export async function getMeetings(): Promise<
  Meeting[]
> {

  const data =
    await request<{
      meetings: Meeting[];
    }>(
      "/meetings",
      {
        skipAuth: true,
      }
    );

  return data.meetings;
}


export function getMeeting(
  meetingId: number
) {

  return request<MeetingDetails>(
    `/meetings/${meetingId}`,
    {
      skipAuth: true,
    }
  );
}


export function createMeeting(
  payload: {
    title: string;
    description?: string | null;
    meeting_type?: string | null;
    source_type?: string;
    source_uri?: string | null;
  }
) {

  return request<Meeting>(
    "/meetings",
    {
      method: "POST",

      body: JSON.stringify(
        payload
      ),

      skipAuth: true,
    }
  );
}


export function updateMeetingStatus(
  meetingId: number,
  status: string
) {

  return request<Meeting>(
    `/meetings/${meetingId}/status`,
    {
      method: "PATCH",

      body: JSON.stringify({
        status,
      }),

      skipAuth: true,
    }
  );
}


// ============================================================
// CONNECTORS
// ============================================================

export interface Connector {
  name: string;
  display_name: string;
}


export interface ConnectorListResponse {
  connectors: Connector[];
}


export interface ConnectorResponse {
  connector: string;
  status: string;
  message?: string;
}


export interface ConnectorTestResponse {
  connector: string;
  connected: boolean;
  status: string;
}


export interface ConnectorFetchResponse {
  connector: string;
  repository?: string;
  count: number;
  records: Record<
    string,
    unknown
  >[];
}


// ============================================================
// GET CONNECTORS
// ============================================================

export function getConnectors() {

  return request<ConnectorListResponse>(
    "/connectors"
  );
}


// ============================================================
// CONNECT CONNECTOR
// ============================================================

export function connectConnector(
  connectorName: string,
  credentials: Record<
    string,
    unknown
  >
) {

  return request<ConnectorResponse>(
    `/connectors/${connectorName}/connect`,
    {
      method: "POST",

      body: JSON.stringify({
        credentials,
      }),
    }
  );
}


// ============================================================
// TEST CONNECTOR
// ============================================================

export function testConnector(
  connectorName: string
) {

  return request<ConnectorTestResponse>(
    `/connectors/${connectorName}/test`,
    {
      method: "POST",
    }
  );
}


// ============================================================
// DISCONNECT CONNECTOR
// ============================================================

export function disconnectConnector(
  connectorName: string
) {
  return request<ConnectorResponse>(
    `/connectors/${connectorName}`,
    {
      method: "DELETE",
    }
  );
}


// ============================================================
// FETCH CONNECTOR DATA
// ============================================================

export function fetchConnector(
  connectorName: string,
  credentials: Record<
    string,
    unknown
  >,
  options: Record<
    string,
    unknown
  > = {}
) {

  return request<ConnectorFetchResponse>(
    `/connectors/${connectorName}/fetch`,
    {
      method: "POST",

      body: JSON.stringify({
        credentials,
        options,
      }),
    }
  );
}

export async function ingestGitHub(
  repository: string,
  token: string,
  state: string = "open",
  limit: number = 50
) {
  const response = await fetch(
    `${API_BASE_URL}/connectors/github/ingest`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem(
          "access_token"
        )}`,
      },
      body: JSON.stringify({
        credentials: {
          token,
        },
        repository,
        state,
        limit,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "GitHub ingestion failed"
    );
  }

  return data;
}