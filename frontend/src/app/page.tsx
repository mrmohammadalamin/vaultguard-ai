"use client";

import { useEffect, useState, useRef } from "react";
import { Terminal, ShieldAlert, CheckCircle, Play, Download, AlertTriangle, Moon, Sun, Check, Loader2, XCircle } from "lucide-react";
import { useTheme } from "next-themes";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";

type LogEntry = {
  timestamp: string;
  msg: string;
  level: "INFO" | "WARN" | "ERROR";
  agent?: string;
};

type ApprovalRequest = {
  action: string;
  risk: string;
  reason: string;
};

const PHASES = [
  "PLANNING",
  "SECURITY_SCAN",
  "DEPENDENCY_ANALYSIS",
  "BUILD",
  "UNIT_TEST",
  "DEPLOY",
  "VERIFY",
  "AUDIT",
  "COMPLETE"
];

export default function Dashboard() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [currentState, setCurrentState] = useState<string>("IDLE");
  const [progress, setProgress] = useState(0);
  const [approvalRequest, setApprovalRequest] = useState<ApprovalRequest | null>(null);
  const [connected, setConnected] = useState(false);
  const [auditData, setAuditData] = useState<any[]>([]);
  const { theme, setTheme } = useTheme();
  const ws = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    connectWebSocket();
    fetchAuditData();
    return () => ws.current?.close();
  }, []);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  useEffect(() => {
    if (currentState === "COMPLETE") {
      fetchAuditData();
    }
  }, [currentState]);

  const fetchAuditData = async () => {
    try {
      const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
      const res = await fetch(`http://${hostname}:8001/api/audit`);
      if (res.ok) {
        const data = await res.json();
        setAuditData(data);
      }
    } catch (e) {
      console.error("Failed to fetch audit data");
    }
  }

  const connectWebSocket = () => {
    const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    ws.current = new WebSocket(`ws://${hostname}:8001/ws`);
    
    ws.current.onopen = () => setConnected(true);
    ws.current.onclose = () => setConnected(false);
    ws.current.onerror = (err) => console.error("WebSocket error:", err);
    
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "log") {
        setLogs((prev) => [...prev, message.data]);
      } else if (message.type === "state_update") {
        setCurrentState(message.data.state);
        setProgress(message.data.progress);
      } else if (message.type === "approval_required") {
        setApprovalRequest(message.data);
      } else if (message.type === "goal_complete") {
        setApprovalRequest(null);
      } else if (message.type === "audit_update") {
        fetchAuditData();
      }
    };
  };

  const startGoal = () => {
    if (!connected) {
      alert("System is currently offline. Waiting for backend connection...");
      return;
    }
    setLogs([]);
    setApprovalRequest(null);
    ws.current?.send(JSON.stringify({ action: "start_goal" }));
  };

  const handleApprove = () => {
    ws.current?.send(JSON.stringify({ action: "approve" }));
    setApprovalRequest(null);
  };

  const handleReject = () => {
    ws.current?.send(JSON.stringify({ action: "reject" }));
    setApprovalRequest(null);
  };

  const downloadAudit = () => {
    const blob = new Blob([JSON.stringify(auditData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "audit_report.json";
    a.click();
  };

  if (!mounted) return null;

  const currentPhaseIndex = PHASES.indexOf(currentState);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300 font-sans p-6">
      
      {/* Header */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-10 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-4 mb-4 md:mb-0">
          <div className="p-3 bg-blue-600 rounded-xl shadow-lg shadow-blue-500/20">
            <ShieldAlert className="text-white w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">VaultGuard AI</h1>
            <p className="text-slate-500 dark:text-slate-400 font-medium">Enterprise Agent Governance Platform</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 bg-white dark:bg-slate-900 px-4 py-2 rounded-full shadow-sm border border-slate-200 dark:border-slate-800">
            <div className={clsx("w-3 h-3 rounded-full animate-pulse", connected ? 'bg-green-500' : 'bg-red-500')} />
            <span className="text-sm font-semibold">{connected ? 'System Online' : 'System Offline'}</span>
          </div>

          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="p-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          >
            {theme === 'dark' ? <Sun className="w-5 h-5 text-yellow-500" /> : <Moon className="w-5 h-5 text-slate-700" />}
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Timeline & Feed */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Action Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-xl shadow-slate-200/50 dark:shadow-none flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold mb-1 flex items-center gap-2">
                <Terminal className="w-5 h-5 text-blue-500" />
                Autonomous Engine
              </h2>
              <p className="text-slate-500 dark:text-slate-400 text-sm">Execute complex workflows with closed-loop engineering.</p>
            </div>
            <button 
              onClick={startGoal}
              disabled={(currentState !== "IDLE" && currentState !== "COMPLETE") || !connected}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:bg-slate-400 px-6 py-3 rounded-lg text-white font-semibold transition shadow-lg shadow-blue-500/30"
            >
              {currentState !== "IDLE" && currentState !== "COMPLETE" ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
              /goal Secure and Deploy
            </button>
          </div>

          {/* Timeline */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
            <h3 className="text-lg font-bold mb-6">Execution Timeline</h3>
            <div className="relative">
              <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-100 dark:bg-slate-800 -translate-y-1/2 rounded-full" />
              <motion.div 
                className="absolute top-1/2 left-0 h-1 bg-blue-500 -translate-y-1/2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
              <div className="flex justify-between relative z-10">
                {PHASES.map((phase, idx) => {
                  const isCompleted = currentPhaseIndex > idx || currentState === "COMPLETE";
                  const isCurrent = currentPhaseIndex === idx && currentState !== "COMPLETE";
                  const isPending = currentPhaseIndex < idx;

                  return (
                    <div key={phase} className="flex flex-col items-center gap-2">
                      <motion.div 
                        initial={false}
                        animate={{
                          backgroundColor: isCompleted ? "#3b82f6" : isCurrent ? "#3b82f6" : theme === 'dark' ? "#1e293b" : "#f1f5f9",
                          borderColor: isCompleted || isCurrent ? "#3b82f6" : theme === 'dark' ? "#334155" : "#cbd5e1",
                          scale: isCurrent ? 1.2 : 1
                        }}
                        className="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors"
                      >
                        {isCompleted && <Check className="w-3 h-3 text-white" />}
                        {isCurrent && <div className="w-2 h-2 rounded-full bg-white animate-pulse" />}
                      </motion.div>
                      <span className={clsx("text-xs font-semibold uppercase tracking-wider", isCurrent ? "text-blue-600 dark:text-blue-400" : isCompleted ? "text-slate-600 dark:text-slate-300" : "text-slate-400 dark:text-slate-600")}>
                        {phase.replace('_', ' ')}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Live Feed */}
          <div className="bg-slate-950 rounded-2xl p-1 shadow-inner border border-slate-800 overflow-hidden relative">
            <div className="absolute top-0 left-0 w-full p-3 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 z-10 flex justify-between items-center text-slate-300 text-xs font-mono tracking-widest">
              <span>AGENT_ACTIVITY_FEED</span>
              <span className="flex items-center gap-2"><span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"/> LIVE</span>
            </div>
            <div className="h-80 overflow-y-auto p-4 pt-14 font-mono text-sm">
              <AnimatePresence>
                {logs.map((log, i) => (
                  <motion.div 
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={clsx(
                      "mb-2 p-2 rounded border-l-2",
                      log.level === 'ERROR' ? "border-red-500 bg-red-500/10 text-red-400" : 
                      log.level === 'WARN' ? "border-yellow-500 bg-yellow-500/10 text-yellow-400" : 
                      "border-blue-500/50 hover:bg-slate-900 text-slate-300"
                    )}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-slate-600">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                      {log.agent && (
                        <span className={clsx(
                          "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest",
                          log.agent === "Master Agent" ? "bg-purple-500/20 text-purple-400" :
                          log.agent === "Security Agent" ? "bg-red-500/20 text-red-400" :
                          log.agent === "Planning Agent" ? "bg-emerald-500/20 text-emerald-400" :
                          log.agent === "Testing Agent" ? "bg-yellow-500/20 text-yellow-400" :
                          "bg-blue-500/20 text-blue-400"
                        )}>
                          {log.agent}
                        </span>
                      )}
                    </div>
                    <div>{log.msg.replace(/^\[.*?\]\s*/, '')}</div>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={logsEndRef} />
            </div>
          </div>

        </div>

        {/* Right Column: Governance & Audit */}
        <div className="space-y-8">
          
          {/* Governance Gateway */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm relative overflow-hidden">
            <div className="flex items-center justify-between mb-6 relative z-10">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-red-500" />
                Governance Gate
              </h3>
            </div>

            <AnimatePresence mode="wait">
              {approvalRequest ? (
                <motion.div 
                  key="approval"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 p-5 rounded-xl relative z-10"
                >
                  <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-bold mb-3">
                    <AlertTriangle className="w-5 h-5 animate-pulse" /> ACTION INTERCEPTED
                  </div>
                  <div className="space-y-3 mb-6">
                    <div className="bg-white dark:bg-slate-950 p-3 rounded border border-slate-200 dark:border-slate-800">
                      <span className="text-xs text-slate-500 block mb-1">Command</span>
                      <code className="text-sm font-mono text-pink-600 dark:text-pink-400">{approvalRequest.action}</code>
                    </div>
                    <div>
                      <span className="text-xs text-slate-500 block">Risk Level</span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300 uppercase tracking-wider mt-1 border border-red-200 dark:border-red-800">
                        {approvalRequest.risk}
                      </span>
                    </div>
                    <div>
                      <span className="text-xs text-slate-500 block">Policy Reason</span>
                      <p className="text-sm font-medium mt-1 dark:text-slate-300">{approvalRequest.reason}</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-3">
                    <button onClick={handleApprove} className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2.5 rounded-lg font-semibold transition shadow-md shadow-green-600/20 flex items-center justify-center gap-2">
                      <CheckCircle className="w-4 h-4" /> Approve
                    </button>
                    <button onClick={handleReject} className="flex-1 bg-slate-800 hover:bg-slate-700 dark:bg-slate-950 dark:hover:bg-slate-900 text-white py-2.5 rounded-lg font-semibold transition border border-slate-700 dark:border-slate-800 flex items-center justify-center gap-2">
                      <XCircle className="w-4 h-4" /> Reject
                    </button>
                  </div>
                </motion.div>
              ) : (
                <motion.div 
                  key="idle"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center py-12 text-slate-400 relative z-10"
                >
                  <ShieldAlert className="w-16 h-16 mb-4 opacity-20" />
                  <p className="font-medium text-slate-500">No Pending Approvals</p>
                  <p className="text-xs mt-1">Policies enforced autonomously.</p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-[0.03] dark:opacity-[0.02] pointer-events-none" style={{ backgroundImage: "radial-gradient(#000 1px, transparent 1px)", backgroundSize: "16px 16px" }} />
          </div>

          {/* Audit Log Table Snapshot */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Recent Audits</h3>
              <button onClick={downloadAudit} className="text-blue-600 hover:text-blue-700 dark:text-blue-400 text-sm font-semibold flex items-center gap-1">
                <Download className="w-4 h-4" /> JSON
              </button>
            </div>
            
            <div className="space-y-3">
              {auditData.length === 0 && <div className="text-sm text-slate-500 py-4 text-center">No audits yet.</div>}
              {auditData.slice().reverse().slice(0, 5).map((log, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800">
                  <div className="truncate pr-4">
                    <div className="text-sm font-mono font-medium truncate">{log.action}</div>
                    <div className="text-xs text-slate-500 mt-1">{new Date(log.timestamp).toLocaleTimeString()} • {log.execution_time_ms}ms</div>
                  </div>
                  <div className="flex-shrink-0">
                    <span className={clsx(
                      "text-xs px-2 py-1 rounded font-bold uppercase tracking-wider",
                      log.policy_decision === "ALLOW" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" :
                      log.policy_decision === "REQUIRE_APPROVAL" ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" :
                      "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                    )}>
                      {log.policy_decision === "REQUIRE_APPROVAL" ? log.approval_event || "PENDING" : log.policy_decision}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </main>
    </div>
  );
}
