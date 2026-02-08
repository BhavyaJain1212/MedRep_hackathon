import { NavLink } from "react-router-dom";
import {
  MessageSquare,
  Pill,
  Activity,
  Globe,
} from "lucide-react";

const links = [
  { to: "/", icon: MessageSquare, label: "Chat" },
  { to: "/drugs", icon: Pill, label: "Drug Explorer" },
  { to: "/search", icon: Globe, label: "Search Web" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 flex flex-col border-r border-navy-700/50 bg-navy-900/80 backdrop-blur-sm">
      {/* Brand */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-navy-700/40">
        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-sky-400">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-base font-semibold text-slate-100 leading-tight">
            MedRep
          </h1>
          <p className="text-[11px] text-slate-400 leading-tight">
            Digital Medical Representative
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${isActive
                ? "bg-blue-500/15 text-blue-400 border border-blue-500/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-navy-700/40 border border-transparent"
              }`
            }
          >
            <Icon className="w-[18px] h-[18px] flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-navy-700/40">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[11px] text-slate-400">
            Medithon 2025 — Track 2
          </span>
        </div>
      </div>
    </aside>
  );
}
