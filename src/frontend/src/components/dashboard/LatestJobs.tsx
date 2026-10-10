import { useCallback } from 'react';
import { useAsyncData } from '../../hooks/useAsyncData';
import { getLatestJobs } from '../../services/api';
import DataState from '../DataState';
import { formatDate } from '../../utils/dashboardData';

interface LatestJobsProps {
  refreshTrigger: number;
}

export default function LatestJobs({ refreshTrigger }: LatestJobsProps) {
  const fetcher = useCallback(() => getLatestJobs(), [refreshTrigger]);
  const { data, loading, error } = useAsyncData(fetcher, [refreshTrigger]);

  return (
    <div className="card mt-6">
      <h2 className="text-lg font-bold mb-4">Latest Scraped Jobs</h2>
      <DataState loading={loading} error={error}>
        {!data || data.length === 0 ? (
          <p className="text-textSecondary text-center py-4">No scraped jobs available yet</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="py-2 px-4 text-textSecondary font-medium">Job Title</th>
                  <th className="py-2 px-4 text-textSecondary font-medium">Company</th>
                  <th className="py-2 px-4 text-textSecondary font-medium">Location</th>
                  <th className="py-2 px-4 text-textSecondary font-medium">Experience</th>
                  <th className="py-2 px-4 text-textSecondary font-medium">Skills</th>
                  <th className="py-2 px-4 text-textSecondary font-medium">Posted Date</th>
                </tr>
              </thead>
              <tbody>
                {data.map((job, i) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-2 px-4">{job.jobtitle}</td>
                    <td className="py-2 px-4">{job.company}</td>
                    <td className="py-2 px-4">{job.location || 'Unknown'}</td>
                    <td className="py-2 px-4">{job.experience || 'N/A'}</td>
                    <td className="py-2 px-4 max-w-xs truncate" title={job.skills}>{job.skills}</td>
                    <td className="py-2 px-4">{formatDate(job.postdate)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </DataState>
    </div>
  );
}



