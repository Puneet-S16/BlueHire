export const JOB_CATEGORIES = [
  "Construction",
  "Electrical",
  "Plumbing",
  "HVAC",
  "Transportation",
  "Welding",
  "Warehousing",
] as const;

export type Job = {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  jobType: string;
  category: string;
  description: string;
  requirements: string[];
};

export const DEMO_JOBS: Job[] = [
  {
    id: "residential-electrician",
    title: "Residential Electrician",
    company: "BrightSpark Electrical",
    location: "Austin, TX",
    salary: "$28–$36 per hour",
    jobType: "Full-time",
    category: "Electrical",
    description:
      "Install and service electrical systems in homes across the Austin area. You will work with a small crew on remodels, new builds, and scheduled service calls.",
    requirements: [
      "Texas journeyman electrician license or equivalent experience",
      "At least 3 years of residential electrical experience",
      "Valid driver's license and a commitment to safe work practices",
    ],
  },
  {
    id: "commercial-plumber",
    title: "Commercial Plumber",
    company: "Harbor Mechanical",
    location: "Seattle, WA",
    salary: "$30–$42 per hour",
    jobType: "Full-time",
    category: "Plumbing",
    description:
      "Join our commercial service team maintaining plumbing systems in offices, schools, and retail spaces. The role includes planned maintenance and occasional installation projects.",
    requirements: [
      "Commercial plumbing experience",
      "Washington plumbing certification or ability to obtain it",
      "Able to read plans and communicate clearly with customers",
    ],
  },
  {
    id: "site-supervisor",
    title: "Construction Site Supervisor",
    company: "Northline Builders",
    location: "Denver, CO",
    salary: "$72,000–$88,000 per year",
    jobType: "Full-time",
    category: "Construction",
    description:
      "Coordinate day-to-day work on residential construction projects. You will keep crews on schedule, review site safety, and help resolve issues as they arise.",
    requirements: [
      "5 years of construction experience, including crew coordination",
      "Strong knowledge of jobsite safety and building plans",
      "Reliable transportation to sites around the Denver metro area",
    ],
  },
  {
    id: "hvac-technician",
    title: "HVAC Service Technician",
    company: "ClearAir Services",
    location: "Phoenix, AZ",
    salary: "$26–$34 per hour",
    jobType: "Full-time",
    category: "HVAC",
    description:
      "Diagnose, repair, and maintain residential heating and cooling systems. Our technicians receive a stocked service vehicle and daily support from an experienced dispatch team.",
    requirements: [
      "2 or more years servicing HVAC equipment",
      "EPA Section 608 certification",
      "Comfortable working outdoors in warm weather",
    ],
  },
  {
    id: "class-a-driver",
    title: "CDL Class A Driver",
    company: "Summit Supply Co.",
    location: "Nashville, TN",
    salary: "$26–$31 per hour",
    jobType: "Full-time",
    category: "Transportation",
    description:
      "Deliver building materials to job sites on local routes. Most shifts start in the morning and bring you home at the end of the day.",
    requirements: [
      "Current CDL Class A license",
      "Clean driving record and a safety-first approach",
      "Able to help secure and unload materials when needed",
    ],
  },
  {
    id: "welder-fabricator",
    title: "Welder / Fabricator",
    company: "Ironwood Fabrication",
    location: "Cleveland, OH",
    salary: "$25–$33 per hour",
    jobType: "Full-time",
    category: "Welding",
    description:
      "Fabricate custom steel assemblies from shop drawings. This position works in a clean, well-equipped shop with a steady mix of production and one-off projects.",
    requirements: [
      "MIG welding experience; TIG experience is a plus",
      "Ability to read measurements and fabrication drawings",
      "Dependable attendance and attention to detail",
    ],
  },
  {
    id: "warehouse-operator",
    title: "Warehouse Equipment Operator",
    company: "Riverbend Logistics",
    location: "Columbus, OH",
    salary: "$21–$26 per hour",
    jobType: "Full-time",
    category: "Warehousing",
    description:
      "Move incoming and outgoing materials safely through a busy distribution center. The team uses modern scanning tools and offers stable, year-round shifts.",
    requirements: [
      "Experience operating a forklift or pallet jack",
      "Able to lift and move materials throughout a shift",
      "Comfortable following inventory and safety procedures",
    ],
  },
  {
    id: "finish-carpenter",
    title: "Finish Carpenter",
    company: "TrueLine Renovations",
    location: "Portland, OR",
    salary: "$28–$38 per hour",
    jobType: "Contract",
    category: "Construction",
    description:
      "Install trim, doors, and cabinetry on residential renovation projects. Work is scheduled in advance with a consistent local crew and quality materials.",
    requirements: [
      "3 years of finish carpentry experience",
      "Own basic hand tools and reliable transportation",
      "Able to measure accurately and leave a tidy work area",
    ],
  },
];

export const EMPLOYER_JOBS_STORAGE_KEY = "bluehire:employer-jobs:v1";
const EMPLOYER_JOBS_CHANGE_EVENT = "bluehire:employer-jobs-change";
const SERVER_JOBS_SNAPSHOT = "__bluehire_server_snapshot__";

function isJob(value: unknown): value is Job {
  if (!value || typeof value !== "object") return false;

  const job = value as Partial<Job>;
  return (
    typeof job.id === "string" &&
    typeof job.title === "string" &&
    typeof job.company === "string" &&
    typeof job.location === "string" &&
    typeof job.salary === "string" &&
    typeof job.jobType === "string" &&
    typeof job.category === "string" &&
    typeof job.description === "string" &&
    Array.isArray(job.requirements) &&
    job.requirements.every((requirement) => typeof requirement === "string")
  );
}

export function parseEmployerJobs(snapshot: string): Job[] {
  if (snapshot === SERVER_JOBS_SNAPSHOT) return [];
  try {
    const storedJobs: unknown = JSON.parse(snapshot);
    return Array.isArray(storedJobs) ? storedJobs.filter(isJob) : [];
  } catch {
    return [];
  }
}

export function getEmployerJobsSnapshot(): string {
  if (typeof window === "undefined") return SERVER_JOBS_SNAPSHOT;

  try {
    return window.localStorage.getItem(EMPLOYER_JOBS_STORAGE_KEY) ?? "[]";
  } catch {
    return "[]";
  }
}

export function getServerEmployerJobsSnapshot(): string {
  return SERVER_JOBS_SNAPSHOT;
}

export function isEmployerJobsSnapshotReady(snapshot: string): boolean {
  return snapshot !== SERVER_JOBS_SNAPSHOT;
}

export function subscribeToEmployerJobs(onChange: () => void): () => void {
  if (typeof window === "undefined") return () => {};

  window.addEventListener("storage", onChange);
  window.addEventListener(EMPLOYER_JOBS_CHANGE_EVENT, onChange);

  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener(EMPLOYER_JOBS_CHANGE_EVENT, onChange);
  };
}

export function saveEmployerJob(job: Job): boolean {
  if (typeof window === "undefined") return false;

  try {
    window.localStorage.setItem(
      EMPLOYER_JOBS_STORAGE_KEY,
      JSON.stringify([job, ...parseEmployerJobs(getEmployerJobsSnapshot())])
    );
    window.dispatchEvent(new Event(EMPLOYER_JOBS_CHANGE_EVENT));
    return true;
  } catch {
    return false;
  }
}
