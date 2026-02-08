import React from 'react';
import {
    AlertTriangle,
    CheckCircle,
    Info,
    ShieldAlert,
    Banknote,
    FileText,
    Activity,
    Pill
} from 'lucide-react';

export default function MedicalResponse({ data }) {
    if (!data) return null;

    return (
        <div className="space-y-4 w-full">
            {/* 1. Summary Section */}
            <div className="bg-navy-800/50 rounded-lg p-3 border border-navy-700/50">
                <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5" /> Summary
                </h4>
                <p className="text-sm text-slate-200 leading-relaxed">
                    {data.summary}
                </p>
            </div>

            {/* 2. Drug Info (Optional) */}
            {data.drug_information && (
                <div className="bg-navy-800/30 rounded-lg p-3 mt-2">
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <Pill className="w-3.5 h-3.5" /> Drug Info
                    </h4>
                    <p className="text-xs text-slate-300">
                        {data.drug_information}
                    </p>
                </div>
            )}

            {/* 3. Interactions Display */}
            {data.interactions && data.interactions.length > 0 && (
                <div className="space-y-2 mt-2">
                    <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5" /> Interactions Detected
                    </h4>
                    {data.interactions.map((interaction, idx) => (
                        <div key={idx} className={`p-3 rounded-lg border ${interaction.severity === 'CRITICAL' ? 'bg-rose-500/10 border-rose-500/30' :
                            interaction.severity === 'MAJOR' ? 'bg-orange-500/10 border-orange-500/30' :
                                'bg-yellow-500/5 border-yellow-500/20'
                            }`}>
                            <div className="flex justify-between items-start mb-1">
                                <span className="font-semibold text-slate-200 text-sm">
                                    {interaction.drugs_involved.join(' + ')}
                                </span>
                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${interaction.severity === 'CRITICAL' ? 'bg-rose-500 text-white' :
                                    interaction.severity === 'MAJOR' ? 'bg-orange-500 text-white' :
                                        'bg-yellow-500/20 text-yellow-400'
                                    }`}>
                                    {interaction.severity}
                                </span>
                            </div>
                            <p className="text-xs text-slate-300 mb-2">
                                {interaction.description}
                            </p>
                            <div className="flex items-start gap-1.5 text-xs text-slate-400 bg-black/20 p-2 rounded">
                                <Info className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
                                <span>{interaction.recommendation}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* 4. Safety Warnings */}
            {data.safety_warnings && data.safety_warnings.length > 0 && (
                <div className="space-y-2 mt-2">
                    <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <ShieldAlert className="w-3.5 h-3.5" /> Safety Warnings
                    </h4>
                    {data.safety_warnings.map((warning, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
                            <div className="flex items-center gap-2 mb-1">
                                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">
                                    {warning.category}
                                </span>
                                <span className="text-xs font-medium text-slate-200">
                                    {warning.condition}
                                </span>
                            </div>
                            <p className="text-xs text-slate-300">
                                {warning.description}
                            </p>
                        </div>
                    ))}
                </div>
            )}

            {/* 5. Reimbursement */}
            {data.reimbursement && (
                <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-lg p-3 mt-2">
                    <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <Banknote className="w-3.5 h-3.5" /> Reimbursement & Pricing
                    </h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                            <span className="text-slate-400 block mb-0.5">Status</span>
                            <span className="text-emerald-300 font-medium">
                                {data.reimbursement.coverage_status}
                            </span>
                        </div>
                        {data.reimbursement.price_range && (
                            <div>
                                <span className="text-slate-400 block mb-0.5">Price Range</span>
                                <span className="text-slate-200">
                                    {data.reimbursement.price_range}
                                </span>
                            </div>
                        )}
                        {data.reimbursement.restrictions && (
                            <div className="col-span-2 mt-1 pt-1 border-t border-emerald-500/10">
                                <span className="text-slate-400 block mb-0.5">Restrictions</span>
                                <span className="text-slate-300">
                                    {data.reimbursement.restrictions}
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* 6. Recommendations */}
            {data.recommendations && (
                <div className="bg-blue-500/5 border-l-2 border-blue-500 pl-3 py-2 rounded-r-lg mt-2">
                    <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-1">
                        Clinical Recommendation
                    </h4>
                    <p className="text-sm text-slate-200">
                        {data.recommendations}
                    </p>
                </div>
            )}

            {/* 7. Data Limitations */}
            {data.data_limitations && (
                <div className="text-xs text-slate-400 italic mt-2">
                    ⚠️ Note: {data.data_limitations} [unverified]
                </div>
            )}

            {/* 8. Sources */}
            {data.sources && data.sources.length > 0 && (
                <div className="pt-2 border-t border-navy-700/50 mt-2">
                    <p className="text-[10px] uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-1">
                        <FileText className="w-3 h-3" /> Sources
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                        {data.sources.map((s, idx) => (
                            <div
                                key={idx}
                                className="px-2 py-0.5 text-[10px] rounded-full bg-navy-800 text-slate-400 border border-navy-700 max-w-full truncate"
                                title={s.snippet}
                            >
                                {s.database}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* 9. Disclaimer */}
            <p className="text-[10px] text-slate-500 pt-1 text-center mt-2">
                {data.disclaimer}
            </p>
        </div>
    );
}
