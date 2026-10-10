import { useState, useCallback } from 'react';
import { useAsyncData } from '../../hooks/useAsyncData';
import { getDashboardStats, getHiringTrends, getSkillTrendYears, getSkillTrends } from '../../services/api';
import { formatName, formatCityName, formatCount, topSkillsFromTrends, hiringSeries } from '../../utils/dashboardData';
import StatCard from '../../components/StatCard';
import ChartCard from '../../components/ChartCard';
import DataState from '../../components/DataState';
import AxisTick from '../../components/AxisTick';
import LatestJobs from '../../components/dashboard/LatestJobs';
import DynamicInsights from '../../components/dashboard/DynamicInsights';
import { ResponsiveContainer, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

function TopSkillsChart({ effectiveYear, refreshTrigger }: { effectiveYear: number | "all", refreshTrigger: number }) {
  const fetchTrends = useCallback(() => {
    const yearNum = effectiveYear !== "all" ? effectiveYear : undefined;
    return getSkillTrends(yearNum);
  }, [effectiveYear, refreshTrigger]);

  const { data: trends, loading: trendsLoading, error: trendsError } = useAsyncData(fetchTrends, [effectiveYear, refreshTrigger]);

  return (
    <DataState loading={trendsLoading} error={trendsError}>
      {trends && (
        <div className="h-[250px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topSkillsFromTrends(trends)} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
              <XAxis dataKey="name" stroke="#9CA3AF" tick={<AxisTick />} interval={0} />
              <YAxis stroke="#9CA3AF" label={{ value: 'Growth (second half vs first half)', angle: -90, position: 'insideLeft', fill: '#9CA3AF', dy: 70, dx: -10 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '4px', color: '#F9FAFB' }}
                itemStyle={{ color: '#A855F7' }}
              />
              <Bar dataKey="growth" fill="#A855F7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </DataState>
  );
}

export default function Overview() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  const fetchStats = useCallback(() => getDashboardStats(), [refreshTrigger]);
  const fetchHiring = useCallback(() => getHiringTrends(), [refreshTrigger]);
  const fetchYears = useCallback(() => getSkillTrendYears(), [refreshTrigger]);

  const { data: stats, loading: statsLoading, error: statsError } = useAsyncData(fetchStats, [refreshTrigger]);
  const { data: hiring, loading: hiringLoading, error: hiringError } = useAsyncData(fetchHiring, [refreshTrigger]);
  const { data: years, loading: yearsLoading, error: yearsError } = useAsyncData(fetchYears, [refreshTrigger]);

  const [selectedYear, setSelectedYear] = useState<number | "all" | null>(null);

  const effectiveYear = selectedYear ?? (years && years.length > 0 ? years[0] : "all");

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const isRefreshing = statsLoading || hiringLoading || yearsLoading;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button 
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded transition-colors"
        >
          {isRefreshing ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      <DataState loading={statsLoading} error={statsError}>
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard 
              label="Total Jobs Scraped" 
              value={formatCount(stats.total_jobs)} 
              badge="Active" 
              tone="blue" 
            />
            <StatCard 
              label="Top Hiring City" 
              value={formatCityName(stats.top_city)} 
              badge="Leading" 
              tone="green" 
            />
            <StatCard 
              label="Most In Demand Skill" 
              value={formatName(stats.most_in_demand_skill)} 
              badge="Rising" 
              tone="purple" 
            />
            <StatCard 
              label="Most Common Role" 
              value={formatName(stats.most_common_role)} 
              badge="Popular" 
              tone="amber" 
            />
          </div>
        )}
      </DataState>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Hiring Trends Over Time">
          <DataState loading={hiringLoading} error={hiringError}>
            {hiring && (
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={hiringSeries(hiring)} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                    <XAxis dataKey="name" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '4px', color: '#F9FAFB' }}
                    />
                    <Area type="monotone" dataKey="jobs" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </DataState>
        </ChartCard>

        <ChartCard title="Top Skills Demand">
          <DataState loading={yearsLoading} error={yearsError}>
            {years && (
              <div className="mb-4">
                <label htmlFor="skills-year" className="block text-sm font-medium text-textSecondary mb-1">Skills year</label>
                <select id="skills-year" value={effectiveYear} 
                  onChange={e => setSelectedYear(e.target.value === "all" ? "all" : parseInt(e.target.value, 10))}
                  className="bg-black/50 border border-white/20 rounded px-3 py-2 w-full max-w-xs focus:outline-none focus:border-purple-500"
                >
                  <option value="all">All years</option>
                  {years.map(y => (
                    <option key={y} value={y.toString()}>{y}</option>
                  ))}
                </select>
              </div>
            )}
          </DataState>
          {(years || yearsError) && !yearsLoading && (
            <TopSkillsChart effectiveYear={effectiveYear} refreshTrigger={refreshTrigger} />
          )}
        </ChartCard>
      </div>

      <LatestJobs refreshTrigger={refreshTrigger} />
      <DynamicInsights refreshTrigger={refreshTrigger} />
    </div>
  );
}
