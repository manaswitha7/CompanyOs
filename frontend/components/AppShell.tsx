"use client";

import {
  BarChart3,
  BriefcaseBusiness,
  Building2,
  CalendarDays,
  CheckSquare,
  ChevronDown,
  Database,
  FileText,
  FolderKanban,
  GitBranch,
  Layers3,
  LogOut,
  Menu,
  MessageSquare,
  Plug,
  Settings,
  Users,
} from "lucide-react";

import Link from "next/link";
import { ReactNode, useEffect, useState } from "react";
import { usePathname } from "next/navigation";

import { getCurrentUser, logout } from "@/lib/api";
import type { CurrentUser } from "@/lib/types";


// ============================================================
// TYPES
// ============================================================

interface AppShellProps {
  children: ReactNode;
}


// ============================================================
// NAVIGATION
// ============================================================

const navigation = [
  {
    section: "WORKSPACE",

    items: [
      {
        name: "Chat",
        href: "/",
        icon: MessageSquare,
      },
      {
        name: "Knowledge",
        href: "/documents",
        icon: FileText,
      },
      {
        name: "Organization",
        href: "/organizations",
        icon: Building2,
      },
      {
        name: "Connectors",
        href: "/connectors",
        icon: Plug,
      },
      {
        name: "CRM",
        href: "/crm",
        icon: BriefcaseBusiness,
      },
      {
        name: "Meetings",
        href: "/meetings",
        icon: CalendarDays,
      },
      {
        name: "Tasks",
        href: "/tasks",
        icon: CheckSquare,
      },
      {
        name: "Projects",
        href: "/projects",
        icon: FolderKanban,
      },
      {
        name: "People",
        href: "/people",
        icon: Users,
      },
    ],
  },

  {
    section: "SYSTEM",

    items: [
      {
        name: "Data",
        href: "/data",
        icon: Database,
      },
      {
        name: "Analytics",
        href: "/analytics",
        icon: BarChart3,
      },
      {
        name: "Settings",
        href: "/settings",
        icon: Settings,
      },
    ],
  },
];


// ============================================================
// APP SHELL
// ============================================================

export default function AppShell({
  children,
}: AppShellProps) {

  const pathname = usePathname();

  const [mobileOpen, setMobileOpen] =
    useState(false);

  const [userOpen, setUserOpen] =
    useState(false);

  const [currentUser, setCurrentUser] =
    useState<CurrentUser | null>(null);


  // ==========================================================
  // CURRENT USER
  //
  // The rest of this component previously hardcoded "Demo User
  // 2" / demo2@companyos.com regardless of who was actually
  // logged in — it never called the API. This fetches the real
  // session.
  // ==========================================================

  useEffect(() => {
    let cancelled = false;

    getCurrentUser()
      .then((user) => {
        if (!cancelled) setCurrentUser(user);
      })
      .catch(() => {
        // getCurrentUser() throwing usually means the stored
        // token is missing/expired — send back to login.
        if (!cancelled) logout();
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const userName = currentUser?.name || "Loading...";
  const userEmail = currentUser?.email || "";
  const userInitial = (
    currentUser?.name?.trim()?.[0] || "?"
  ).toUpperCase();
  const workspaceLabel =
    currentUser?.workspace_id != null
      ? `Workspace ${currentUser.workspace_id}`
      : "Workspace";


  // ==========================================================
  // ACTIVE ROUTE
  // ==========================================================

  const isActive = (href: string) => {

    if (href === "/") {
      return pathname === "/";
    }

    return (
      pathname === href ||
      pathname.startsWith(`${href}/`)
    );
  };


  // ==========================================================
  // SIDEBAR
  // ==========================================================

  const Sidebar = () => {

    return (
      <aside
        className="
          flex
          h-dvh
          w-[260px]
          shrink-0
          flex-col
          overflow-hidden
          border-r
          border-white/[0.07]
          bg-[#0b1020]
          text-white
        "
      >

        {/* ====================================================
            BRAND
        ===================================================== */}

        <div
          className="
            flex
            h-[72px]
            shrink-0
            items-center
            gap-3
            border-b
            border-white/[0.07]
            px-5
          "
        >

          <div
            className="
              flex
              h-9
              w-9
              shrink-0
              items-center
              justify-center
              rounded-[10px]
              bg-gradient-to-br
              from-indigo-500
              to-blue-600
              text-base
              font-bold
              shadow-lg
              shadow-indigo-500/20
            "
          >
            C
          </div>


          <div className="min-w-0">

            <div
              className="
                truncate
                text-[15px]
                font-semibold
                tracking-tight
                text-white
              "
            >
              Company OS
            </div>

            <div
              className="
                mt-0.5
                truncate
                text-[8px]
                font-medium
                uppercase
                tracking-[0.18em]
                text-slate-500
              "
            >
              Company Knowledge
            </div>

          </div>

        </div>


        {/* ====================================================
            NAVIGATION
            ONLY THIS SECTION SCROLLS
        ===================================================== */}

        <nav
          className="
            min-h-0
            flex-1
            overflow-y-auto
            overflow-x-hidden
            px-3
            py-4

            [&::-webkit-scrollbar]:w-[4px]
            [&::-webkit-scrollbar-track]:bg-transparent
            [&::-webkit-scrollbar-thumb]:rounded-full
            [&::-webkit-scrollbar-thumb]:bg-white/10
            hover:[&::-webkit-scrollbar-thumb]:bg-white/20
          "
        >

          {navigation.map((group) => (

            <div
              key={group.section}
              className="mb-5"
            >

              {/* Section title */}

              <div
                className="
                  mb-2
                  px-3
                  text-[9px]
                  font-semibold
                  uppercase
                  tracking-[0.18em]
                  text-slate-600
                "
              >
                {group.section}
              </div>


              {/* Items */}

              <div className="space-y-1">

                {group.items.map((item) => {

                  const active =
                    isActive(item.href);

                  const Icon = item.icon;

                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      onClick={() => {
                        setMobileOpen(false);
                        setUserOpen(false);
                      }}
                      className={`
                        group
                        relative
                        flex
                        h-[42px]
                        w-full
                        items-center
                        gap-3
                        rounded-[10px]
                        px-3
                        transition-all
                        duration-150

                        ${
                          active
                            ? "bg-[#171d31] text-white"
                            : "text-slate-400 hover:bg-white/[0.04] hover:text-slate-100"
                        }
                      `}
                    >

                      {/* Active bar */}

                      {active && (
                        <span
                          className="
                            absolute
                            left-0
                            top-1/2
                            h-5
                            w-[3px]
                            -translate-y-1/2
                            rounded-r-full
                            bg-indigo-500
                          "
                        />
                      )}


                      {/* Icon */}

                      <Icon
                        size={19}
                        strokeWidth={active ? 2 : 1.7}
                        className={`
                          shrink-0
                          transition-colors

                          ${
                            active
                              ? "text-indigo-400"
                              : "text-slate-500 group-hover:text-slate-300"
                          }
                        `}
                      />


                      {/* Label */}

                      <span
                        className="
                          min-w-0
                          flex-1
                          truncate
                          text-[13px]
                          font-medium
                        "
                      >
                        {item.name}
                      </span>


                      {/* Active dot */}

                      {active && (
                        <span
                          className="
                            h-[5px]
                            w-[5px]
                            shrink-0
                            rounded-full
                            bg-indigo-400
                          "
                        />
                      )}

                    </Link>
                  );

                })}

              </div>

            </div>

          ))}

        </nav>


        {/* ====================================================
            BOTTOM AREA
            ALWAYS FIXED
        ===================================================== */}

        <div
          className="
            shrink-0
            border-t
            border-white/[0.07]
            bg-[#0b1020]
            px-3
            py-3
          "
        >

          {/* ==================================================
              WORKSPACE

              The backend has no multi-workspace-per-user
              model — a user belongs to exactly one workspace,
              created automatically at registration
              (POST /auth/register), with no join/switch/create
              endpoints for an existing account. The previous
              "Switch workspace" / "+ Create workspace" popup
              didn't correspond to anything the backend could
              actually do, so it's replaced with a plain link
              to the real workspace overview page.
          ================================================== */}

          <Link
            href="/workspaces"
            className="
              flex
              w-full
              items-center
              gap-3
              rounded-[10px]
              border
              border-white/[0.07]
              bg-[#111728]
              px-3
              py-2.5
              text-left
              transition
              hover:border-white/[0.12]
              hover:bg-[#151c2e]
            "
          >

            {/* Small workspace icon */}

            <div
              className="
                flex
                h-7
                w-7
                shrink-0
                items-center
                justify-center
                rounded-md
                bg-indigo-500/10
                text-indigo-400
              "
            >
              <Layers3
                size={15}
                strokeWidth={1.8}
              />
            </div>


            {/* Details */}

            <div className="min-w-0 flex-1">

              <div
                className="
                  text-[8px]
                  font-medium
                  uppercase
                  tracking-[0.16em]
                  text-slate-600
                "
              >
                Workspace
              </div>

              <div
                className="
                  mt-0.5
                  truncate
                  text-[12px]
                  font-semibold
                  text-slate-200
                "
              >
                {workspaceLabel}
              </div>

            </div>

          </Link>


          {/* ==================================================
              USER
          ================================================== */}

          <div className="relative mt-2">

            <button
              type="button"
              onClick={() => {
                setUserOpen(!userOpen);
              }}
              className="
                flex
                w-full
                items-center
                gap-3
                rounded-[10px]
                px-2
                py-2
                text-left
                transition
                hover:bg-white/[0.04]
              "
            >

              {/* Avatar */}

              <div
                className="
                  flex
                  h-8
                  w-8
                  shrink-0
                  items-center
                  justify-center
                  rounded-full
                  bg-gradient-to-br
                  from-indigo-500
                  to-purple-600
                  text-[11px]
                  font-semibold
                  text-white
                "
              >
                {userInitial}
              </div>


              {/* User */}

              <div className="min-w-0 flex-1">

                <div
                  className="
                    truncate
                    text-[12px]
                    font-semibold
                    text-slate-200
                  "
                >
                  {userName}
                </div>

                <div
                  className="
                    truncate
                    text-[10px]
                    text-slate-600
                  "
                >
                  {userEmail}
                </div>

              </div>


              <ChevronDown
                size={14}
                className={`
                  shrink-0
                  text-slate-600
                  transition-transform
                  ${
                    userOpen
                      ? "rotate-180"
                      : ""
                  }
                `}
              />

            </button>


            {/* User popup */}

            {userOpen && (

              <div
                className="
                  absolute
                  bottom-[calc(100%+8px)]
                  left-0
                  z-50
                  w-full
                  overflow-hidden
                  rounded-xl
                  border
                  border-white/10
                  bg-[#151b2d]
                  shadow-2xl
                  shadow-black/40
                "
              >

                <Link
                  href="/settings"
                  className="
                    flex
                    items-center
                    gap-2.5
                    px-3
                    py-2.5
                    text-[11px]
                    text-slate-300
                    hover:bg-white/[0.05]
                    hover:text-white
                  "
                >
                  <Settings size={14} />
                  Settings
                </Link>


                <button
                  type="button"
                  onClick={() => logout()}
                  className="
                    flex
                    w-full
                    items-center
                    gap-2.5
                    border-t
                    border-white/[0.06]
                    px-3
                    py-2.5
                    text-[11px]
                    text-red-400
                    hover:bg-red-500/10
                  "
                >
                  <LogOut size={14} />
                  Sign out
                </button>

              </div>

            )}

          </div>

        </div>

      </aside>
    );
  };


  // ==========================================================
  // MAIN LAYOUT
  // ==========================================================

  return (

    <div
      className="
        flex
        h-dvh
        w-full
        overflow-hidden
        bg-[#f8f9fc]
      "
    >

      {/* ====================================================
          DESKTOP SIDEBAR
      ===================================================== */}

      <div className="hidden lg:block">
        <Sidebar />
      </div>


      {/* ====================================================
          MOBILE SIDEBAR
      ===================================================== */}

      {mobileOpen && (

        <>
          <button
            aria-label="Close sidebar"
            onClick={() =>
              setMobileOpen(false)
            }
            className="
              fixed
              inset-0
              z-40
              bg-black/50
              lg:hidden
            "
          />

          <div
            className="
              fixed
              inset-y-0
              left-0
              z-50
              lg:hidden
            "
          >
            <Sidebar />
          </div>
        </>

      )}


      {/* ====================================================
          MAIN CONTENT
      ===================================================== */}

      <main
        className="
          flex
          min-w-0
          flex-1
          flex-col
          overflow-hidden
        "
      >

        {/* ==================================================
            HEADER
        ================================================== */}

        <header
          className="
            flex
            h-[72px]
            shrink-0
            items-center
            justify-between
            border-b
            border-slate-200
            bg-white
            px-5
            lg:px-7
          "
        >

          {/* Left */}

          <div
            className="
              flex
              min-w-0
              items-center
              gap-3
            "
          >

            <button
              type="button"
              onClick={() =>
                setMobileOpen(true)
              }
              className="
                rounded-lg
                p-2
                text-slate-500
                hover:bg-slate-100
                lg:hidden
              "
            >
              <Menu size={20} />
            </button>


            <div className="min-w-0">

              <div
                className="
                  flex
                  items-center
                  gap-2
                  text-[15px]
                  font-semibold
                  text-slate-900
                "
              >

                <span className="hidden sm:inline">
                  Company OS
                </span>

                <span
                  className="
                    hidden
                    text-slate-300
                    sm:inline
                  "
                >
                  /
                </span>

                <span
                  className="
                    truncate
                    font-medium
                    text-slate-500
                  "
                >
                  {getPageName(pathname)}
                </span>

              </div>


              <div
                className="
                  mt-0.5
                  hidden
                  text-[11px]
                  text-slate-400
                  md:block
                "
              >
                Your company knowledge, retrieved and cited.
              </div>

            </div>

          </div>


          {/* Right */}

          <div
            className="
              flex
              items-center
              gap-3
            "
          >

            {/* AI status */}

            <div
              className="
                hidden
                items-center
                gap-2
                rounded-full
                border
                border-emerald-200
                bg-emerald-50
                px-3
                py-1.5
                text-xs
                font-medium
                text-emerald-700
                sm:flex
              "
            >

              <span
                className="
                  h-1.5
                  w-1.5
                  rounded-full
                  bg-emerald-500
                "
              />

              AI online

            </div>


            {/* User */}

            <button
              type="button"
              className="
                flex
                h-9
                w-9
                items-center
                justify-center
                rounded-full
                border
                border-slate-200
                bg-white
                text-[11px]
                font-bold
                text-slate-700
                shadow-sm
              "
            >
              {userInitial}
            </button>

          </div>

        </header>


        {/* ==================================================
            PAGE CONTENT
        ================================================== */}

        <div
          className="
            min-h-0
            flex-1
            overflow-y-auto
          "
        >
          {children}
        </div>

      </main>

    </div>
  );
}


// ============================================================
// PAGE NAME
// ============================================================

function getPageName(
  pathname: string
): string {

  if (
    pathname === "/" ||
    pathname === ""
  ) {
    return "Chat";
  }


  const names: Record<string, string> = {

    "/documents":
      "Knowledge",

    "/organizations":
      "Organization",

    "/connectors":
      "Connectors",

    "/crm":
      "CRM",

    "/meetings":
      "Meetings",

    "/tasks":
      "Tasks",

    "/projects":
      "Projects",

    "/people":
      "People",

    "/data":
      "Data",

    "/analytics":
      "Analytics",

    "/settings":
      "Settings",
  };


  const basePath =
    "/" +
    pathname
      .split("/")
      .filter(Boolean)[0];


  return (
    names[basePath] ??
    "Company OS"
  );
}

