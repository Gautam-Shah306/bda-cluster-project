import { truncateLabel } from '../utils/dashboardData';

interface AxisTickProps {
  x?: number;
  y?: number;
  payload?: {
    value: string;
  };
}

export default function AxisTick({ x = 0, y = 0, payload }: AxisTickProps) {
  if (!payload) return null;
  
  return (
    <g transform={`translate(${x},${y})`}>
      <text
        x={0}
        y={0}
        dy={16}
        textAnchor="end"
        fill="#9CA3AF"
        transform="rotate(-90)"
        fontSize={12}
      >
        {truncateLabel(payload.value, 15)}
      </text>
    </g>
  );
}


