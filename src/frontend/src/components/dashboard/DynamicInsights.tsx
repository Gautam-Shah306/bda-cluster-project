import { useState, useCallback, useEffect } from 'react';
import { useAsyncData } from '../../hooks/useAsyncData';
import { getTopCities, getTopRoles, getRoleDistribution, getCitySpread } from '../../services/api';
import DataState from '../DataState';
import ChartCard from '../ChartCard';
import AxisTick from '../AxisTick';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

interface DynamicInsightsProps {
  refreshTrigger: number;
}

export default function DynamicInsights({ refreshTrigger }: DynamicInsightsProps) {
  const fetchCities = useCallback(() => getTopCities(), [refreshTrigger]);
  const fetchRoles = useCallback(() => getTopRoles(), [refreshTrigger]);
  
  const { data: cities, loading: citiesLoading, error: citiesError } = useAsyncData(fetchCities, [refreshTrigger]);
  const { data: roles, loading: rolesLoading, error: rolesError } = useAsyncData(fetchRoles, [refreshTrigger]);
  
  const [selectedCity, setSelectedCity] = useState<string>('');
  const [selectedRole, setSelectedRole] = useState<string>('');

  useEffect(() => {
    if (cities && cities.length > 0 && !selectedCity) {
      setSelectedCity(cities[0].name);
    }
  }, [cities, selectedCity]);

  useEffect(() => {
    if (roles && roles.length > 0 && !selectedRole) {
      setSelectedRole(roles[0].role);
    }
  }, [roles, selectedRole]);

  const fetchDist = useCallback(() => {
    if (!selectedCity) return Promise.resolve([]);
    return getRoleDistribution(selectedCity);
  }, [selectedCity]);

  const fetchSpread = useCallback(() => {
    if (!selectedRole) return Promise.resolve([]);
    return getCitySpread(selectedRole);
  }, [selectedRole]);

  const { data: distData, loading: distLoading, error: distError } = useAsyncData(fetchDist, [selectedCity, refreshTrigger]);
  const { data: spreadData, loading: spreadLoading, error: spreadError } = useAsyncData(fetchSpread, [selectedRole, refreshTrigger]);

  return (
    <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartCard title="Role Distribution">
        <DataState loading={citiesLoading || distLoading} error={citiesError || distError}>
          <div className="mb-4">
            <label htmlFor="city-select" className="block text-sm font-medium text-textSecondary mb-1">City</label>
            <select id="city-select"               value={selectedCity} 
              onChange={e => setSelectedCity(e.target.value)}
              className="bg-black/50 border border-white/20 rounded px-3 py-2 w-full max-w-xs focus:outline-none focus:border-blue-500"
            >
              {cities?.map(c => (
                <option key={c.name} value={c.name}>{c.name}</option>
              ))}
            </select>
          </div>
          {!distData || distData.length === 0 ? (
            <p className="text-textSecondary text-center py-4">No roles found for this city.</p>
          ) : (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                  <XAxis dataKey="name" stroke="#9CA3AF" tick={<AxisTick />} interval={0} />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '4px', color: '#F9FAFB' }}
                    itemStyle={{ color: '#60A5FA' }}
                  />
                  <Bar dataKey="value" fill="#60A5FA" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </DataState>
      </ChartCard>

      <ChartCard title="City Spread">
        <DataState loading={rolesLoading || spreadLoading} error={rolesError || spreadError}>
          <div className="mb-4">
            <label htmlFor="role-select" className="block text-sm font-medium text-textSecondary mb-1">Role</label>
            <select id="role-select" value={selectedRole} 
              onChange={e => setSelectedRole(e.target.value)}
              className="bg-black/50 border border-white/20 rounded px-3 py-2 w-full max-w-xs focus:outline-none focus:border-blue-500"
            >
              {roles?.map(r => (
                <option key={r.role} value={r.role}>{r.role}</option>
              ))}
            </select>
          </div>
          {!spreadData || spreadData.length === 0 ? (
            <p className="text-textSecondary text-center py-4">No cities found for this role.</p>
          ) : (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={spreadData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                  <XAxis dataKey="name" stroke="#9CA3AF" tick={<AxisTick />} interval={0} />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '4px', color: '#F9FAFB' }}
                    itemStyle={{ color: '#34D399' }}
                  />
                  <Bar dataKey="value" fill="#34D399" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </DataState>
      </ChartCard>
    </div>
  );
}




