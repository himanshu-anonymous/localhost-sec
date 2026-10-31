import React from 'react';
import { Sparkles, Brain, CheckCircle2, AlertTriangle, ShieldCheck, KeyRound } from 'lucide-react';
import { GemmaAIExplanation } from '../types';

interface AiReasoningViewProps {
  explanation?: GemmaAIExplanation;
}

export const AiReasoningView: React.FC<AiReasoningViewProps> = ({
  explanation = {
    environment_id: 'env_b_adaptive',
    incident_summary: 'Adaptive DDPS actively adjusted defensive priorities, isolating the attacker while preserving core application routes.',
    observed_degradation: 'Minor transient latency observed; system successfully maintained 98.2% availability.',
    defensive_action_explanation: 'DDPS elevated edge traffic filtering to level 2 and enforced segmentation mode 2 to neutralize lateral pivot.',
    policy_outcome: 'Incident contained within 0.0s with zero compromised databases.',
    invariant_status: 'All mandatory security invariants (Omega) fully preserved.',
    potential_weaknesses: ['Slight overhead penalty during initial policy adjustment window'],
    recommendations: ['Tune token decay rate to smoothly relax filters during post-incident recovery'],
    confidence_score: 0.95
  }
}) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Domain C: Gemma 4 AI Cognitive Security Analyst</h2>
          <p className="text-xs text-slate-500 mt-0.5">Out-of-band incident root-cause analysis, policy explanation, and recommendations</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-bold px-3 py-1 bg-slate-100 rounded text-slate-700 flex items-center gap-1.5">
            <KeyRound className="w-3.5 h-3.5 text-[#dc2626]" />
            Multi-Key Rotation Active
          </span>
          <span className="text-xs font-bold px-3 py-1 bg-red-100 text-[#dc2626] rounded flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" />
            Confidence: {(explanation.confidence_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {/* Incident Diagnosis */}
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
              <Brain className="w-4 h-4 text-[#dc2626]" />
              Incident Diagnosis
            </div>
            <p className="text-xs text-slate-700 leading-relaxed font-medium mb-3">
              {explanation.incident_summary}
            </p>
            <div className="p-3 bg-slate-50 rounded border border-slate-100 text-xs text-slate-600">
              <span className="font-bold text-slate-800">Observed Impact: </span>
              {explanation.observed_degradation}
            </div>
          </div>

          {/* Defensive Action Justification */}
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              Defensive Action Justification
            </div>
            <p className="text-xs text-slate-700 leading-relaxed font-medium mb-3">
              {explanation.defensive_action_explanation}
            </p>
            <div className="p-3 bg-emerald-50 rounded border border-emerald-100 text-xs text-emerald-800 font-semibold">
              <span className="font-bold">Resilience Outcome: </span>
              {explanation.policy_outcome}
            </div>
          </div>
        </div>

        {/* Strategic Recommendations & Invariants */}
        <div className="space-y-4">
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
              Strategic Recommendations
            </h3>
            <ul className="space-y-2 text-xs text-slate-600">
              {explanation.recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#dc2626] mt-1.5 shrink-0" />
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
              Security Invariants Status
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              {explanation.invariant_status}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

