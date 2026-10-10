import { useAsyncData } from '../../hooks/useAsyncData';
import { getSkillTrends, getSkillGap } from '../../services/api';
import { formatName, gapSeries } from '../../utils/dashboardData';
import ChartCard from '../../components/ChartCard';
import DataState from '../../components/DataState';
import AxisTick from '../../components/AxisTick';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function SkillsIntelligence() {
  const { data: trends, loading: trendsLoading, error: trendsError } = useAsyncData(() => getSkillTrends(), []);
  const { data: gap, loading: gapLoading, error: gapError } = useAsyncData(() => getSkillGap(), []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Skills Intelligence</h1>

      <DataState loading={trendsLoading} error={trendsError}>
        {trends && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card">
              <h2 className="text-lg font-bold mb-4">Top Rising Skills</h2>
              <div className="space-y-3">
                {trends.rising_skills.slice(0, 5).map((skill, i) => (
                  <div key={i} className="flex justify-between items-center p-3 bg-white/5 rounded">
                    <span className="font-medium">{formatName(skill.name)}</span>
                    <span className="text-sm px-2 py-1 rounded bg-green-900/30 text-green-400">{skill.growth}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <h2 className="text-lg font-bold mb-4">Top Declining Skills</h2>
              <div className="space-y-3">
                {trends.declining_skills.slice(0, 5).map((skill, i) => (
                  <div key={i} className="flex justify-between items-center p-3 bg-white/5 rounded">
                    <span className="font-medium">{formatName(skill.name)}</span>
                    <span className="text-sm px-2 py-1 rounded bg-red-900/30 text-red-400">{skill.decline}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </DataState>

      <ChartCard title="Market Skill Gap Map">
        <DataState loading={gapLoading} error={gapError}>
          {!gap || gap.length === 0 ? (
            <p className="text-textSecondary text-center py-4">No skill gap data available.</p>
          ) : (
            <div className="w-full overflow-x-auto">
              <div className="min-w-[1200px] h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={gapSeries(gap)} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                    <XAxis dataKey="name" stroke="#9CA3AF" tick={<AxisTick />} interval={0} />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '4px', color: '#F9FAFB' }}
                      formatter={(value, name, props) => {
                        if (name === "Training Supply Index") {
                          return [value, `Training Supply Index (Raw supply: ${props.payload.training_supply})`];
                        }
                        return [value, name];
                      }}
                    />
                    <Legend verticalAlign="top" height={36} />
                    <Bar dataKey="market_demand" name="Companies Demand" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="supplyIndex" name="Training Supply Index" fill="#EC4899" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </DataState>
      </ChartCard>
    </div>
  );
}



