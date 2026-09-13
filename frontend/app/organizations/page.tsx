"use client";

import { useEffect, useState } from "react";

import {
  getCurrentUser,
  getCompanies,
  getPeople,
  getProjects,
  getDepartments,
  getTeams,
} from "@/lib/api";

import type {
  Company,
  Person,
  Project,
  Department,
  Team,
} from "@/lib/types";


// ============================================================
// PAGE
// ============================================================

export default function OrganizationsPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [people, setPeople] = useState<Person[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [workspaceId, setWorkspaceId] = useState<number | null>(
    null
  );

  // ----------------------------------------------------------
  // LOAD ORGANIZATION
  // ----------------------------------------------------------

  useEffect(() => {
    let cancelled = false;

    async function loadOrganization() {
      try {
        setLoading(true);
        setError("");

        // ----------------------------------------------------
        // 1. Get logged-in user
        // ----------------------------------------------------

        const user = await getCurrentUser();

        if (cancelled) {
          return;
        }

        // ----------------------------------------------------
        // 2. Get workspace ID
        // ----------------------------------------------------

        const currentWorkspaceId = user.workspace_id;

        if (
          currentWorkspaceId === null ||
          currentWorkspaceId === undefined
        ) {
          throw new Error(
            "Your account is not assigned to a workspace. Please contact an administrator."
          );
        }

        setWorkspaceId(currentWorkspaceId);

        console.log(
          "[Organization] workspace_id:",
          currentWorkspaceId
        );

        // ----------------------------------------------------
        // 3. Load organization data
        // ----------------------------------------------------

        const [
          companiesData,
          peopleData,
          projectsData,
          departmentsData,
          teamsData,
        ] = await Promise.all([
          getCompanies(currentWorkspaceId),
          getPeople(currentWorkspaceId),
          getProjects(currentWorkspaceId),
          getDepartments(currentWorkspaceId),
          getTeams(currentWorkspaceId),
        ]);

        if (cancelled) {
          return;
        }

        // ----------------------------------------------------
        // 4. Store data
        // ----------------------------------------------------

        setCompanies(
          Array.isArray(companiesData)
            ? companiesData
            : []
        );

        setPeople(
          Array.isArray(peopleData)
            ? peopleData
            : []
        );

        setProjects(
          Array.isArray(projectsData)
            ? projectsData
            : []
        );

        setDepartments(
          Array.isArray(departmentsData)
            ? departmentsData
            : []
        );

        setTeams(
          Array.isArray(teamsData)
            ? teamsData
            : []
        );

      } catch (err: unknown) {
        if (cancelled) {
          return;
        }

        console.error(
          "[Organization] API error:",
          err
        );

        // ----------------------------------------------------
        // Better error extraction
        // ----------------------------------------------------

        let message =
          "Failed to load organization data.";

        if (err instanceof Error) {
          message = err.message;
        } else if (
          typeof err === "string"
        ) {
          message = err;
        } else if (
          err &&
          typeof err === "object"
        ) {
          const errorObject =
            err as Record<string, unknown>;

          if (
            typeof errorObject.message ===
            "string"
          ) {
            message = errorObject.message;
          } else if (
            typeof errorObject.detail ===
            "string"
          ) {
            message = errorObject.detail;
          } else {
            try {
              message = JSON.stringify(
                errorObject
              );
            } catch {
              message =
                "Failed to load organization data.";
            }
          }
        }

        setError(message);

      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadOrganization();

    return () => {
      cancelled = true;
    };
  }, []);


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {
    return (
      <main className="min-h-screen bg-ink p-8 text-white">
        <div className="mx-auto max-w-7xl">

          <p className="font-mono text-xs uppercase tracking-widest text-white/40">
            Company OS
          </p>

          <h1 className="mt-2 font-display text-3xl font-semibold">
            Organization
          </h1>

          <div className="mt-10 rounded-xl border border-ink-line bg-ink-soft p-8">
            <div className="flex items-center gap-3">

              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white" />

              <p className="font-mono text-sm text-white/50">
                Loading organization...
              </p>

            </div>
          </div>

        </div>
      </main>
    );
  }


  // ==========================================================
  // ERROR
  // ==========================================================

  if (error) {
    return (
      <main className="min-h-screen bg-ink p-8 text-white">
        <div className="mx-auto max-w-7xl">

          <p className="font-mono text-xs uppercase tracking-widest text-white/40">
            Company OS
          </p>

          <h1 className="mt-2 font-display text-3xl font-semibold">
            Organization
          </h1>

          <div className="mt-10 rounded-xl border border-red-500/30 bg-red-500/10 p-6">

            <p className="font-mono text-xs uppercase tracking-widest text-red-300">
              Organization Error
            </p>

            <p className="mt-3 break-words text-sm leading-6 text-red-200">
              {error}
            </p>

            {workspaceId === null && (
              <p className="mt-4 text-xs text-red-300/70">
                Workspace ID could not be determined
                from the current user.
              </p>
            )}

          </div>

        </div>
      </main>
    );
  }


  // ==========================================================
  // PAGE
  // ==========================================================

  return (
    <main className="min-h-screen bg-ink p-8 text-white">

      <div className="mx-auto max-w-7xl">

        {/* ==================================================
            HEADER
        ================================================== */}

        <div className="mb-8">

          <p className="font-mono text-xs uppercase tracking-widest text-white/40">
            Company OS
          </p>

          <div className="mt-2 flex flex-wrap items-center gap-4">

            <h1 className="font-display text-3xl font-semibold">
              Organization
            </h1>

            {workspaceId !== null && (
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 font-mono text-[10px] uppercase tracking-wider text-white/40">
                Workspace {workspaceId}
              </span>
            )}

          </div>

          <p className="mt-2 text-sm text-white/50">
            Company structure, people, projects,
            departments and teams.
          </p>

        </div>


        {/* ==================================================
            STATS
        ================================================== */}

        <div className="mb-10 grid grid-cols-2 gap-4 md:grid-cols-5">

          <StatCard
            label="Companies"
            value={companies.length}
          />

          <StatCard
            label="People"
            value={people.length}
          />

          <StatCard
            label="Projects"
            value={projects.length}
          />

          <StatCard
            label="Departments"
            value={departments.length}
          />

          <StatCard
            label="Teams"
            value={teams.length}
          />

        </div>


        {/* ==================================================
            COMPANIES
        ================================================== */}

        <Section
          title="Companies"
          count={companies.length}
        >
          {companies.length === 0 ? (
            <Empty text="No companies found." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">

              {companies.map((company) => (
                <Card key={company.id}>

                  <div className="flex items-start justify-between gap-4">

                    <h3 className="font-medium">
                      {company.name}
                    </h3>

                    <span className="font-mono text-[10px] text-white/20">
                      #{company.id}
                    </span>

                  </div>

                  {company.description && (
                    <p className="mt-2 text-sm leading-6 text-white/50">
                      {company.description}
                    </p>
                  )}

                </Card>
              ))}

            </div>
          )}
        </Section>


        {/* ==================================================
            PEOPLE
        ================================================== */}

        <Section
          title="People"
          count={people.length}
        >
          {people.length === 0 ? (
            <Empty text="No people found." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">

              {people.map((person) => (
                <Card key={person.id}>

                  <div className="flex items-start justify-between gap-4">

                    <div>

                      <h3 className="font-medium">
                        {person.name}
                      </h3>

                      {person.role && (
                        <p className="mt-1 font-mono text-xs text-white/40">
                          {person.role}
                        </p>
                      )}

                    </div>

                    <span className="font-mono text-[10px] text-white/20">
                      #{person.id}
                    </span>

                  </div>

                  {person.email && (
                    <p className="mt-3 text-sm text-white/50">
                      {person.email}
                    </p>
                  )}

                  {(person.department_id !== null &&
                    person.department_id !== undefined) && (
                    <p className="mt-3 font-mono text-[10px] text-white/30">
                      Department #{person.department_id}
                    </p>
                  )}

                  {(person.team_id !== null &&
                    person.team_id !== undefined) && (
                    <p className="mt-1 font-mono text-[10px] text-white/30">
                      Team #{person.team_id}
                    </p>
                  )}

                </Card>
              ))}

            </div>
          )}
        </Section>


        {/* ==================================================
            PROJECTS
        ================================================== */}

        <Section
          title="Projects"
          count={projects.length}
        >
          {projects.length === 0 ? (
            <Empty text="No projects found." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">

              {projects.map((project) => (
                <Card key={project.id}>

                  <div className="flex items-start justify-between gap-4">

                    <h3 className="font-medium">
                      {project.name}
                    </h3>

                    <span className="font-mono text-[10px] text-white/20">
                      #{project.id}
                    </span>

                  </div>

                  {project.description && (
                    <p className="mt-2 text-sm leading-6 text-white/50">
                      {project.description}
                    </p>
                  )}

                  {project.status && (
                    <span className="mt-4 inline-block rounded-md border border-white/10 bg-white/5 px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-white/50">
                      {project.status}
                    </span>
                  )}

                </Card>
              ))}

            </div>
          )}
        </Section>


        {/* ==================================================
            DEPARTMENTS
        ================================================== */}

        <Section
          title="Departments"
          count={departments.length}
        >
          {departments.length === 0 ? (
            <Empty text="No departments found." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">

              {departments.map((department) => (
                <Card key={department.id}>

                  <div className="flex items-start justify-between gap-4">

                    <h3 className="font-medium">
                      {department.name}
                    </h3>

                    <span className="font-mono text-[10px] text-white/20">
                      #{department.id}
                    </span>

                  </div>

                  {department.description && (
                    <p className="mt-2 text-sm leading-6 text-white/50">
                      {department.description}
                    </p>
                  )}

                </Card>
              ))}

            </div>
          )}
        </Section>


        {/* ==================================================
            TEAMS
        ================================================== */}

        <Section
          title="Teams"
          count={teams.length}
        >
          {teams.length === 0 ? (
            <Empty text="No teams found." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">

              {teams.map((team) => (
                <Card key={team.id}>

                  <div className="flex items-start justify-between gap-4">

                    <h3 className="font-medium">
                      {team.name}
                    </h3>

                    <span className="font-mono text-[10px] text-white/20">
                      #{team.id}
                    </span>

                  </div>

                  {team.description && (
                    <p className="mt-2 text-sm leading-6 text-white/50">
                      {team.description}
                    </p>
                  )}

                  {team.department_id !== null &&
                    team.department_id !== undefined && (
                      <p className="mt-3 font-mono text-[10px] text-white/30">
                        Department #{team.department_id}
                      </p>
                    )}

                </Card>
              ))}

            </div>
          )}
        </Section>

      </div>

    </main>
  );
}


// ============================================================
// STAT CARD
// ============================================================

function StatCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-ink-line bg-ink-soft p-5">

      <p className="font-mono text-[10px] uppercase tracking-wider text-white/40">
        {label}
      </p>

      <p className="mt-2 font-display text-2xl font-semibold">
        {value}
      </p>

    </div>
  );
}


// ============================================================
// SECTION
// ============================================================

function Section({
  title,
  count,
  children,
}: {
  title: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <section className="mb-10">

      <div className="mb-4 flex items-center gap-3">

        <h2 className="font-display text-xl font-semibold">
          {title}
        </h2>

        <span className="rounded-full border border-white/10 px-2 py-0.5 font-mono text-[10px] text-white/40">
          {count}
        </span>

      </div>

      {children}

    </section>
  );
}


// ============================================================
// CARD
// ============================================================

function Card({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-ink-line bg-ink-soft p-5 transition hover:border-white/20">
      {children}
    </div>
  );
}


// ============================================================
// EMPTY
// ============================================================

function Empty({
  text,
}: {
  text: string;
}) {
  return (
    <div className="rounded-xl border border-dashed border-white/10 p-8 text-center">

      <p className="font-mono text-xs text-white/30">
        {text}
      </p>

    </div>
  );
}