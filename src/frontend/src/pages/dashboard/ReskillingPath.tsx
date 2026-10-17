/**
 * Reskilling Paths page: shows the stored plan and lets the user (re)generate it.
 * Generation calls Gemini and can take up to about two minutes.
 */
import { useEffect, useState } from 'react';
import { Check, Circle } from 'lucide-react';
import { generateReskilling, getReskilling } from '../../services/api';
import type { RecommendationType, ReskillingPlan } from '../../services/workerTypes';
import { safeHttpUrl } from '../../utils/workerData';

const typeClasses: Record<RecommendationType, string> = {
  upskilling: 'bg-green-900/20 text-green-400 border-green-500/20',
  reskilling: 'bg-purple-900/20 text-purple-400 border-purple-500/20',
};

export default function ReskillingPath() {
  const [plan, setPlan] = useState<ReskillingPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getReskilling()
      .then((p) => {
        if (!cancelled && p.recommendationType !== null) setPlan(p);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Could not load the plan');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const generate = async () => {
    setPending(true);
    setError(null);
    try {
      const p = await generateReskilling();
      if (p.error) setError(p.error);
      if (p.recommendationType !== null) setPlan(p);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed');
    } finally {
      setPending(false);
    }
  };

  const hasPlan = plan !== null && plan.recommendationType !== null;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold">Reskilling Paths</h1>
        <button type="button" className="btn-primary" onClick={generate} disabled={pending || loading}>
          {pending ? 'Generating...' : hasPlan ? 'Regenerate Path' : 'Generate Path'}
        </button>
      </div>

      {pending && <p className="text-textSecondary">This can take up to two minutes. Please keep this page open.</p>}

      {error && (
        <div role="alert" className="p-4 bg-red-900/20 text-red-400 border border-red-500/20 rounded">
          {error}
        </div>
      )}

      {loading && <p className="text-textSecondary">Loading...</p>}

      {!loading && !hasPlan && !pending && (
        <div className="card">
          <p className="text-textSecondary">
            No plan yet. Fill in the Worker Analysis page first, then generate your path.
          </p>
        </div>
      )}

      {plan && plan.recommendationType !== null && (
        <>
          <div className="card space-y-3">
            <span className={`inline-block text-xs px-2 py-1 rounded border capitalize ${typeClasses[plan.recommendationType]}`}>
              {plan.recommendationType}
            </span>
            <p>{plan.summary}</p>
          </div>

          <div className="card">
            <h2 className="text-lg font-bold mb-3">Recommended Skills</h2>
            {plan.recommendedSkills.length === 0 ? (
              <p className="text-textSecondary">None.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {plan.recommendedSkills.map((s, i) => (
                  <div key={i} className="p-3 bg-white/5 rounded">
                    <span className="inline-block px-2 py-1 mb-1 text-sm rounded bg-blue-900/30 text-blue-300">{s.skill}</span>
                    <p className="text-sm text-textSecondary">{s.reason}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <h2 className="text-lg font-bold mb-3">Learning Timeline</h2>
            {plan.learningPath.length === 0 ? (
              <p className="text-textSecondary">None.</p>
            ) : (
              <ol className="space-y-4 border-l border-gray-700 pl-6">
                {plan.learningPath.map((step, i) => {
                  const last = i === plan.learningPath.length - 1;
                  return (
                    <li key={i} className="relative">
                      <span className="absolute -left-[34px] top-0 w-5 h-5 rounded-full bg-secondary border border-accent flex items-center justify-center">
                        {last ? <Check className="w-3 h-3 text-green-400" aria-label="Final step" /> : <Circle className="w-3 h-3 text-accent" aria-hidden="true" />}
                      </span>
                      {i === 0 && <p className="text-xs uppercase tracking-wide text-accent">Start Here</p>}
                      <p className="text-sm text-textSecondary">{step.week}</p>
                      <p className="font-medium">{step.title}</p>
                      <p className="text-sm text-textSecondary">{step.description}</p>
                    </li>
                  );
                })}
              </ol>
            )}
          </div>

          <div className="card">
            <h2 className="text-lg font-bold mb-3">Recommended Courses</h2>
            {plan.recommendedCourses.length === 0 ? (
              <p className="text-textSecondary">None.</p>
            ) : (
              <div className="space-y-3">
                {plan.recommendedCourses.map((c, i) => {
                  const link = safeHttpUrl(c.url);
                  return (
                    <div key={i} className="p-3 bg-white/5 rounded space-y-2">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-medium">{c.name}</p>
                        {link && (
                          <a href={link} target="_blank" rel="noopener noreferrer" className="text-accent underline shrink-0">
                            Open
                          </a>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-2 text-xs">
                        {c.source !== '' && <span className="px-2 py-1 rounded bg-gray-800">{c.source}</span>}
                        {c.duration !== '' && <span className="px-2 py-1 rounded bg-gray-800">{c.duration}</span>}
                        {c.matchedSkills.map((m, j) => (
                          <span key={j} className="px-2 py-1 rounded bg-blue-900/30 text-blue-300">{m}</span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="card">
            <h2 className="text-lg font-bold mb-3">Recommended Jobs</h2>
            {plan.recommendedJobs.length === 0 ? (
              <p className="text-textSecondary">None.</p>
            ) : (
              <div className="space-y-3">
                {plan.recommendedJobs.map((j, i) => (
                  <div key={i} className="p-3 bg-white/5 rounded space-y-2">
                    <p className="font-medium">{j.title}</p>
                    <p className="text-sm text-textSecondary">{[j.company, j.location].filter((x) => x !== '').join(' - ')}</p>
                    {j.matchReason !== '' && <p className="text-sm">{j.matchReason}</p>}
                    <div className="flex flex-wrap gap-2 text-xs">
                      {j.requiredSkills.map((s, k) => (
                        <span key={k} className="px-2 py-1 rounded bg-blue-900/30 text-blue-300">{s}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
