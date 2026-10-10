import { useAsyncData } from '../../hooks/useAsyncData';
import { getHiringTrends, getTopCities } from '../../services/api';
import { hiringSeries, formatCityName } from '../../utils/dashboardData';
import ChartCard from '../../components/ChartCard';
import DataState from '../../components/DataState';
import AxisTick from '../../components/AxisTick';
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function HiringTrends() {
  const { data: hiring, loading: hiringLoading, error: hiringError } = useAsyncData(getHiringTrends, []);
  const { data: cities, loading: citiesLoading, error: citiesError } = useAsyncData(getTopCities, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Hiring Trends</h1>

      <ChartCard 
        title="Aggregate Job Postings"
        subtitle="Postings (left axis) and Estimated Active Roles (right axis, 0.8 x postings)"
      >
        <DataState loading={hiringLoading} error={hiringError}>
          {hiring && (
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={hiringSeries(hiring)} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis yAxisId="left" stroke="#9CA3AF" />
                  <YAxis yAxisId="right" orientation="right" stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '4px', color: '#F9FAFB' }}
                  />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="jobs" name="Postings" stroke="#3B82F6" activeDot={{ r: 8 }} />
                  <Line yAxisId="right" type="monotone" dataKey="active" name="Estimated Active Roles" stroke="#10B981" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </DataState>
      </ChartCard>

      <ChartCard title="City Demand Comparison">
        <DataState loading={citiesLoading} error={citiesError}>
          {cities && (
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cities} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                  <XAxis dataKey="name" stroke="#9CA3AF" tickFormatter={formatCityName} tick={<AxisTick />} interval={0} />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '4px', color: '#F9FAFB' }}
                    itemStyle={{ color: '#F59E0B' }}
                  />
                  <Bar dataKey="demand" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </DataState>
      </ChartCard>
    </div>
  );
}


