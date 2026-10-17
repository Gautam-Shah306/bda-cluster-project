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

// ---------------------------------------------------------------------------
// F3 fixtures (worker, reskilling, chatbot). ALL OF THESE ARE contract-derived:
// they were built from the documented response shapes (docs/DECISIONS.md D-021,
// D-023, D-024, D-025 and the Python source), not captured from a running API.
// Re-capture them from a live API with a throwaway user when convenient.
// ---------------------------------------------------------------------------

/** contract-derived: GET /worker/profile for a brand-new user (signup defaults). */
export const contractNewUserProfile = {
  job_role: null,
  city: null,
  years_of_experience: null,
  role_description: null,
  skills: [],
  gemini_risk_score: null,
  reasoning: null,
  reskilling_path: null,
  gemini_analysis: null
};

/** contract-derived: GET /worker/profile after a profile was analyzed. */
export const contractSavedProfile = {
  job_role: 'BPO Voice Executive',
  city: 'Pune',
  years_of_experience: 3,
  role_description: 'Handle inbound customer calls and update the CRM.',
  skills: ['communication', 'crm'],
  gemini_risk_score: 78,
  reasoning: 'Base risk is high for scripted voice work.',
  reskilling_path: null,
  gemini_analysis: {
    risk_score: 78,
    risk_level: 'high',
    pivot_roles: ['AI Content Moderation Analyst', 'Data Analyst'],
    new_skills: ['Excel', 'SQL'],
    explanation: 'Base risk is high for scripted voice work.',
    raw_response: '{}'
  }
};

/** contract-derived: POST /worker/profile response. */
export const contractAnalyzeResponse = {
  parsed_profile: { role: 'BPO Voice Executive', city: 'Pune', experience: 3, skills: ['crm'] },
  gemini_analysis: contractSavedProfile.gemini_analysis
};

/** contract-derived: GET /worker/reskilling before any plan exists (reference empty shape). */
export const contractEmptyReskilling = {
  recommendation_type: null,
  summary: "No reskilling analysis generated yet. Click 'Generate' to create one.",
  recommended_skills: [],
  recommended_courses: [],
  recommended_jobs: [],
  learning_path: [],
  error: null
};

/** contract-derived: a full reskilling plan following the prompt's JSON schema. */
export const contractReskillingPlan = {
  recommendation_type: 'reskilling',
  summary: 'Move from scripted voice support towards data work.',
  recommended_skills: [
    { skill: 'Excel', reason: 'Used in almost every analytics role.' },
    { skill: 'SQL', reason: 'Core skill for data analyst openings.' }
  ],
  recommended_courses: [
    {
      name: 'Data Analysis with Python',
      source: 'NPTEL',
      url: 'https://onlinecourses.nptel.ac.in/noc25_cs00/preview',
      duration: '12 weeks',
      matched_skills: ['python', 'data analysis']
    }
  ],
  recommended_jobs: [
    {
      title: 'Junior Data Analyst',
      company: 'Acme Analytics',
      location: 'Pune',
      required_skills: ['excel', 'sql'],
      match_reason: 'Matches the Excel and SQL skills you are building.'
    }
  ],
  learning_path: [
    { week: 'Week 1-2', title: 'Spreadsheet basics', description: 'Learn formulas and pivot tables.' },
    { week: 'Week 3-6', title: 'SQL fundamentals', description: 'Practice joins and aggregation.' },
    { week: 'Week 7-12', title: 'Portfolio project', description: 'Analyse a public dataset.' }
  ],
  raw_response: '{}',
  error: null
};

/** contract-derived: POST /chatbot/query for a user without an analysis (canned reply in query_router.py). */
export const contractChatbotCanned = {
  response: "Please fill in the Worker Analysis page and click 'Analyze Risk & Opportunities' first."
};
