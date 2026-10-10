import { ReactNode } from 'react';

interface DataStateProps {
  loading: boolean;
  error: string | null;
  children: ReactNode;
}

export default function DataState({ loading, error, children }: DataStateProps) {
  if (loading) {
    return <div className="p-4 text-center text-textSecondary">Loading...</div>;
  }
  if (error) {
    return (
      <div role="alert" className="p-4 bg-red-900/20 text-red-400 border border-red-500/20 rounded">
        {error}
      </div>
    );
  }
  return <>{children}</>;
}



