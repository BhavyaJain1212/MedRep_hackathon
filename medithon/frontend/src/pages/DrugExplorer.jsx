import { useState } from "react";
import { Search, Pill, Tag, DollarSign, FileText, ChevronDown, ChevronUp } from "lucide-react";
import { getDrug } from "../services/api";

/* ── Static data for offline demo ── */
import drugsMaster from "../../../backend/data/drugs_master.json";
const drugList = drugsMaster.drugs;

function DrugCard({ drug, expanded, onToggle }) {
  const savings = drug.savings_percent
    ? `${Math.round(drug.savings_percent)}%`
    : "N/A";

  return (
    <div className="glass-card rounded-xl overflow-hidden transition-all">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-navy-700/20 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
            <Pill className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">
              {drug.generic_name}
            </h3>
            <p className="text-xs text-slate-400">
              {drug.category} · {drug.primary_strength}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {drug.savings_percent > 0 && (
            <span className="px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/15 text-emerald-400">
              Save {savings}
            </span>
          )}
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="px-5 pb-5 space-y-4 border-t border-navy-700/30 pt-4">
          {/* Brands */}
          {drug.brands && drug.brands.length > 0 && (
            <div>
              <p className="text-[11px] uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1">
                <Tag className="w-3 h-3" /> Brands
              </p>
              <div className="flex flex-wrap gap-1.5">
                {drug.brands.map((b) => (
                  <span
                    key={b}
                    className="px-2.5 py-1 rounded-md text-xs bg-navy-700/50 text-slate-300"
                  >
                    {b}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Pricing row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg bg-navy-800/50 px-4 py-3">
              <p className="text-[11px] uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1">
                <DollarSign className="w-3 h-3" /> Brand MRP
              </p>
              <p className="text-base font-semibold text-slate-100">
                {drug.brand_mrp
                  ? `₹${drug.brand_mrp.mrp}`
                  : "Not available"}
              </p>
              {drug.brand_mrp && (
                <p className="text-[10px] text-slate-400 mt-0.5">
                  {drug.brand_mrp.name} · {drug.brand_mrp.pack}
                </p>
              )}
            </div>
            <div className="rounded-lg bg-emerald-500/5 border border-emerald-500/10 px-4 py-3">
              <p className="text-[11px] uppercase tracking-wider text-emerald-400/70 mb-1">
                Jan Aushadhi
              </p>
              <p className="text-base font-semibold text-emerald-400">
                {drug.jan_aushadhi_mrp
                  ? `₹${drug.jan_aushadhi_mrp.mrp}`
                  : "Not listed"}
              </p>
              {drug.jan_aushadhi_mrp && (
                <p className="text-[10px] text-emerald-400/50 mt-0.5">
                  {drug.jan_aushadhi_mrp.variant} · {drug.jan_aushadhi_mrp.pack}
                </p>
              )}
            </div>
          </div>

          {/* CGHS / ESIC */}
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg bg-navy-800/50 px-4 py-3">
              <p className="text-[11px] uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1">
                <FileText className="w-3 h-3" /> CGHS
              </p>
              <p className="text-xs text-slate-300 leading-relaxed">
                {drug.cghs_codes && drug.cghs_codes.length > 0
                  ? drug.cghs_codes.join(", ")
                  : drug.cghs_entry || "Bucket-level coverage"}
              </p>
            </div>
            <div className="rounded-lg bg-navy-800/50 px-4 py-3">
              <p className="text-[11px] uppercase tracking-wider text-slate-400 mb-1">
                ESIC
              </p>
              <StatusBadge status={drug.esic_status} />
              {drug.esic_detail && (
                <p className="text-[10px] text-slate-400 mt-1">
                  {drug.esic_detail}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }) {
  const styles = {
    yes: "bg-emerald-500/15 text-emerald-400",
    no: "bg-rose-500/15 text-rose-400",
    fdc_only: "bg-amber-500/15 text-amber-400",
    kit_only: "bg-amber-500/15 text-amber-400",
    not_verified: "bg-slate-500/15 text-slate-400",
  };
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${styles[status] || styles.not_verified
        }`}
    >
      {status?.replace("_", " ") || "unknown"}
    </span>
  );
}

const CATEGORIES = [
  "All",
  "Pain Management",
  "Antibiotics",
  "Diabetes",
  "Cardiovascular",
  "Gastrointestinal",
  "Respiratory",
];

export default function DrugLookup() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [expandedId, setExpandedId] = useState(null);

  const filtered = drugList.filter((d) => {
    const matchSearch =
      d.generic_name.toLowerCase().includes(search.toLowerCase()) ||
      (d.brands || []).some((b) =>
        b.toLowerCase().includes(search.toLowerCase())
      );
    const matchCat = category === "All" || d.category === category;
    return matchSearch && matchCat;
  });

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-1">
          Drug Lookup
        </h2>
        <p className="text-sm text-slate-400">
          Browse all {drugList.length} drugs — pricing, CGHS codes, ESIC status
        </p>
      </div>

      {/* Search + Filter */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by generic name or brand..."
            className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-navy-800 border border-navy-600/50 text-sm text-slate-200 placeholder-slate-500 input-glow focus:outline-none focus:border-blue-500/40 transition-all"
          />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {CATEGORIES.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${category === c
                  ? "bg-blue-500/15 text-blue-400 border border-blue-500/20"
                  : "text-slate-400 hover:text-slate-300 bg-navy-800 border border-navy-700/50"
                }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div className="space-y-2">
        {filtered.length === 0 && (
          <p className="text-sm text-slate-400 text-center py-8">
            No drugs match your search.
          </p>
        )}
        {filtered.map((d) => (
          <DrugCard
            key={d.id}
            drug={d}
            expanded={expandedId === d.id}
            onToggle={() =>
              setExpandedId(expandedId === d.id ? null : d.id)
            }
          />
        ))}
      </div>
    </div>
  );
}
