
const toneClasses = {
  blue: "bg-blue-900/20 text-blue-400 border-blue-500/20",
  green: "bg-green-900/20 text-green-400 border-green-500/20",
  purple: "bg-purple-900/20 text-purple-400 border-purple-500/20",
  amber: "bg-amber-900/20 text-amber-400 border-amber-500/20"
};

interface StatCardProps {
  label: string;
  value: string;
  badge: string;
  tone: keyof typeof toneClasses;
}

export default function StatCard({ label, value, badge, tone }: StatCardProps) {
  return (
    <div className="card">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-sm font-medium text-textSecondary">{label}</h3>
        <span className={`text-xs px-2 py-1 rounded border ${toneClasses[tone]}`}>
          {badge}
        </span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}


