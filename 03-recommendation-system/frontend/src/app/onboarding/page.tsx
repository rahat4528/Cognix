'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Sparkles, Check, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { submitOnboardQuiz } from '@/lib/api';

const AVAILABLE_CATEGORIES = [
  'Audio',
  'Computing',
  'Wearables',
  'Smart Office',
  'Photography',
  'Smart Home'
];

export default function OnboardingQuiz() {
  const [selectedCats, setSelectedCats] = useState<string[]>(['Audio', 'Computing']);
  const [priceTier, setPriceTier] = useState<string>('mid');
  const [techStyle, setTechStyle] = useState<string>('high');
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const toggleCategory = (cat: string) => {
    setSelectedCats((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    );
  };

  const handleSubmit = async () => {
    if (selectedCats.length === 0) {
      alert('Please select at least one preferred category.');
      return;
    }
    setLoading(true);
    try {
      await submitOnboardQuiz(selectedCats, priceTier, techStyle);
      setSubmitted(true);
    } catch (e: any) {
      alert('Submission failed: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Cold-Start Preference Profiling</h2>
        <p className="text-sm text-slate-400 mt-1">
          Zero-history onboarding wizard. Initializes your user preference centroid and eliminates cold-start latency.
        </p>
      </div>

      {!submitted ? (
        <div className="bg-surface border border-surfaceBorder rounded-2xl p-8 space-y-8 shadow-xl">
          {/* Question 1: Categories */}
          <div className="space-y-3">
            <label className="text-sm font-bold text-white flex items-center space-x-2">
              <span className="w-5 h-5 rounded-full bg-primary/20 text-primary text-xs flex items-center justify-center font-bold">1</span>
              <span>What categories interest you most? (Select 1 or more)</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {AVAILABLE_CATEGORIES.map((cat) => {
                const isSelected = selectedCats.includes(cat);
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => toggleCategory(cat)}
                    className={`p-4 rounded-xl border text-left transition flex items-center justify-between ${
                      isSelected
                        ? 'border-primary bg-primary/10 ring-1 ring-primary text-white'
                        : 'border-surfaceBorder bg-slate-900/60 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <span className="text-xs font-semibold">{cat}</span>
                    {isSelected && <Check className="w-4 h-4 text-primary" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Question 2: Price tier */}
          <div className="space-y-3 pt-4 border-t border-surfaceBorder">
            <label className="text-sm font-bold text-white flex items-center space-x-2">
              <span className="w-5 h-5 rounded-full bg-primary/20 text-primary text-xs flex items-center justify-center font-bold">2</span>
              <span>What is your typical budget tier?</span>
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'budget', label: 'Budget Friendly', desc: 'Under $100' },
                { id: 'mid', label: 'Mid-Range Value', desc: '$100 - $400' },
                { id: 'premium', label: 'Flagship Premium', desc: '$400+' }
              ].map((tier) => (
                <button
                  key={tier.id}
                  type="button"
                  onClick={() => setPriceTier(tier.id)}
                  className={`p-3.5 rounded-xl border text-left transition ${
                    priceTier === tier.id
                      ? 'border-primary bg-primary/10 ring-1 ring-primary text-white'
                      : 'border-surfaceBorder bg-slate-900/60 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="text-xs font-semibold">{tier.label}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{tier.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Question 3: Style */}
          <div className="space-y-3 pt-4 border-t border-surfaceBorder">
            <label className="text-sm font-bold text-white flex items-center space-x-2">
              <span className="w-5 h-5 rounded-full bg-primary/20 text-primary text-xs flex items-center justify-center font-bold">3</span>
              <span>Primary Tech Focus</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: 'high', label: 'High Performance & Pro Productivity', desc: 'Engineers, Creators, Audiophiles' },
                { id: 'casual', label: 'Everyday Convenience & Smart Lifestyle', desc: 'Fitness, Smart Home, Travel' }
              ].map((st) => (
                <button
                  key={st.id}
                  type="button"
                  onClick={() => setTechStyle(st.id)}
                  className={`p-3.5 rounded-xl border text-left transition ${
                    techStyle === st.id
                      ? 'border-primary bg-primary/10 ring-1 ring-primary text-white'
                      : 'border-surfaceBorder bg-slate-900/60 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="text-xs font-semibold">{st.label}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{st.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-3 bg-primary hover:bg-primaryHover disabled:opacity-50 text-white rounded-xl text-sm font-bold transition shadow-lg shadow-primary/25"
          >
            {loading ? 'Initializing Cold-Start Preferences...' : 'Initialize Personal Recommendations'}
          </button>
        </div>
      ) : (
        <div className="bg-surface border border-emerald-500/30 rounded-2xl p-8 text-center space-y-4">
          <div className="w-14 h-14 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Cold-Start Profile Ready!</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
              Your preferences have been registered. The hybrid engine has formed your initial centroid profile.
            </p>
          </div>
          <div className="pt-2">
            <Link
              href="/"
              className="inline-flex items-center space-x-1.5 px-6 py-2.5 rounded-xl bg-primary hover:bg-primaryHover text-white text-xs font-bold transition shadow-lg shadow-primary/25"
            >
              <span>Explore Tailored Storefront</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
