export const liveStats = {
  total_jobs: 22979,
  top_city: 'Bengaluru/Bangalore',
  most_in_demand_skill: 'Sales',
  most_common_role: 'Business Development Executive'
};

export const liveHiringTrends = [
  { month: '2026-03', job_count: 10665 },
  { month: '2026-02', job_count: 8500 },
  { month: '2026-01', job_count: 7200 }
];

export const liveSkillTrends = {
  rising_skills: [
    { name: 'Sales', growth: '129800.0%', color: 'green' },
    { name: 'Python', growth: '500.0%', color: 'green' },
    { name: 'React', growth: '200.0%', color: 'green' }
  ],
  declining_skills: [
    { name: 'Customer service', decline: '-100.0%', color: 'red' },
    { name: 'Java', decline: '-50.0%', color: 'red' },
    { name: 'C++', decline: '-20.0%', color: 'red' }
  ]
};

export const liveSkillTrendYears = {
  years: [2026, 2017, 2016, 2015]
};

export const liveSkillGap = [
  { skill: 'Sales', market_demand: 1299, training_supply: 0, gap: 1299 },
  { skill: 'Python', market_demand: 800, training_supply: 200, gap: 600 },
  { skill: 'React', market_demand: 500, training_supply: 100, gap: 400 }
];

export const liveVulnerability = {
  table: [
    { job_role: 'Accountant', city: 'Navi Mumbai', ai_risk_score: 4.0 },
    { job_role: 'Data Entry', city: 'Pune', ai_risk_score: 4.5 },
    { job_role: 'Support', city: 'Bengaluru', ai_risk_score: 3.8 }
  ],
  regions: {
    'Kolkata': 3.90566037735849,
    'Delhi': 3.9038461538461537,
    'Mumbai': 3.5
  }
};

export const liveLatestJobs = [
  {
    jobtitle: 'Hiring Freshers (Only Female)',
    company: 'Radical Technologies',
    location: 'Pune',
    skills: 'Fresher,BCA,BSc,Recruitment,HR,Non IT Recruiter',
    experience: '0 Yrs',
    postdate: '2026-03-07 06:48:45 +0000'
  },
  {
    jobtitle: 'Software Developer',
    company: 'Tech Corp',
    location: 'Bengaluru',
    skills: 'Java,Spring',
    experience: '2 Yrs',
    postdate: '2026-03-06 10:00:00 +0000'
  },
  {
    jobtitle: 'Data Scientist',
    company: 'AI Inc',
    location: 'Remote',
    skills: 'Python,ML',
    experience: '3 Yrs',
    postdate: '2026-03-05 09:00:00 +0000'
  }
];

export const liveTopCities = [
  { name: 'Bengaluru/Bangalore', demand: 5902 },
  { name: 'Mumbai', demand: 3881 },
  { name: 'Bengaluru', demand: 2052 }
];

export const liveTopRoles = [
  { role: 'Business Development Executive', count: 94 },
  { role: 'Business Development Manager', count: 92 },
  { role: 'Software Engineer', count: 81 }
];

export const liveCityRoleDistribution = [
  { city_key: 'mumbai', name: 'GN-Comms & Media -Mobile Private Networks Senior Manager', value: 18, rank: 1 },
  { city_key: 'mumbai', name: 'SAP Consultant (BTP / BW4 / MDG)', value: 18, rank: 2 },
  { city_key: 'mumbai', name: 'Solutions Engineer, Networking Architecture', value: 18, rank: 3 }
];

export const liveRoleCityDistribution = [
  { role_key: 'software engineer', name: 'Bengaluru/Bangalore', value: 40, rank: 1 },
  { role_key: 'software engineer', name: 'Delhi', value: 9, rank: 2 },
  { role_key: 'software engineer', name: 'Mumbai', value: 8, rank: 3 }
];
