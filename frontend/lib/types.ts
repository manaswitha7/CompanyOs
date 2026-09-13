// ============================================================
// AUTH
// ============================================================

export type CurrentUser = {
  id: number;
  email: string;
  name: string;
  role: string;

  /**
   * Workspace associated with the authenticated user.
   *
   * The backend organization APIs require this value.
   */
  workspace_id: number | null;

  /**
   * Human-readable workspace name (e.g. "Jane's Workspace"),
   * set at registration time. Null if the user has no
   * workspace or the backend hasn't been updated to return it.
   */
  workspace_name: string | null;
};


// ============================================================
// DOCUMENTS
// ============================================================

export type Citation = {
  filename: string;
  page_number: number | null;
  chunk_id: number;
};


export type RagMetrics = {
  question_length?: number;
  provider?: string;
  model?: string;

  retrieval_latency_ms?: number;
  llm_latency_ms?: number;
  total_latency_ms?: number;

  retrieved_chunks?: number;
  citation_count?: number;

  success?: boolean;
  error?: string | null;
};


export type ChatResponse = {
  question: string;
  answer: string;
  citations: Citation[];
  metrics?: RagMetrics;
};


export type UploadResponse = {
  message: string;
  document_id: number;
  filename: string;
  storage_key: string;
};


export type DocumentStatus =
  | "queued"
  | "processing"
  | "completed"
  | "failed";


export type DocumentItem = {
  document_id: number;
  filename: string;
  file_type: string;
  status: DocumentStatus;
  created_at: string;
};


export type DocumentsResponse = {
  documents: DocumentItem[];
};


// ============================================================
// SEARCH
// ============================================================

export type SearchResult = {
  chunk_id: number;
  document_id: number;
  filename: string;

  chunk_index?: number;
  page_number?: number | null;

  content: string;

  semantic_score?: number;
  keyword_score?: number;
  final_score?: number;
};


export type SearchResponse = {
  results: SearchResult[];
};


// ============================================================
// CHAT SESSIONS
// ============================================================

export type ChatSession = {
  id: number;
  title?: string | null;

  workspace_id?: number | null;
  user_id?: number | null;

  created_at?: string;
  updated_at?: string;
};


export type ChatMessage = {
  id: number;
  session_id: number;

  role: string;
  content: string;

  created_at?: string;
};


export type ChatSessionsResponse = {
  sessions: ChatSession[];
};


// ============================================================
// ORGANIZATION
// ============================================================

export type Company = {
  id: number;
  name: string;

  description?: string | null;

  workspace_id?: number | null;

  created_at?: string;
};


export type Person = {
  id: number;
  name: string;

  email?: string | null;
  role?: string | null;

  department_id?: number | null;
  team_id?: number | null;
  company_id?: number | null;

  workspace_id?: number | null;

  created_at?: string;
};


export type Project = {
  id: number;
  name: string;

  description?: string | null;

  company_id?: number | null;
  workspace_id?: number | null;

  status?: string | null;

  created_at?: string;
};


export type Department = {
  id: number;
  name: string;

  description?: string | null;

  workspace_id?: number | null;
};


export type Team = {
  id: number;
  name: string;

  description?: string | null;

  department_id?: number | null;
  workspace_id?: number | null;
};


// ============================================================
// ORGANIZATION API RESPONSES
// ============================================================

export type CompaniesResponse = {
  companies: Company[];
};


export type PeopleResponse = {
  people: Person[];
};


export type ProjectsResponse = {
  projects: Project[];
};


export type DepartmentsResponse = {
  departments: Department[];
};


export type TeamsResponse = {
  teams: Team[];
};


export type OrganizationOverview = {
  companies?: Company[];
  people?: Person[];
  projects?: Project[];
  departments?: Department[];
  teams?: Team[];

  [key: string]: unknown;
};


// ============================================================
// SYSTEM
// ============================================================

export type SystemHealth = {
  [key: string]: unknown;
};


export type SystemStats = {
  total_users?: number;
  total_workspaces?: number;

  total_documents?: number;

  completed_documents?: number;
  processing_documents?: number;
  queued_documents?: number;
  failed_documents?: number;

  total_audit_events?: number;

  [key: string]: unknown;
};


export type IngestionStats = {
  queued?: number;
  processing?: number;
  completed?: number;
  failed?: number;

  [key: string]: unknown;
};


export type AuditLog = {
  id: number;

  workspace_id?: number | null;
  user_id?: number | null;

  action: string;

  resource_type?: string | null;
  resource_id?: number | null;

  details?: Record<string, unknown> | null;

  created_at?: string;
};


// ============================================================
// RBAC
// ============================================================

export type UpdateRoleResponse = {
  message: string;
  user: CurrentUser;
};


// ============================================================
// LINEAGE
// ============================================================

export type DocumentLineage = {
  [key: string]: unknown;
};


// ============================================================
// TOOLS
// ============================================================

export type Tool = {
  name: string;

  description?: string;

  [key: string]: unknown;
};


export type ToolsResponse = {
  tools: Tool[];
};


// ============================================================
// EVALUATION
// ============================================================

export type EvaluationResponse = {
  [key: string]: unknown;
};

// ============================================================
// TASKS
// ============================================================

export type TaskStatus =
  | "todo"
  | "in_progress"
  | "completed"
  | "cancelled"
  | string;

export type Task = {
  id: number;
  workspace_id: number;
  created_by: number;
  title: string;
  description?: string | null;
  status: TaskStatus;
  created_at?: string;
  updated_at?: string;
};

export type CreateTaskRequest = {
  title: string;
  description?: string;
};

export type UpdateTaskRequest = {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
};

export type TasksResponse = {
  tasks: Task[];
};