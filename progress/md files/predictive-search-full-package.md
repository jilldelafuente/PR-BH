# Predictive Search — Full Pattern Package

> Downloaded from the AI Pattern Engine on June 11, 2026

## How to Use This Package

This is a complete, self-contained pattern package. You can paste this entire file into Claude, ChatGPT, or any AI assistant and ask it to:
- Customize the design system (colors, typography, branding)
- Add new sections or features
- Adapt the pattern for a different industry or use case
- Extract specific components for reuse
- Generate tests or documentation

---

## Pattern Metadata

| Field | Value |
|-------|-------|
| **ID** | ai-001 |
| **Name** | Predictive Search |
| **Use Case** | Discovery |
| **Category** | Flagship AI Tools |
| **Modality** | Web, Chat |
| **AI Enabled** | No |
| **Confidence** | 0.92 |
| **Memory** | Session |
| **Autonomy** | Assistive |
| **Context** | Operational |
| **Keywords** | search, find, anticipate, autocomplete, query, intent, discovery, navigation, lookup |

**Description:** Anticipates user intent based on current session behavior and historical data to suggest results before typing completes.

---

## Opportunity Brief

### Client Challenge
Users struggle with search - either they don't find what they need, or finding it requires multiple query reformulations. They don't know what to search for, or results don't match intent. Search abandonment is high.

### What This Pattern Addresses
Intent-aware search that predicts what users are looking for as they type, surfaces relevant results before query completion, and suggests searches they might not know to try.

### How It Works
User starts typing: "How do I..." Pattern analyzes: Intent Detection (Recognizes troubleshooting pattern), Context (User role, current location in system, recent activity), History (Past search behavior and clicked results). Instantly provides: Most likely answer to common troubleshooting question, Related scenarios: "Reset password", "Contact support", "Documentation", Alternative searches: "Tutorial videos", "Common errors". Results appear before user finishes typing. User often finds answer without completing search (zero-click satisfaction).

### Value Potential
- Reduced need for query reformulation
- Improved result relevance and user satisfaction
- Increased zero-click satisfaction (answer without clicking)
- Decreased support tickets for "can't find X"

### Common Use Cases
- **Enterprise Knowledge Bases:** Employee self-service
- **E-commerce:** Product discovery
- **Support Portals:** Customer self-service
- **Content Platforms:** Content discovery

### Implementation Approach
- **Discovery:** Analyze search patterns and failure cases
- **Pilot:** Deploy on subset with metrics comparison
- **Scale:** Expand with continuous learning from behavior
- **Integration Points:** Search infrastructure, content index, behavior tracking
- **Consideration:** Requires search analytics and query logs

### Questions This Pattern Answers
- What is this user really looking for?
- What are likely next searches?
- Can we answer before they finish typing?
- What relevant content might they not know exists?

### Conversation Starters
- "What percentage of searches result in zero results?"
- "How often do users reformulate their search queries?"
- "How many support tickets start with 'I can't find...'?"

### Internal Positioning
This addresses search effectiveness. Clients have search bars but users still can't find things. This goes beyond autocomplete to intent prediction - understanding what they're trying to accomplish and surfacing it proactively.

---

## Tech Stack & Dependencies

- **Framework:** React 18 + TypeScript
- **Styling:** Tailwind CSS (utility-first)
- **Animation:** Framer Motion
- **Icons:** Lucide React
- **Routing:** Wouter
- **Backend:** Express.js + Node.js
- **AI:** OpenAI API (GPT-4o / GPT-4o-mini)

---

## File Manifest

| File | Purpose | Lines |
|------|---------|-------|
| `client/src/pages/search-pattern.tsx` | Main component (UI + logic) | 962 |
| `server/services/ai-predictive-search.ts` | AI service (OpenAI calls) | 246 |

---

## Source Code

### Main Component — `search-pattern.tsx`

```tsx
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, Search, Brain, Sparkles, TrendingUp, Shield, Lock, Eye, CheckCircle2, Building2, Heart, ShoppingCart, Laptop, Zap, Play, AlertTriangle, Database, FileText, Calendar, Headphones, Layers, GitBranch, Network, Clock, ChevronRight, BarChart3, Users } from "lucide-react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { searchScenarios, searchComponents, SearchScenario, industryScenarios, IndustryVertical, roiMetrics, guardrailControls } from "@/lib/search-data";
import { SearchSimulation } from "@/components/search-simulation";
import { SearchComponent } from "@/components/search-component";
import { cn } from "@/lib/utils";

const industries: { id: IndustryVertical; name: string; icon: any; color: string }[] = [
  { id: "Healthcare", name: "Healthcare", icon: Heart, color: "from-red-500 to-rose-600" },
  { id: "Finance", name: "Finance", icon: Building2, color: "from-emerald-500 to-green-600" },
  { id: "Retail", name: "Retail", icon: ShoppingCart, color: "from-orange-500 to-amber-600" },
  { id: "Technology", name: "Technology", icon: Laptop, color: "from-blue-500 to-cyan-600" }
];

const sourceIcons: Record<string, any> = {
  crm: Users,
  knowledge_base: FileText,
  analytics: BarChart3,
  support: Headphones,
  documents: FileText,
  calendar: Calendar
};

const sourceColors: Record<string, string> = {
  crm: "from-blue-500 to-blue-600",
  knowledge_base: "from-purple-500 to-purple-600",
  analytics: "from-emerald-500 to-emerald-600",
  support: "from-amber-500 to-amber-600",
  documents: "from-rose-500 to-rose-600",
  calendar: "from-cyan-500 to-cyan-600"
};

const exampleQueries: Record<IndustryVertical, string[]> = {
  Healthcare: [
    "Which patients missed their follow-up appointments last month and have open claims?",
    "Show me providers with high satisfaction scores who accept our top 3 insurance plans",
    "Find all diabetic patients due for A1C testing who haven't been contacted"
  ],
  Finance: [
    "Which enterprise deals are at risk of churning and what support tickets do they have open?",
    "Compare Q3 revenue by region against our forecast and find the underperformers",
    "Find all pending approvals over $10k and cross-reference with budget remaining"
  ],
  Retail: [
    "Which products have increasing returns and what are customers saying in reviews?",
    "Find our top 100 customers by lifetime value who haven't purchased in 60 days",
    "Show inventory levels for trending items and match with upcoming promotions"
  ],
  Technology: [
    "Which deployments caused latency spikes and were there related support tickets?",
    "Find engineers who worked on the auth service and check their availability this week",
    "Show me all critical bugs assigned to my team and correlate with customer escalations"
  ]
};

interface FederatedResult {
  queryDecomposition: {
    originalQuery: string;
    subTasks: { id: string; description: string; targetSource: string; status: string; reasoning: string }[];
  };
  sources: {
    id: string;
    name: string;
    type: string;
    status: string;
    resultCount: number;
    latencyMs: number;
    results: { title: string; snippet: string; relevance: number; metadata: Record<string, string>; actionable: boolean; actionLabel?: string }[];
  }[];
  synthesizedInsight: string;
  crossSystemConnections: { insight: string; sources: string[]; confidence: number }[];
  suggestedWorkflow: { id: string; action: string; system: string; description: string; estimatedTime: string; requiresApproval: boolean; dependencies: string[] }[];
  executiveSummary: string;
  autonomyAssessment: { level: string; reasoning: string; humanCheckpoints: string[] };
}

export default function SearchPattern() {
  const [_, setLocation] = useLocation();
  const [selectedIndustry, setSelectedIndustry] = useState<IndustryVertical>("Technology");
  const [activeScenario, setActiveScenario] = useState<SearchScenario>(industryScenarios.Technology[0]);
  const [liveQuery, setLiveQuery] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [liveDiagnosis, setLiveDiagnosis] = useState<any>(null);
  const [executingAction, setExecutingAction] = useState<string | null>(null);
  const [executedActions, setExecutedActions] = useState<string[]>([]);

  const [federatedQuery, setFederatedQuery] = useState("");
  const [isFederating, setIsFederating] = useState(false);
  const [federatedResult, setFederatedResult] = useState<FederatedResult | null>(null);
  const [federatedError, setFederatedError] = useState<string | null>(null);
  const [animatingSource, setAnimatingSource] = useState<number>(-1);
  const [showDecomposition, setShowDecomposition] = useState(true);
  const [executingWorkflowStep, setExecutingWorkflowStep] = useState<string | null>(null);
  const [completedWorkflowSteps, setCompletedWorkflowSteps] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"federated" | "intent" | "scenarios">("federated");

  useEffect(() => {
    const scenarios = industryScenarios[selectedIndustry];
    if (scenarios && scenarios.length > 0) {
      setActiveScenario(scenarios[0]);
    }
  }, [selectedIndustry]);

  const handleLiveSearch = async () => {
    if (!liveQuery.trim() || liveQuery.length < 3) return;
    
    setIsAnalyzing(true);
    try {
      const response = await fetch('/api/search/diagnose-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: liveQuery,
          industry: selectedIndustry,
          context: { currentPage: "Search Pattern Demo" }
        })
      });
      
      if (response.ok) {
        const diagnosis = await response.json();
        setLiveDiagnosis(diagnosis);
      }
    } catch (error) {
      console.error("Error diagnosing intent:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if (liveQuery.length >= 3) {
        handleLiveSearch();
      } else {
        setLiveDiagnosis(null);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [liveQuery, selectedIndustry]);

  const handleExecuteAction = (actionTitle: string) => {
    setExecutingAction(actionTitle);
    setTimeout(() => {
      setExecutedActions(prev => [...prev, actionTitle]);
      setExecutingAction(null);
    }, 1500);
  };

  const handleFederatedSearch = async () => {
    if (!federatedQuery.trim() || federatedQuery.length < 5) return;

    setIsFederating(true);
    setFederatedResult(null);
    setFederatedError(null);
    setAnimatingSource(-1);
    setCompletedWorkflowSteps([]);
    setShowDecomposition(true);

    try {
      const response = await fetch('/api/search/federated', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: federatedQuery,
          industry: selectedIndustry,
          userRole: "Senior Manager"
        })
      });

      if (!response.ok) throw new Error("Failed to execute federated search");

      const result: FederatedResult = await response.json();
      setFederatedResult(result);

      for (let i = 0; i < (result.sources?.length || 0); i++) {
        await new Promise(r => setTimeout(r, 300));
        setAnimatingSource(i);
      }
    } catch (err: any) {
      setFederatedError(err.message || "Failed to search across systems");
    } finally {
      setIsFederating(false);
    }
  };

  const handleExecuteWorkflowStep = (stepId: string) => {
    setExecutingWorkflowStep(stepId);
    setTimeout(() => {
      setCompletedWorkflowSteps(prev => [...prev, stepId]);
      setExecutingWorkflowStep(null);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-blue-500/30 overflow-hidden">
      
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-500/10 rounded-full blur-[120px] animate-pulse" style={{ animationDuration: '8s' }} />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-500/10 rounded-full blur-[120px] animate-pulse" style={{ animationDuration: '10s' }} />
      </div>

      <header className="h-20 border-b border-white/10 bg-card/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto h-full flex items-center justify-between px-6">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => setLocation("/")} className="text-white/50 hover:text-white transition-colors" data-testid="button-back">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <div className="h-6 w-px bg-white/20" />
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <Search className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="font-display font-bold text-lg text-white tracking-tight">Predictive Search</h1>
                  <p className="text-sm text-white/50">Federated Intent-to-Action Engine</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-pink-500 to-purple-600 rounded-full text-xs font-semibold text-white border-0">
                <Sparkles className="w-3 h-3" />
                Experience Pattern
              </span>
            </div>
        </div>
      </header>

      <main className="flex-1 p-8 relative z-10">
         <div className="max-w-7xl mx-auto space-y-12">

            {/* Value Proposition Banner */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-blue-900/40 via-purple-900/30 to-blue-900/40 border border-blue-500/20 rounded-2xl p-8"
            >
              <div className="flex items-start gap-6">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <Network className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-display font-bold text-white mb-2" data-testid="text-hero-title">
                    Not Search. Cross-System Intelligence.
                  </h2>
                  <p className="text-white/60 max-w-3xl leading-relaxed" data-testid="text-hero-description">
                    Platform search finds documents in <span className="text-white font-medium">one system</span>. 
                    This pattern searches across <span className="text-blue-300 font-medium">CRM, Knowledge Base, Analytics, Support, and Calendar simultaneously</span>, 
                    finds connections between data sources that no single platform can see, and generates 
                    <span className="text-purple-300 font-medium"> executable multi-step workflows</span> — not just links.
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Industry Selector */}
            <div className="flex gap-4 overflow-x-auto pb-2">
              {industries.map((industry) => {
                const Icon = industry.icon;
                const isActive = selectedIndustry === industry.id;
                return (
                  <button
                    key={industry.id}
                    onClick={() => { setSelectedIndustry(industry.id); setFederatedResult(null); }}
                    className={cn(
                      "flex items-center gap-3 px-6 py-3 rounded-xl border transition-all whitespace-nowrap",
                      isActive 
                        ? `bg-gradient-to-r ${industry.color} border-white/20 text-white shadow-lg`
                        : "bg-white/5 border-white/10 text-white/60 hover:bg-white/10 hover:border-white/20"
                    )}
                    data-testid={`button-industry-${industry.id.toLowerCase()}`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-bold">{industry.name}</span>
                  </button>
                );
              })}
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-2 border-b border-white/10 pb-0">
              {[
                { id: "federated" as const, label: "Federated Command Center", icon: Network },
                { id: "intent" as const, label: "Live Intent Diagnosis", icon: Brain },
                { id: "scenarios" as const, label: "Industry Scenarios", icon: Layers }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "flex items-center gap-2 px-5 py-3 text-sm font-medium transition-all border-b-2 -mb-px",
                    activeTab === tab.id
                      ? "text-white border-blue-400"
                      : "text-white/40 border-transparent hover:text-white/60"
                  )}
                  data-testid={`tab-${tab.id}`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Federated Command Center - THE DIFFERENTIATOR */}
            {activeTab === "federated" && (
              <section className="space-y-8">
                <div>
                  <h2 className="text-2xl font-display font-bold text-white mb-2 flex items-center gap-2">
                    <Network className="w-6 h-6 text-blue-400" /> Federated Command Center
                  </h2>
                  <p className="text-white/60 max-w-2xl">
                    Ask a complex business question. Watch the AI decompose it, search across enterprise systems simultaneously, and propose an executable workflow.
                  </p>
                </div>

                {/* Query Input */}
                <div className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-2xl p-6">
                  <div className="relative mb-4">
                    <Network className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-blue-400" />
                    <input
                      type="text"
                      value={federatedQuery}
                      onChange={(e) => setFederatedQuery(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleFederatedSearch()}
                      placeholder="Ask a cross-system question..."
                      className="w-full bg-black/40 border border-white/20 rounded-xl h-14 pl-12 pr-32 text-white placeholder:text-white/30 focus:border-blue-400 focus:outline-none transition-all text-lg"
                      data-testid="input-federated-query"
                    />
                    <Button
                      onClick={handleFederatedSearch}
                      disabled={isFederating || federatedQuery.length < 5}
                      className="absolute right-2 top-1/2 -translate-y-1/2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold px-6"
                      data-testid="button-federated-search"
                    >
                      {isFederating ? (
                        <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" /> Searching...</>
                      ) : (
                        <><Zap className="w-4 h-4 mr-2" /> Search All</>
                      )}
                    </Button>
                  </div>

                  {/* Example Queries */}
                  <div className="flex flex-wrap gap-2">
                    <span className="text-xs text-white/30 py-1">Try:</span>
                    {exampleQueries[selectedIndustry].map((q, i) => (
                      <button
                        key={i}
                        onClick={() => { setFederatedQuery(q); }}
                        className="text-xs px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-white/50 hover:text-white hover:bg-white/10 transition-all truncate max-w-xs"
                        data-testid={`button-example-query-${i}`}
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Federated Results */}
                <AnimatePresence mode="wait">
                  {federatedError && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3"
                      data-testid="status-federated-error"
                    >
                      <AlertTriangle className="w-5 h-5 text-red-400" />
                      <p className="text-red-300 text-sm">{federatedError}</p>
                    </motion.div>
                  )}

                  {federatedResult && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-8"
                    >
                      {/* Executive Summary */}
                      <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/20 rounded-2xl p-6" data-testid="card-executive-summary">
                        <div className="flex items-center gap-2 text-blue-300 mb-3 font-bold text-xs uppercase tracking-wider">
                          <Sparkles className="w-4 h-4" /> Executive Summary
                        </div>
                        <p className="text-white/90 leading-relaxed">{federatedResult.executiveSummary}</p>
                        <div className="mt-4 flex items-center gap-4">
                          <div className={cn(
                            "px-3 py-1 rounded-full text-xs font-bold",
                            federatedResult.autonomyAssessment?.level === "Agentic" ? "bg-purple-500/20 text-purple-300" :
                            federatedResult.autonomyAssessment?.level === "Collaborative" ? "bg-blue-500/20 text-blue-300" :
                            "bg-green-500/20 text-green-300"
                          )}>
                            {federatedResult.autonomyAssessment?.level} Mode
                          </div>
                          <span className="text-xs text-white/40">{federatedResult.sources?.length || 0} sources queried</span>
                          <span className="text-xs text-white/40">{federatedResult.crossSystemConnections?.length || 0} cross-system connections found</span>
                        </div>
                      </div>

                      {/* Query Decomposition */}
                      {federatedResult.queryDecomposition && (
                        <div className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-2xl p-6" data-testid="card-decomposition">
                          <button
                            onClick={() => setShowDecomposition(!showDecomposition)}
                            className="flex items-center justify-between w-full mb-4"
                          >
                            <div className="flex items-center gap-2 text-white font-bold">
                              <GitBranch className="w-5 h-5 text-purple-400" /> Query Decomposition
                              <span className="text-xs text-white/40 font-normal ml-2">
                                {federatedResult.queryDecomposition.subTasks?.length || 0} sub-tasks
                              </span>
                            </div>
                            <ChevronRight className={cn("w-4 h-4 text-white/40 transition-transform", showDecomposition && "rotate-90")} />
                          </button>
                          <AnimatePresence>
                            {showDecomposition && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: "auto", opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="space-y-3 overflow-hidden"
                              >
                                {federatedResult.queryDecomposition.subTasks?.map((task, i) => (
                                  <motion.div
                                    key={task.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    className="flex items-start gap-3 p-3 bg-white/5 border border-white/10 rounded-xl"
                                  >
                                    <div className="w-6 h-6 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                                      <CheckCircle2 className="w-3.5 h-3.5 text-purple-300" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <p className="text-sm text-white font-medium">{task.description}</p>
                                      <p className="text-xs text-white/40 mt-1">{task.reasoning}</p>
                                    </div>
                                    <span className="text-[10px] px-2 py-1 bg-purple-500/10 text-purple-300 rounded-full whitespace-nowrap border border-purple-500/20">
                                      {task.targetSource}
                                    </span>
                                  </motion.div>
                                ))}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      )}

                      {/* Federated Sources Grid */}
                      <div data-testid="card-sources">
                        <div className="flex items-center gap-2 text-white font-bold mb-4">
                          <Database className="w-5 h-5 text-emerald-400" /> Federated Sources
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {federatedResult.sources?.map((source, i) => {
                            const Icon = sourceIcons[source.type] || Database;
                            const colorClass = sourceColors[source.type] || "from-gray-500 to-gray-600";
                            const isVisible = i <= animatingSource;

                            return (
                              <motion.div
                                key={source.id}
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: isVisible ? 1 : 0.3, scale: isVisible ? 1 : 0.95 }}
                                transition={{ delay: i * 0.15 }}
                                className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden"
                              >
                                <div className="p-4 border-b border-white/5 flex items-center justify-between">
                                  <div className="flex items-center gap-3">
                                    <div className={cn("w-8 h-8 rounded-lg bg-gradient-to-br flex items-center justify-center", colorClass)}>
                                      <Icon className="w-4 h-4 text-white" />
                                    </div>
                                    <div>
                                      <h4 className="text-sm font-bold text-white">{source.name}</h4>
                                      <p className="text-[10px] text-white/40">{source.resultCount} results in {source.latencyMs}ms</p>
                                    </div>
                                  </div>
                                  {isVisible && (
                                    <div className="w-2 h-2 rounded-full bg-emerald-400" />
                                  )}
                                </div>
                                <div className="p-3 space-y-2 max-h-48 overflow-y-auto">
                                  {source.results?.map((result, j) => (
                                    <div key={j} className="p-2.5 bg-white/5 rounded-lg hover:bg-white/10 transition-all group">
                                      <div className="flex items-start justify-between gap-2">
                                        <div className="min-w-0">
                                          <p className="text-xs font-medium text-white truncate">{result.title}</p>
                                          <p className="text-[10px] text-white/40 mt-0.5 line-clamp-2">{result.snippet}</p>
                                        </div>
                                        <div className="flex items-center gap-2 flex-shrink-0">
                                          <span className="text-[10px] text-emerald-400 font-mono">{Math.round(result.relevance * 100)}%</span>
                                          {result.actionable && (
                                            <button className="text-[10px] px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded font-medium opacity-0 group-hover:opacity-100 transition-opacity" data-testid={`button-action-${source.id}-${j}`}>
                                              {result.actionLabel || "Open"}
                                            </button>
                                          )}
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </motion.div>
                            );
                          })}
                        </div>
                      </div>

                      {/* Cross-System Connections - THE KEY DIFFERENTIATOR */}
                      {federatedResult.crossSystemConnections && federatedResult.crossSystemConnections.length > 0 && (
                        <div className="bg-gradient-to-br from-indigo-900/30 to-purple-900/20 border border-indigo-500/20 rounded-2xl p-6" data-testid="card-cross-system">
                          <div className="flex items-center gap-2 text-indigo-300 mb-4 font-bold text-xs uppercase tracking-wider">
                            <Network className="w-4 h-4" /> Cross-System Connections
                            <span className="ml-2 px-2 py-0.5 bg-indigo-500/20 rounded-full text-[10px]">Only possible with federated search</span>
                          </div>
                          <div className="space-y-4">
                            {federatedResult.crossSystemConnections.map((connection, i) => (
                              <motion.div
                                key={i}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.3 + i * 0.15 }}
                                className="flex items-start gap-4 p-4 bg-white/5 border border-indigo-500/10 rounded-xl"
                              >
                                <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
                                  <Sparkles className="w-5 h-5 text-indigo-300" />
                                </div>
                                <div className="flex-1">
                                  <p className="text-sm text-white/90 leading-relaxed">{connection.insight}</p>
                                  <div className="flex items-center gap-3 mt-2">
                                    <div className="flex gap-1.5">
                                      {connection.sources?.map((src, j) => (
                                        <span key={j} className="text-[10px] px-2 py-0.5 bg-indigo-500/10 text-indigo-300 rounded-full border border-indigo-500/20">{src}</span>
                                      ))}
                                    </div>
                                    <span className="text-[10px] text-emerald-400 font-mono">{Math.round(connection.confidence * 100)}% confidence</span>
                                  </div>
                                </div>
                              </motion.div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Synthesized Insight */}
                      {federatedResult.synthesizedInsight && (
                        <div className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-2xl p-6" data-testid="card-synthesis">
                          <div className="flex items-center gap-2 text-amber-300 mb-3 font-bold text-xs uppercase tracking-wider">
                            <Brain className="w-4 h-4" /> AI Synthesis
                          </div>
                          <p className="text-white/80 leading-relaxed">{federatedResult.synthesizedInsight}</p>
                        </div>
                      )}

                      {/* Executable Workflow */}
                      {federatedResult.suggestedWorkflow && federatedResult.suggestedWorkflow.length > 0 && (
                        <div className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-2xl p-6" data-testid="card-workflow">
                          <div className="flex items-center gap-2 text-emerald-300 mb-4 font-bold text-xs uppercase tracking-wider">
                            <Play className="w-4 h-4" /> Suggested Workflow
                            <span className="ml-2 text-white/30 font-normal normal-case">Click to execute each step</span>
                          </div>
                          <div className="space-y-3">
                            {federatedResult.suggestedWorkflow.map((step, i) => {
                              const isComplete = completedWorkflowSteps.includes(step.id);
                              const isExecuting = executingWorkflowStep === step.id;
                              const canExecute = step.dependencies?.every(d => completedWorkflowSteps.includes(d)) ?? true;

                              return (
                                <motion.div
                                  key={step.id}
                                  initial={{ opacity: 0, y: 10 }}
                                  animate={{ opacity: 1, y: 0 }}
                                  transition={{ delay: 0.2 + i * 0.1 }}
                                  className={cn(
                                    "flex items-center gap-4 p-4 rounded-xl border transition-all",
                                    isComplete ? "bg-emerald-500/10 border-emerald-500/20" :
                                    isExecuting ? "bg-blue-500/10 border-blue-500/20" :
                                    canExecute ? "bg-white/5 border-white/10 hover:border-white/20" :
                                    "bg-white/5 border-white/5 opacity-50"
                                  )}
                                >
                                  <div className={cn(
                                    "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold",
                                    isComplete ? "bg-emerald-500 text-white" :
                                    isExecuting ? "bg-blue-500 text-white" :
                                    "bg-white/10 text-white/60"
                                  )}>
                                    {isComplete ? <CheckCircle2 className="w-4 h-4" /> : 
                                     isExecuting ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> :
                                     i + 1}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                      <p className="text-sm font-medium text-white">{step.action}</p>
                                      <span className="text-[10px] px-2 py-0.5 bg-white/10 text-white/50 rounded">{step.system}</span>
                                    </div>
                                    <p className="text-xs text-white/40 mt-0.5">{step.description}</p>
                                  </div>
                                  <div className="flex items-center gap-3 flex-shrink-0">
                                    <span className="text-[10px] text-white/30 flex items-center gap-1">
                                      <Clock className="w-3 h-3" /> {step.estimatedTime}
                                    </span>
                                    {step.requiresApproval && (
                                      <span className="text-[10px] px-2 py-0.5 bg-amber-500/10 text-amber-300 rounded border border-amber-500/20">Approval</span>
                                    )}
                                    {!isComplete && canExecute && (
                                      <Button
                                        size="sm"
                                        onClick={() => handleExecuteWorkflowStep(step.id)}
                                        disabled={isExecuting}
                                        className="h-7 text-xs bg-blue-500 hover:bg-blue-600"
                                        data-testid={`button-execute-step-${step.id}`}
                                      >
                                        {isExecuting ? "Running..." : "Execute"}
                                      </Button>
                                    )}
                                  </div>
                                </motion.div>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Autonomy Assessment */}
                      {federatedResult.autonomyAssessment && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-slate-900/60 border border-white/10 rounded-xl p-5">
                            <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3 flex items-center gap-2">
                              <Shield className="w-3 h-3" /> Autonomy Assessment
                            </h4>
                            <p className="text-sm text-white/70 leading-relaxed">{federatedResult.autonomyAssessment.reasoning}</p>
                          </div>
                          <div className="bg-slate-900/60 border border-white/10 rounded-xl p-5">
                            <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3 flex items-center gap-2">
                              <Eye className="w-3 h-3" /> Human Checkpoints
                            </h4>
                            <div className="space-y-2">
                              {federatedResult.autonomyAssessment.humanCheckpoints?.map((cp, i) => (
                                <div key={i} className="flex items-start gap-2 text-sm text-white/70">
                                  <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                                  {cp}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>

                {!federatedResult && !isFederating && (
                  <div className="text-center py-16">
                    <Network className="w-16 h-16 text-white/10 mx-auto mb-4" />
                    <p className="text-white/30 text-lg">Enter a complex business question to see cross-system intelligence in action</p>
                    <p className="text-white/20 text-sm mt-2">The AI will decompose your query, search across 4-6 enterprise systems, and propose an executable workflow</p>
                  </div>
                )}
              </section>
            )}

            {/* Live AI Intent Diagnosis */}
            {activeTab === "intent" && (
              <section>
                <div className="mb-6">
                  <h2 className="text-2xl font-display font-bold text-white mb-2 flex items-center gap-2">
                    <Zap className="w-6 h-6 text-yellow-400" /> Live AI Intent Diagnosis
                  </h2>
                  <p className="text-white/60 max-w-2xl">
                    Type your own query and watch real AI analyze your intent in real-time
                  </p>
                </div>

                <div className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-3xl p-8">
                  <div className="relative mb-6">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                    <input
                      type="text"
                      value={liveQuery}
                      onChange={(e) => setLiveQuery(e.target.value)}
                      placeholder={`Try: "show me" or "find the" or "why is"...`}
                      className="w-full bg-black/40 border border-white/20 rounded-xl h-14 pl-12 pr-4 text-white placeholder:text-white/30 focus:border-blue-400 focus:outline-none transition-all"
                      data-testid="input-live-search"
                    />
                    {isAnalyzing && (
                      <div className="absolute right-4 top-1/2 -translate-y-1/2">
                        <div className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                      </div>
                    )}
                  </div>

                  <AnimatePresence mode="wait">
                    {liveDiagnosis && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
                      >
                        <div className="space-y-4">
                          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                            <h4 className="text-xs text-white/40 uppercase tracking-wider mb-2">Predicted Completion</h4>
                            <p className="text-lg text-white font-mono">
                              {liveQuery}<span className="text-blue-400">{liveDiagnosis.predictedCompletion}</span>
                            </p>
                          </div>

                          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                            <div className="flex items-center justify-between mb-3">
                              <h4 className="text-xs text-white/40 uppercase tracking-wider">Detected Intent</h4>
                              <span className="text-blue-400 font-bold">{(liveDiagnosis.confidence * 100).toFixed(0)}% confidence</span>
                            </div>
                            <p className="text-xl font-bold text-white">{liveDiagnosis.intent}</p>
                          </div>

                          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                            <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3">Suggested Actions</h4>
                            <div className="space-y-2">
                              {liveDiagnosis.suggestedActions?.map((action: any, idx: number) => (
                                <div key={idx} className="flex items-center justify-between p-3 bg-black/30 rounded-lg">
                                  <div>
                                    <p className="font-medium text-white">{action.title}</p>
                                    <p className="text-xs text-white/50">{action.description}</p>
                                  </div>
                                  {action.canExecute && (
                                    <button 
                                      onClick={() => handleExecuteAction(action.title)}
                                      disabled={executingAction === action.title || executedActions.includes(action.title)}
                                      className={cn(
                                        "px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2",
                                        executedActions.includes(action.title)
                                          ? "bg-emerald-500/20 text-emerald-400"
                                          : "bg-blue-500 hover:bg-blue-600 text-white"
                                      )}
                                      data-testid={`button-execute-${idx}`}
                                    >
                                      {executedActions.includes(action.title) ? (
                                        <><CheckCircle2 className="w-4 h-4" /> Done</>
                                      ) : executingAction === action.title ? (
                                        <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Executing...</>
                                      ) : (
                                        <><Play className="w-4 h-4" /> Execute</>
                                      )}
                                    </button>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div className="space-y-4">
                          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                            <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3">Diagnosis Steps</h4>
                            <div className="space-y-2">
                              {liveDiagnosis.diagnosisSteps?.map((step: any, idx: number) => (
                                <div key={idx} className={cn(
                                  "p-2 rounded-lg text-xs font-mono border",
                                  step.status === "match" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-300" :
                                  step.status === "inference" ? "bg-purple-500/10 border-purple-500/20 text-purple-300" :
                                  "bg-blue-500/10 border-blue-500/20 text-blue-300"
                                )}>
                                  {step.step}
                                </div>
                              ))}
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                              <h4 className="text-xs text-white/40 uppercase tracking-wider mb-2">Context Used</h4>
                              <div className="flex flex-wrap gap-1">
                                {liveDiagnosis.contextUsed?.map((ctx: string, idx: number) => (
                                  <span key={idx} className="text-[10px] px-2 py-1 bg-blue-500/10 text-blue-300 rounded-full">{ctx}</span>
                                ))}
                              </div>
                            </div>
                            <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                              <h4 className="text-xs text-white/40 uppercase tracking-wider mb-2">Memory Accessed</h4>
                              <div className="flex flex-wrap gap-1">
                                {liveDiagnosis.memoryAccessed?.map((mem: string, idx: number) => (
                                  <span key={idx} className="text-[10px] px-2 py-1 bg-purple-500/10 text-purple-300 rounded-full">{mem}</span>
                                ))}
                              </div>
                            </div>
                          </div>

                          <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-xl p-4">
                            <div className="flex items-center justify-between">
                              <h4 className="text-xs text-white/40 uppercase tracking-wider">Autonomy Level</h4>
                              <span className={cn(
                                "px-3 py-1 rounded-full text-sm font-bold",
                                liveDiagnosis.autonomyLevel === "Agentic" ? "bg-purple-500/20 text-purple-300" :
                                liveDiagnosis.autonomyLevel === "Collaborative" ? "bg-blue-500/20 text-blue-300" :
                                "bg-green-500/20 text-green-300"
                              )}>
                                {liveDiagnosis.autonomyLevel}
                              </span>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {!liveDiagnosis && liveQuery.length < 3 && (
                      <div className="text-center py-12">
                        <Brain className="w-12 h-12 text-white/20 mx-auto mb-4" />
                        <p className="text-white/40">Type at least 3 characters to see live AI intent diagnosis</p>
                      </div>
                    )}
                  </AnimatePresence>
                </div>
              </section>
            )}

            {/* Industry Scenarios */}
            {activeTab === "scenarios" && (
              <section className="space-y-8">
                <div>
                  <h2 className="text-2xl font-display font-bold text-white mb-2 flex items-center gap-2">
                    <Layers className="w-6 h-6 text-blue-400" /> Industry Scenarios
                  </h2>
                  <p className="text-white/60 max-w-2xl">
                    See how predictive search adapts to different industry contexts with pre-built scenarios
                  </p>
                </div>

                <div className="flex gap-4 mb-6 overflow-x-auto pb-2 scrollbar-hide">
                  {industryScenarios[selectedIndustry]?.map((scenario) => (
                    <button
                      key={scenario.id}
                      onClick={() => setActiveScenario(scenario)}
                      className={cn(
                        "px-4 py-2 rounded-full text-sm font-medium transition-all border whitespace-nowrap",
                        activeScenario.id === scenario.id 
                          ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-900/20"
                          : "bg-white/5 border-white/10 text-white/60 hover:bg-white/10 hover:border-white/20"
                      )}
                      data-testid={`button-scenario-${scenario.id}`}
                    >
                      {scenario.intent}
                    </button>
                  ))}
                </div>

                <div className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-3xl p-1 shadow-2xl overflow-hidden">
                  <SearchSimulation scenario={activeScenario} onExecuteAction={handleExecuteAction} executingAction={executingAction} executedActions={executedActions} />
                </div>
              </section>
            )}

            {/* ROI Metrics */}
            <section>
              <div className="mb-6">
                <h2 className="text-2xl font-display font-bold text-white mb-2 flex items-center gap-2">
                  <TrendingUp className="w-6 h-6 text-emerald-400" /> Business Impact
                </h2>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {roiMetrics.map((metric) => (
                  <div key={metric.id} className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all group">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-3xl font-black text-white">{metric.value}</span>
                      <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                        metric.improvement.startsWith('+') ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {metric.improvement}
                      </span>
                    </div>
                    <h3 className="font-bold text-white mb-1">{metric.label}</h3>
                    <p className="text-xs text-white/50">{metric.description}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Guardrails */}
            <section>
              <div className="mb-6">
                <h2 className="text-2xl font-display font-bold text-white mb-2 flex items-center gap-2">
                  <Shield className="w-6 h-6 text-amber-400" /> Enterprise Guardrails & Privacy
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {guardrailControls.map((control) => (
                  <div key={control.id} className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-all">
                    <div className="flex items-start gap-3 mb-3">
                      <div className={cn(
                        "w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0",
                        control.category === "privacy" ? "bg-purple-500/20" :
                        control.category === "security" ? "bg-red-500/20" :
                        control.category === "compliance" ? "bg-blue-500/20" :
                        "bg-amber-500/20"
                      )}>
                        {control.category === "privacy" ? <Eye className="w-5 h-5 text-purple-400" /> :
                         control.category === "security" ? <Lock className="w-5 h-5 text-red-400" /> :
                         control.category === "compliance" ? <Shield className="w-5 h-5 text-blue-400" /> :
                         <AlertTriangle className="w-5 h-5 text-amber-400" />}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <h3 className="font-bold text-white">{control.name}</h3>
                          <span className={cn(
                            "text-[10px] px-2 py-0.5 rounded-full font-medium uppercase",
                            control.status === "enabled" ? "bg-emerald-500/20 text-emerald-400" :
                            control.status === "configurable" ? "bg-blue-500/20 text-blue-400" :
                            "bg-white/10 text-white/50"
                          )}>
                            {control.status}
                          </span>
                        </div>
                        <p className="text-xs text-white/50">{control.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Component Repository */}
            <section>
              <div className="mb-12">
                <h2 className="text-2xl font-display font-bold text-white mb-2 flex items-center gap-2">
                  <Search className="w-6 h-6 text-purple-400" /> Pattern Components
                </h2>
                <p className="text-white/60 max-w-2xl leading-relaxed">
                  A library of search interfaces designed for different levels of AI autonomy and contextual awareness.
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {searchComponents.map((component, idx) => (
                  <motion.div 
                    key={component.id} 
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: idx * 0.1 }}
                    className="flex flex-col gap-4 group"
                  >
                    <div className="border-b border-white/10 pb-2 group-hover:border-white/20 transition-colors">
                      <h3 className="text-lg font-bold text-white group-hover:text-blue-300 transition-colors">{component.name}</h3>
                      <p className="text-xs text-white/50">{component.description}</p>
                    </div>
                    <div className="bg-slate-900/40 border border-white/10 rounded-xl p-4 group-hover:border-white/20 transition-all group-hover:bg-slate-900/60">
                      <SearchComponent spec={component} />
                    </div>
                  </motion.div>
                ))}
              </div>
            </section>

         </div>
      </main>
    </div>
  );
}

```

### AI Service — `ai-predictive-search.ts`

```typescript
import OpenAI from "openai";

const openai = new OpenAI({
  baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL,
  apiKey: process.env.AI_INTEGRATIONS_OPENAI_API_KEY
});

export interface IntentDiagnosis {
  predictedCompletion: string;
  intent: string;
  confidence: number;
  diagnosisSteps: {
    step: string;
    status: "processing" | "match" | "inference";
  }[];
  suggestedActions: {
    title: string;
    description: string;
    actionType: "navigate" | "execute" | "display";
    canExecute: boolean;
  }[];
  contextUsed: string[];
  memoryAccessed: string[];
  autonomyLevel: "Assistive" | "Collaborative" | "Agentic";
}

export interface FederatedSource {
  id: string;
  name: string;
  type: "crm" | "knowledge_base" | "analytics" | "support" | "documents" | "calendar";
  status: "searching" | "complete" | "no_results";
  resultCount: number;
  latencyMs: number;
  results: {
    title: string;
    snippet: string;
    relevance: number;
    metadata: Record<string, string>;
    actionable: boolean;
    actionLabel?: string;
  }[];
}

export interface QueryDecomposition {
  originalQuery: string;
  subTasks: {
    id: string;
    description: string;
    targetSource: string;
    status: "pending" | "executing" | "complete";
    reasoning: string;
  }[];
}

export interface WorkflowStep {
  id: string;
  action: string;
  system: string;
  description: string;
  estimatedTime: string;
  requiresApproval: boolean;
  dependencies: string[];
}

export interface FederatedSearchResult {
  queryDecomposition: QueryDecomposition;
  sources: FederatedSource[];
  synthesizedInsight: string;
  crossSystemConnections: {
    insight: string;
    sources: string[];
    confidence: number;
  }[];
  suggestedWorkflow: WorkflowStep[];
  executiveSummary: string;
  autonomyAssessment: {
    level: "Assistive" | "Collaborative" | "Agentic";
    reasoning: string;
    humanCheckpoints: string[];
  };
}

export async function diagnoseSearchIntent(
  partialQuery: string,
  industry: string,
  userContext?: {
    currentPage?: string;
    recentActions?: string[];
    userRole?: string;
  }
): Promise<IntentDiagnosis> {
  const systemPrompt = `You are an AI intent diagnosis engine for a predictive search system. Your job is to:
1. Predict what the user is trying to search for based on partial input
2. Diagnose their intent using context and memory
3. Suggest actions that can be executed directly

Industry context: ${industry}
${userContext?.currentPage ? `Current page: ${userContext.currentPage}` : ''}
${userContext?.userRole ? `User role: ${userContext.userRole}` : ''}

Respond with JSON matching this exact structure:
{
  "predictedCompletion": "the rest of what user is likely typing",
  "intent": "short intent label (2-4 words)",
  "confidence": 0.85 to 0.99,
  "diagnosisSteps": [
    {"step": "Entity Extraction: what was detected", "status": "match"},
    {"step": "Context Analysis: what context informed this", "status": "inference"},
    {"step": "Memory Recall: any preferences/history used", "status": "match"},
    {"step": "Intent Formulation: final intent determination", "status": "processing"}
  ],
  "suggestedActions": [
    {"title": "Primary Action", "description": "Description of action", "actionType": "execute", "canExecute": true},
    {"title": "Secondary Action", "description": "Alternative option", "actionType": "navigate", "canExecute": true}
  ],
  "contextUsed": ["Context signal 1", "Context signal 2"],
  "memoryAccessed": ["Memory item 1", "Preference recalled"],
  "autonomyLevel": "Collaborative"
}

Make the diagnosis realistic and specific to the industry. Show intelligent reasoning.`;

  const userMessage = `Diagnose intent for partial search query: "${partialQuery}"

Provide a realistic prediction of what the user wants, with detailed reasoning steps.`;

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage }
      ],
      response_format: { type: "json_object" },
      max_tokens: 800,
      temperature: 0.7
    });

    const content = response.choices[0]?.message?.content;
    if (!content) {
      throw new Error("No response from AI");
    }

    const diagnosis = JSON.parse(content) as IntentDiagnosis;
    return diagnosis;
  } catch (error) {
    console.error("Error diagnosing search intent:", error);
    return {
      predictedCompletion: "...",
      intent: "Query Analysis",
      confidence: 0.75,
      diagnosisSteps: [
        { step: "Processing partial input", status: "processing" }
      ],
      suggestedActions: [
        { title: "Search Results", description: "View matching results", actionType: "display", canExecute: false }
      ],
      contextUsed: ["User input"],
      memoryAccessed: [],
      autonomyLevel: "Assistive"
    };
  }
}

export async function federatedSearch(
  query: string,
  industry: string,
  userRole?: string
): Promise<FederatedSearchResult> {
  const systemPrompt = `You are a Federated Intelligence Engine — not a search bar. You receive a natural language business question and you:

1. DECOMPOSE the query into 3-5 sub-tasks that need to be resolved across different enterprise systems
2. SEARCH across 4-6 simulated enterprise data sources (CRM, Knowledge Base, Analytics Platform, Support Tickets, Document Store, Calendar) and return realistic results from each
3. SYNTHESIZE cross-system insights that NO single platform could produce alone — this is the key differentiator
4. GENERATE an executable multi-step workflow with specific actions across systems
5. ASSESS the autonomy level needed and identify human checkpoints

Industry: ${industry}
${userRole ? `User role: ${userRole}` : 'User role: Senior Manager'}

CRITICAL: The value proposition is that platform search finds documents in ONE system. This pattern searches ACROSS systems, finds connections between data sources, and orchestrates actions. Make the cross-system connections the star of the response.

Return JSON:
{
  "queryDecomposition": {
    "originalQuery": "the user's query",
    "subTasks": [
      {"id": "st1", "description": "What this sub-task does", "targetSource": "CRM|Knowledge Base|Analytics|Support|Documents|Calendar", "status": "complete", "reasoning": "Why this sub-task is needed"}
    ]
  },
  "sources": [
    {
      "id": "src1",
      "name": "Source name (e.g., Salesforce CRM)",
      "type": "crm|knowledge_base|analytics|support|documents|calendar",
      "status": "complete",
      "resultCount": 3,
      "latencyMs": 120,
      "results": [
        {"title": "Result title", "snippet": "Brief description of what was found", "relevance": 0.95, "metadata": {"key": "value"}, "actionable": true, "actionLabel": "Open Record"}
      ]
    }
  ],
  "synthesizedInsight": "A paragraph explaining what was discovered by connecting data across all sources — insights that no single system could have provided",
  "crossSystemConnections": [
    {"insight": "Connection found between Source A data and Source B data that reveals X", "sources": ["Source A", "Source B"], "confidence": 0.92}
  ],
  "suggestedWorkflow": [
    {"id": "w1", "action": "Specific action to take", "system": "Which system", "description": "Details", "estimatedTime": "2 min", "requiresApproval": false, "dependencies": []}
  ],
  "executiveSummary": "2-3 sentence executive summary of findings and recommended actions",
  "autonomyAssessment": {
    "level": "Collaborative",
    "reasoning": "Why this level of autonomy",
    "humanCheckpoints": ["Points where human review is recommended"]
  }
}

Make results realistic with specific names, numbers, dates. Each source should have 2-4 results. Generate 2-4 cross-system connections. The workflow should have 3-6 executable steps.`;

  const userMessage = `Federated query: "${query}"

Search across all enterprise systems, find cross-system connections, and propose an executable workflow.`;

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage }
      ],
      response_format: { type: "json_object" },
      max_tokens: 3000,
      temperature: 0.7
    });

    const content = response.choices[0]?.message?.content;
    if (!content) throw new Error("No response from AI");

    return JSON.parse(content) as FederatedSearchResult;
  } catch (error) {
    console.error("Error in federated search:", error);
    throw error;
  }
}

```

---

## Customization Guide

### Rebranding
To adapt this pattern for a different brand, update:
1. **Colors** — Search for hex values (e.g., `#4D148C`, `#FF6600`) and Tailwind color classes
2. **Typography** — Search for `fontFamily` declarations (DM Sans, JetBrains Mono)
3. **Logo** — Replace any logo image imports or SVG references
4. **Copy** — Update section titles, descriptions, and placeholder text

### Adding Sections
Each section is a standalone function component. To add a new section:
1. Create a new function component following the existing pattern
2. Add it to the section navigation array
3. Register it in the section rendering switch/conditional

### AI Integration
The AI service uses OpenAI. To connect:
1. Set `OPENAI_API_KEY` in your environment
2. The service file exports async functions — each takes structured input and returns JSON
3. Routes are simple POST endpoints that validate input and call the service
4. Frontend calls `fetch("/api/...")` to invoke each AI feature

