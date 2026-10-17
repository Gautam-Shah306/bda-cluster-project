/**
 * Worker Analysis page: the worker describes their job, Gemini returns an
 * automation-risk assessment. The form draft survives reloads (D-027 item 11),
 * and a saved backend profile replaces the draft when one exists (D-033).
 */
import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { analyzeWorker, getWorkerProfile } from '../../services/api';
import type { GeminiAnalysis, RiskLevel } from '../../services/workerTypes';
import { parseSkillsInput, scoreView } from '../../utils/workerData';

const DRAFT_KEY = 'worker_form_draft';

interface FormState {
  title: string;
  city: string;
  experience: string;
  description: string;
  skills: string;
}

const EMPTY_FORM: FormState = { title: '', city: '', experience: '', description: '', skills: '' };

const levelClasses: Record<RiskLevel, string> = {
  high: 'bg-red-900/20 text-red-400 border-red-500/20',
  moderate: 'bg-amber-900/20 text-amber-400 border-amber-500/20',
  low: 'bg-green-900/20 text-green-400 border-green-500/20',
  unknown: 'bg-amber-900/20 text-amber-400 border-amber-500/20',
};

const barClasses: Record<RiskLevel, string> = {
  high: 'bg-red-500',
  moderate: 'bg-amber-500',
  low: 'bg-green-500',
  unknown: 'bg-amber-500',
};

function loadDraft(): FormState {
  try {
    const raw = localStorage.getItem(DRAFT_KEY);
    if (!raw) return EMPTY_FORM;
    const p: unknown = JSON.parse(raw);
    if (typeof p !== 'object' || p === null) return EMPTY_FORM;
    const r = p as Record<string, unknown>;
    const s = (k: string) => (typeof r[k] === 'string' ? (r[k] as string) : '');
    return { title: s('title'), city: s('city'), experience: s('experience'), description: s('description'), skills: s('skills') };
  } catch {
    return EMPTY_FORM;
  }
}

function saveDraft(form: FormState): void {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(form));
  } catch {
    // storage unavailable: the draft is simply not kept
  }
}

export default function WorkerIntelligence() {
  const [form, setForm] = useState<FormState>(loadDraft);
  const [analysis, setAnalysis] = useState<GeminiAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [bannerDismissed, setBannerDismissed] = useState(false);

  useEffect(() => {
    saveDraft(form);
  }, [form]);

  useEffect(() => {
    let cancelled = false;
    getWorkerProfile()
      .then((p) => {
        if (cancelled || p.jobRole === '') return;
        setForm({
          title: p.jobRole,
          city: p.city,
          experience: p.yearsOfExperience === null ? '' : String(p.yearsOfExperience),
          description: p.roleDescription,
          skills: p.skills.join(', '),
        });
        if (p.analysis) setAnalysis(p.analysis);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Could not load your profile');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const update = (key: keyof FormState) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const years = Number(form.experience);
    if (!Number.isFinite(years) || years < 0) {
      setError('Years of experience must be a number that is 0 or more');
      return;
    }
    setError(null);
    setPending(true);
    setBannerDismissed(false);
    try {
      const result = await analyzeWorker({
        job_role: form.title,
        city: form.city,
        years_of_experience: years,
        role_description: form.description,
        skills: parseSkillsInput(form.skills),
      });
      setAnalysis(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setPending(false);
    }
  };

  const view = analysis ? scoreView(analysis.riskScore) : null;
  const showBanner = analysis !== null && analysis.riskScore !== null && analysis.riskScore > 85 && !bannerDismissed;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Worker Analysis</h1>

      {showBanner && (
        <div role="status" className="flex items-start justify-between gap-4 p-4 bg-red-900/30 border border-red-500/40 rounded text-red-200">
          <p>Your role looks highly exposed to automation. The recommendations below can help you plan a move.</p>
          <button type="button" className="underline shrink-0" onClick={() => setBannerDismissed(true)}>
            Dismiss
          </button>
        </div>
      )}

      {error && (
        <div role="alert" className="p-4 bg-red-900/20 text-red-400 border border-red-500/20 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <form onSubmit={submit} className="card space-y-4 lg:col-span-1">
          <div>
            <label htmlFor="w-title" className="block text-sm font-medium mb-1">Current job title</label>
            <input id="w-title" className="input-field" required value={form.title} onChange={update('title')} />
          </div>
          <div>
            <label htmlFor="w-city" className="block text-sm font-medium mb-1">City</label>
            <input id="w-city" className="input-field" required value={form.city} onChange={update('city')} />
          </div>
          <div>
            <label htmlFor="w-exp" className="block text-sm font-medium mb-1">Years of experience</label>
            <input id="w-exp" className="input-field" type="number" min={0} step="any" required value={form.experience} onChange={update('experience')} />
          </div>
          <div>
            <label htmlFor="w-desc" className="block text-sm font-medium mb-1">What you do day to day</label>
            <textarea id="w-desc" className="input-field" rows={4} required value={form.description} onChange={update('description')} />
          </div>
          <div>
            <label htmlFor="w-skills" className="block text-sm font-medium mb-1">Skills (comma separated, optional)</label>
            <input id="w-skills" className="input-field" value={form.skills} onChange={update('skills')} />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={pending}>
            {pending ? 'Analyzing...' : 'Analyze Risk & Opportunities'}
          </button>
        </form>

        <div className="lg:col-span-2 space-y-6">
          {analysis && view && (
            <>
              <div className="card space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold">AI Risk Assessment</h2>
                  <span className={`text-xs px-2 py-1 rounded border capitalize ${levelClasses[analysis.riskLevel]}`}>
                    {analysis.riskLevel}
                  </span>
                </div>
                {view.available ? (
                  <div>
                    <p className="text-3xl font-bold">{view.label}</p>
                    <div className="h-3 bg-gray-800 rounded mt-2" aria-hidden="true">
                      <div
                        data-testid="risk-bar"
                        className={`h-3 rounded ${barClasses[analysis.riskLevel]}`}
                        style={{ width: `${view.percent}%` }}
                      />
                    </div>
                  </div>
                ) : (
                  <p className="text-textSecondary">Score unavailable</p>
                )}
                {analysis.explanation !== '' && <p className="text-textSecondary whitespace-pre-wrap">{analysis.explanation}</p>}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card">
                  <h2 className="text-lg font-bold mb-3">Recommended New Skills</h2>
                  {analysis.newSkills.length === 0 ? (
                    <p className="text-textSecondary">No skills suggested.</p>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {analysis.newSkills.map((s, i) => (
                        <span key={`${s}-${i}`} className="px-2 py-1 text-sm rounded bg-blue-900/30 text-blue-300">{s}</span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="card">
                  <h2 className="text-lg font-bold mb-3">Suggested Pivot Roles</h2>
                  {analysis.pivotRoles.length === 0 ? (
                    <p className="text-textSecondary">No pivot roles suggested.</p>
                  ) : (
                    <ol className="list-decimal pl-5 space-y-1">
                      {analysis.pivotRoles.map((r, i) => (
                        <li key={`${r}-${i}`}>{r}</li>
                      ))}
                    </ol>
                  )}
                </div>
              </div>
            </>
          )}

          <div className="card">
            <h2 className="text-lg font-bold mb-3">Methodology</h2>
            <p className="text-textSecondary text-sm mb-3">
              The assessment weighs how automatable your tasks are, how easily your skills can be replaced, how repetitive the work is and how widely AI tools are already used in it:
            </p>
            <p className="font-mono text-sm">
              (Automation Probability x 0.4) + (Skill Replaceability x 0.3) + (Task Repetition Level x 0.2) + (AI Tool Adoption Rate x 0.1)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
