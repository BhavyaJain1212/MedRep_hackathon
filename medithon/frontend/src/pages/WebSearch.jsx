import React, { useState } from 'react';
import { Search, Globe, ExternalLink, Loader2, ArrowRight } from 'lucide-react';

export default function WebSearch() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSearch = async (e) => {
        if (e) e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:5000/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await response.json();
            if (response.ok) {
                setResults(data.results || []);
            } else {
                setError(data.error || 'Failed to fetch search results');
            }
        } catch (err) {
            setError('Error connecting to the search service');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-navy-950 text-slate-200 p-6 md:p-10">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <div className="space-y-2">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent flex items-center gap-3">
                        <Globe className="w-8 h-8 text-blue-500" />
                        Web Search
                    </h1>
                    <p className="text-slate-400">Search the latest medical publications, journals, and health news.</p>
                </div>

                {/* Search Bar */}
                <form onSubmit={handleSearch} className="relative group">
                    <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                        <Search className="w-5 h-5 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                    </div>
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search for drugs, studies, or medical news..."
                        className="w-full bg-navy-900/50 border border-navy-700/50 rounded-2xl py-4 pl-12 pr-32 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 backdrop-blur-xl transition-all shadow-2xl"
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="absolute right-2.5 top-2.5 px-6 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium transition-all transform active:scale-95 disabled:opacity-50 disabled:active:scale-100 flex items-center gap-2"
                    >
                        {loading ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <>
                                Search <ArrowRight className="w-4 h-4" />
                            </>
                        )}
                    </button>
                </form>

                {/* Error Message */}
                {error && (
                    <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
                        <span className="w-2 h-2 rounded-full bg-rose-500" />
                        {error}
                    </div>
                )}

                {/* Results Section */}
                <div className="space-y-4">
                    {loading && results.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-20 gap-4 opacity-50">
                            <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
                            <p className="text-slate-400 animate-pulse">Scanning the web for relevant insights...</p>
                        </div>
                    )}

                    {!loading && results.length === 0 && !error && query && (
                        <div className="text-center py-20 text-slate-500">
                            No results found for your query.
                        </div>
                    )}

                    <div className="grid gap-4">
                        {results.map((result, idx) => (
                            <a
                                key={idx}
                                href={result.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="group block p-5 rounded-2xl bg-navy-900/30 border border-navy-800/50 hover:border-blue-500/30 hover:bg-navy-800/40 transition-all duration-300 shadow-lg hover:shadow-blue-500/5"
                            >
                                <div className="flex justify-between items-start gap-4 mb-2">
                                    <h3 className="text-lg font-semibold text-slate-100 group-hover:text-blue-400 transition-colors leading-tight">
                                        {result.title}
                                    </h3>
                                    <ExternalLink className="w-4 h-4 text-slate-600 group-hover:text-blue-400 transition-colors flex-shrink-0 mt-1" />
                                </div>
                                <p className="text-sm text-slate-400 line-clamp-2 leading-relaxed mb-3">
                                    {result.snippet}
                                </p>
                                <div className="flex items-center gap-2 text-[11px] font-medium text-slate-500 tracking-wider uppercase bg-navy-950/50 w-fit px-2 py-1 rounded">
                                    <Globe className="w-3 h-3" />
                                    {result.source || new URL(result.link).hostname}
                                </div>
                            </a>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
