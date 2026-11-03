"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { ArrowRight, BriefcaseBusiness, MapPin, Search } from "lucide-react";
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  DEMO_JOBS,
  getEmployerJobsSnapshot,
  JOB_CATEGORIES,
  getServerEmployerJobsSnapshot,
  parseEmployerJobs,
  subscribeToEmployerJobs,
} from "@/lib/jobs";

const ALL_CATEGORIES = "All categories";

export default function JobsPage() {
  const employerJobsSnapshot = useSyncExternalStore(
    subscribeToEmployerJobs,
    getEmployerJobsSnapshot,
    getServerEmployerJobsSnapshot
  );
  const jobs = useMemo(
    () => [...parseEmployerJobs(employerJobsSnapshot), ...DEMO_JOBS],
    [employerJobsSnapshot]
  );
  const [searchTerm, setSearchTerm] = useState("");
  const [category, setCategory] = useState(ALL_CATEGORIES);

  const filteredJobs = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    return jobs.filter((job) => {
      const matchesTitle = job.title.toLowerCase().includes(normalizedSearch);
      const matchesCategory =
        category === ALL_CATEGORIES || job.category === category;

      return matchesTitle && matchesCategory;
    });
  }, [category, jobs, searchTerm]);

  return (
    <main className="min-h-screen bg-slate-50 pb-16 pt-24">
      <Navbar />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <section className="mb-8 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="mb-3 text-sm font-semibold uppercase tracking-[0.16em] text-blue-700">
              BlueHire job board
            </p>
            <h1 className="max-w-2xl text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Find work that moves you forward.
            </h1>
            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
              Explore trade and service roles from employers looking for
              reliable people like you.
            </p>
          </div>
          <Button
            asChild
            className="h-11 w-fit bg-blue-700 px-5 text-white hover:bg-blue-800"
          >
            <Link href="/employer">
              Post a job <ArrowRight className="ml-2 size-4" aria-hidden="true" />
            </Link>
          </Button>
        </section>

        <section
          aria-label="Search and filter jobs"
          className="mb-8 grid gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[minmax(0,1fr)_240px] sm:p-5"
        >
          <label className="relative block">
            <span className="sr-only">Search by job title</span>
            <Search
              className="absolute left-3 top-1/2 size-5 -translate-y-1/2 text-slate-400"
              aria-hidden="true"
            />
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search job titles"
              className="h-12 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-4 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </label>

          <label className="block">
            <span className="sr-only">Filter by category</span>
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="h-12 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option>{ALL_CATEGORIES}</option>
              {JOB_CATEGORIES.map((jobCategory) => (
                <option key={jobCategory} value={jobCategory}>
                  {jobCategory}
                </option>
              ))}
            </select>
          </label>
        </section>

        <div className="mb-4 flex items-center justify-between gap-4">
          <p className="text-sm font-medium text-slate-600" aria-live="polite">
            {filteredJobs.length} {filteredJobs.length === 1 ? "role" : "roles"} available
          </p>
          {searchTerm || category !== ALL_CATEGORIES ? (
            <button
              type="button"
              onClick={() => {
                setSearchTerm("");
                setCategory(ALL_CATEGORIES);
              }}
              className="text-sm font-semibold text-blue-700 hover:text-blue-900"
            >
              Clear filters
            </button>
          ) : null}
        </div>

        {filteredJobs.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2">
            {filteredJobs.map((job) => (
              <Link
                key={job.id}
                href={`/jobs/${encodeURIComponent(job.id)}`}
                className="rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                aria-label={`View details for ${job.title} at ${job.company}`}
              >
                <Card className="h-full border border-slate-200 bg-white py-0 shadow-sm transition-shadow hover:border-blue-200 hover:shadow-md">
                  <CardHeader className="flex-row items-start justify-between gap-4 px-5 pt-5">
                    <div className="flex min-w-0 items-start gap-3">
                      <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
                        <BriefcaseBusiness className="size-5" aria-hidden="true" />
                      </div>
                      <div className="min-w-0">
                        <CardTitle className="text-lg font-semibold text-slate-900">
                          {job.title}
                        </CardTitle>
                        <p className="mt-1 truncate text-sm text-slate-600">
                          {job.company}
                        </p>
                      </div>
                    </div>
                    <span className="shrink-0 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                      {job.category}
                    </span>
                  </CardHeader>
                  <CardContent className="px-5 pb-5 pt-2">
                    <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm text-slate-600">
                      <span className="inline-flex items-center gap-1.5">
                        <MapPin className="size-4 text-blue-700" aria-hidden="true" />
                        {job.location}
                      </span>
                      <span>{job.jobType}</span>
                    </div>
                    <div className="mt-4 flex items-center justify-between gap-4 border-t border-slate-100 pt-4">
                      <p className="font-semibold text-slate-900">{job.salary}</p>
                      <span className="inline-flex items-center gap-1 text-sm font-semibold text-blue-700">
                        View details <ArrowRight className="size-4" aria-hidden="true" />
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center">
            <h2 className="text-lg font-semibold text-slate-900">No matching jobs</h2>
            <p className="mt-2 text-sm text-slate-600">
              Try another title or choose a different category.
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
