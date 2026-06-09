import React, { useEffect, useState } from 'react';
import { Search, ChevronDown, ChevronUp, BookOpen, AlertCircle, HelpCircle } from 'lucide-react';
import type { KBArticle } from '../types';

interface KnowledgeBaseProps {
  token?: string | null;
  addToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

export const KnowledgeBase: React.FC<KnowledgeBaseProps> = ({ addToast }) => {
  const [articles, setArticles] = useState<KBArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const fetchKB = async () => {
    setLoading(true);
    try {
      let url = 'http://localhost:8000/api/kb/search';
      if (search) {
        url += `?query=${encodeURIComponent(search)}`;
      }
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to retrieve knowledge base records.');
      }
      const data = await response.json();
      setArticles(data);
    } catch (err: any) {
      addToast(err.message || 'Error fetching KB', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKB();
  }, [search]);

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Search Header */}
      <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
          <BookOpen className="w-5 h-5" />
          <h3 className="font-semibold text-sm uppercase tracking-wider">Search documentation</h3>
        </div>
        <div className="relative">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-slate-400">
            <Search className="w-5 h-5" />
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Type search terms like 'VPN', 'password', 'reimbursement'..."
            className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-800 dark:text-slate-200 transition-all text-sm"
          />
        </div>
      </div>

      {/* Articles Feed */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
        </div>
      ) : articles.length > 0 ? (
        <div className="space-y-3">
          {articles.map((article) => {
            const isExpanded = expandedId === article.id;
            return (
              <div
                key={article.id}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden transition-all duration-200"
              >
                {/* Accordion Trigger Header */}
                <button
                  onClick={() => toggleExpand(article.id)}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-slate-50/50 dark:hover:bg-slate-800/20"
                >
                  <div className="space-y-1.5 flex-1 min-w-0 pr-4">
                    <span className="inline-flex px-2 py-0.5 bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/50 text-[10px] font-bold rounded">
                      {article.category}
                    </span>
                    <h4 className="font-semibold text-slate-800 dark:text-white text-sm sm:text-base tracking-tight leading-snug">
                      {article.question}
                    </h4>
                  </div>
                  <div className="text-slate-400">
                    {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </div>
                </button>

                {/* Expandable answer panel */}
                {isExpanded && (
                  <div className="px-5 pb-5 pt-1 text-sm bg-slate-50/40 dark:bg-slate-950/20 border-t border-slate-100 dark:border-slate-850">
                    <div className="flex gap-2 text-slate-600 dark:text-slate-400 mt-2">
                      <HelpCircle className="w-5 h-5 text-indigo-500 flex-shrink-0 mt-0.5" />
                      <p className="leading-relaxed whitespace-pre-line text-sm">
                        {article.answer}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <AlertCircle className="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
          <h3 className="font-semibold text-slate-700 dark:text-slate-300 text-lg">No matches found</h3>
          <p className="text-slate-400 dark:text-slate-500 text-sm max-w-sm mt-1">
            Try looking up a different help topic or category keyword.
          </p>
        </div>
      )}
    </div>
  );
};
