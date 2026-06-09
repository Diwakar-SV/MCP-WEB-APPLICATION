import React, { useState } from 'react';
import { Sparkles, Terminal, Cpu, CheckCircle, AlertTriangle, Play } from 'lucide-react';

interface Step {
  step_number: number;
  thought: string;
  action: string;
  observation: string;
  timestamp: string;
}

interface AgentSimulatorProps {
  token: string | null;
  addToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

export const AgentSimulator: React.FC<AgentSimulatorProps> = ({ token, addToast }) => {
  const [issue, setIssue] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(-1);
  const [steps, setSteps] = useState<Step[]>([]);
  const [finalResponse, setFinalResponse] = useState('');
  const [priority, setPriority] = useState('');
  const [actionType, setActionType] = useState<'CREATE' | 'COMMENT' | null>(null);
  const [affectedId, setAffectedId] = useState<number | null>(null);
  const [isDuplicate, setIsDuplicate] = useState(false);
  
  // Quick pre-set examples for interview demonstrations
  const examples = [
    { text: "Production database queries are taking over 5 seconds", label: "Critical Database (Outage)" },
    { text: "My Cisco VPN is not connecting. It gets stuck on Duo push notifications.", label: "VPN Connection Issue" },
    { text: "The hydraulic cylinder in my desk chair is sinking to the floor", label: "Broken Desk Chair" },
    { text: "Requesting access to GitHub Copilot for the team", label: "Software License Request" }
  ];

  const handleRunAgent = async (issueText: string) => {
    if (!issueText.trim()) {
      addToast('Please enter an issue description.', 'error');
      return;
    }

    setLoading(true);
    setIssue(issueText);
    setSteps([]);
    setFinalResponse('');
    setCurrentStepIdx(-1);
    setPriority('');
    setActionType(null);
    setAffectedId(null);
    setIsDuplicate(false);

    try {
      const response = await fetch('http://localhost:8000/api/agent/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ issue: issueText }),
      });

      if (!response.ok) {
        throw new Error('Failed to run agent workflow.');
      }

      const data = await response.json();
      
      // Extract metadata state
      const state = data.state || {};
      setPriority(state.priority || 'LOW');
      setIsDuplicate(state.is_duplicate || false);
      
      if (state.created_ticket_id) {
        setActionType('CREATE');
        setAffectedId(state.created_ticket_id);
      } else if (state.duplicate_ticket_id) {
        setActionType('COMMENT');
        setAffectedId(state.duplicate_ticket_id);
      }

      // Playback steps sequentially to simulate real-time agent reasoning
      const fetchedSteps = data.steps || [];
      setSteps(fetchedSteps);
      
      // Trigger sequential playback
      let idx = 0;
      setCurrentStepIdx(0);
      const interval = setInterval(() => {
        idx++;
        if (idx < fetchedSteps.length) {
          setCurrentStepIdx(idx);
        } else {
          clearInterval(interval);
          setFinalResponse(data.final_response || '');
          setLoading(false);
          addToast('Agent completed reasoning loop!', 'success');
        }
      }, 1500); // 1.5 seconds per step

    } catch (err: any) {
      addToast(err.message || 'Error executing agent', 'error');
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Title block */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl text-white">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-600 rounded-xl text-white shadow-lg shadow-indigo-600/30">
            <Cpu className="w-8 h-8 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-bold text-xl tracking-tight">AI Agent Simulator</h2>
              <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full text-[10px] uppercase font-bold tracking-wider">
                ReAct Core
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Demonstrating Multi-Step Reasoning, Priority Detection, and Duplicate Ticket Mitigation
            </p>
          </div>
        </div>
        
        {/* API mode status */}
        <div className="flex items-center gap-2 self-start md:self-auto text-xs px-3.5 py-2 bg-slate-800/80 border border-slate-700/60 rounded-xl text-slate-300">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
          <span>Agent Service Status: <b>Online</b></span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: User Input & Presets */}
        <div className="lg:col-span-1 space-y-6">
          <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
            <h3 className="font-bold text-slate-800 dark:text-white text-md tracking-tight mb-4 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-500" />
              1. Issue Submission
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                  Describe User Issue
                </label>
                <textarea
                  value={issue}
                  onChange={(e) => setIssue(e.target.value)}
                  placeholder="Describe what is wrong in detail..."
                  rows={4}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm outline-none focus:border-indigo-500 text-slate-800 dark:text-slate-200 focus:ring-1 focus:ring-indigo-500 transition-all resize-none"
                  disabled={loading}
                />
              </div>

              <button
                onClick={() => handleRunAgent(issue)}
                disabled={loading || !issue.trim()}
                className="flex items-center justify-center gap-1.5 w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/20 transition-all active:scale-[0.98] duration-200 text-sm"
              >
                <Play className="w-4 h-4" />
                <span>Run ReAct Agent Workflow</span>
              </button>
            </div>

            {/* Presets/Templates */}
            <div className="mt-6 border-t border-slate-100 dark:border-slate-800/80 pt-5">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-3">
                Demo Interview Presets
              </span>
              <div className="space-y-2">
                {examples.map((ex, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setIssue(ex.text);
                      handleRunAgent(ex.text);
                    }}
                    disabled={loading}
                    className="w-full text-left p-3 text-xs bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-950 dark:hover:bg-slate-800/60 border border-slate-200/60 dark:border-slate-800/50 hover:border-indigo-300 dark:hover:border-indigo-900 rounded-xl transition-all text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium"
                  >
                    <div className="font-semibold text-slate-700 dark:text-slate-300 mb-0.5 truncate">{ex.label}</div>
                    <div className="text-[11px] text-slate-500 truncate">{ex.text}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Reasoning Steps Terminal Visualizer */}
        <div className="lg:col-span-2 space-y-6">
          {/* Terminal Console */}
          <div className="p-5 bg-slate-950 border border-slate-800 rounded-2xl shadow-xl flex flex-col h-[520px]">
            <div className="flex items-center justify-between border-b border-slate-800/60 pb-3 mb-4">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                <Terminal className="w-4 h-4 text-emerald-500" />
                <span>REASONING WORKFLOW TRACE</span>
              </div>
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 font-mono text-xs text-slate-300 pr-1 select-text">
              {currentStepIdx === -1 && !loading && (
                <div className="flex flex-col items-center justify-center h-full text-slate-600 text-center p-6">
                  <Terminal className="w-12 h-12 mb-3 opacity-30" />
                  <p>Agent engine is idle.</p>
                  <p className="text-[10px] mt-1">Submit an issue or pick a preset to trigger the ReAct loop.</p>
                </div>
              )}

              {loading && currentStepIdx === -1 && (
                <div className="flex flex-col items-center justify-center h-full text-slate-500 text-center">
                  <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-3" />
                  <p>Initializing ReAct planner engine...</p>
                </div>
              )}

              {steps.map((step, idx) => {
                if (idx > currentStepIdx) return null;
                return (
                  <div key={idx} className="space-y-2 border-l-2 border-indigo-900/60 pl-3 animate-fade-in">
                    {/* Timestamp / step indicator */}
                    <div className="flex items-center gap-2 text-[10px] text-slate-500">
                      <span>STEP {step.step_number}</span>
                      <span>•</span>
                      <span>{new Date(step.timestamp).toLocaleTimeString()}</span>
                    </div>

                    {/* Agent Thought */}
                    <div className="bg-indigo-950/20 border border-indigo-900/40 rounded-xl p-3 text-slate-200 leading-relaxed">
                      <span className="text-indigo-400 font-semibold uppercase text-[10px] tracking-wider block mb-1">
                        Thought
                      </span>
                      {step.thought}
                    </div>

                    {/* Tool Action Call */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 font-semibold text-emerald-400">
                      <span className="text-emerald-500 font-semibold uppercase text-[10px] tracking-wider block mb-1">
                        Action Call
                      </span>
                      &gt; {step.action}
                    </div>

                    {/* Observation Result */}
                    <div className="bg-slate-900/40 border border-slate-900/80 rounded-xl p-3 text-slate-400 leading-normal max-h-48 overflow-y-auto whitespace-pre-wrap">
                      <span className="text-slate-500 font-semibold uppercase text-[10px] tracking-wider block mb-1">
                        Observation Output
                      </span>
                      {step.observation}
                    </div>
                  </div>
                );
              })}

              {/* Loader placeholder inside terminal */}
              {loading && currentStepIdx > -1 && currentStepIdx < steps.length - 1 && (
                <div className="flex items-center gap-2 text-indigo-400 italic animate-pulse pl-3 py-2 border-l-2 border-dashed border-indigo-900">
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" />
                  <span>Thinking next step...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Final Outcome Results Card */}
      {(finalResponse || priority) && (
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm animate-slide-up space-y-6">
          <h3 className="font-bold text-slate-800 dark:text-white text-md tracking-tight flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-500" />
            2. Resolution Summary & Database Impact
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Priority Widget */}
            <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800 flex flex-col justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
                Detected Priority
              </span>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  priority === 'CRITICAL' || priority === 'HIGH' 
                    ? 'bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 border border-rose-100 dark:border-rose-900/50' 
                    : priority === 'MEDIUM' 
                      ? 'bg-amber-50 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400 border border-amber-100 dark:border-amber-900/50'
                      : 'bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/50'
                }`}>
                  {priority}
                </span>
              </div>
            </div>

            {/* Duplicate Check Widget */}
            <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800 flex flex-col justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
                Duplicate Status
              </span>
              <span className={`text-sm font-bold flex items-center gap-1.5 ${
                isDuplicate ? 'text-amber-500' : 'text-emerald-500'
              }`}>
                {isDuplicate ? (
                  <>
                    <AlertTriangle className="w-4 h-4" />
                    Duplicate Found
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Unique Request
                  </>
                )}
              </span>
            </div>

            {/* Action Triggered Widget */}
            <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800 flex flex-col justify-between col-span-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
                Database Operation
              </span>
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-400">
                {actionType === 'CREATE' && (
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-50 dark:bg-emerald-950/20 px-2 py-1 border border-emerald-100 dark:border-emerald-900/40 rounded-lg">
                    CREATE_TICKET (New Ticket #{affectedId})
                  </span>
                )}
                {actionType === 'COMMENT' && (
                  <span className="text-amber-600 dark:text-amber-400 font-bold bg-amber-50 dark:bg-amber-950/20 px-2 py-1 border border-amber-100 dark:border-amber-900/40 rounded-lg">
                    ADD_COMMENT (Ticket #{affectedId} Thread Updated)
                  </span>
                )}
                {!actionType && <span className="text-slate-400">None</span>}
              </div>
            </div>
          </div>

          {/* Final response markdown text panel */}
          <div className="p-5 bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 rounded-xl">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
              Final Summary Response to User
            </span>
            <div className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {finalResponse}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
