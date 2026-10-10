import { SkillTrends, HiringTrendPoint, SkillGapRow } from '../services/dashboardTypes';

export function formatName(s: string): string {
  if (!s) return "";
  const tokens = s.split(" ");
  const uppercaseSet = new Set(["IT", "AI", "ML", "ERP", "QA", "AWS"]);
  
  return tokens.map(token => {
    if (token === "-") return token;
    const upperToken = token.toUpperCase();
    if (uppercaseSet.has(upperToken)) {
      return upperToken;
    }
    if (token.length > 0) {
      return token.charAt(0).toUpperCase() + token.slice(1).toLowerCase();
    }
    return token;
  }).join(" ");
}

export function formatCityName(s: string): string {
  if (!s) return "";
  const part = s.split("/")[0].split(",")[0].trim();
  const lower = part.toLowerCase();
  if (lower === "delhi ncr" || lower === "ncr") {
    return "Delhi NCR";
  }
  if (part.length > 0) {
    return part.charAt(0).toUpperCase() + part.slice(1);
  }
  return part;
}

export function truncateLabel(s: string, max: number = 15): string {
  if (s.length > max) {
    return s.slice(0, max) + "...";
  }
  return s;
}

export function parseGrowth(g: string): number {
  if (g.startsWith("+")) {
    g = g.slice(1);
  }
  const val = parseInt(g, 10);
  return isNaN(val) ? 0 : val;
}

export function topSkillsFromTrends(t: SkillTrends) {
  return t.rising_skills.map(skill => ({
    name: formatName(skill.name),
    growth: parseGrowth(skill.growth)
  }));
}

export function hiringSeries(points: HiringTrendPoint[]) {
  return points.map(pt => ({
    name: pt.month,
    jobs: pt.job_count,
    active: Math.round(pt.job_count * 0.8)
  }));
}

export function gapSeries(rows: SkillGapRow[]) {
  const filtered = rows.filter(r => r.training_supply > 0);
  const mapped = filtered.map(r => ({
    name: formatName(r.skill),
    market_demand: r.market_demand,
    supplyIndex: r.training_supply * 10,
    training_supply: r.training_supply
  }));
  
  // Stable sort by market_demand descending
  mapped.sort((a, b) => b.market_demand - a.market_demand);
  
  return mapped.slice(0, 10);
}

export function regionSeries(regions: Record<string, number>) {
  const entries = Object.entries(regions).map(([name, risk]) => ({ name, risk }));
  entries.sort((a, b) => {
    if (b.risk !== a.risk) {
      return b.risk - a.risk; // Descending
    }
    return a.name.localeCompare(b.name); // Ascending by name
  });
  
  return entries.slice(0, 8);
}

export function riskLevel(score: number): "high" | "medium" | "low" {
  if (score >= 60) return "high";
  if (score >= 30) return "medium";
  return "low";
}

export function formatDate(postdate: string): string {
  if (!postdate) return "";
  return postdate.split(" ")[0];
}

export function formatCount(n: number): string {
  return n.toLocaleString("en-US");
}



