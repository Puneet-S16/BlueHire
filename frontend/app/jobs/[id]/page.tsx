"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, BriefcaseBusiness, CheckCircle2, MapPin } from "lucide-react";
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  DEMO_JOBS,
  getEmployerJobsSnapshot,
  getServerEmployerJobsSnapshot,
  isEmployerJobsSnapshotReady,
  parseEmployerJobs,
  subscribeToEmployerJobs,
} from "@/lib/jobs";

export default function JobDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const employerJobsSnapshot = useSyncExternalStore(
    subscribeToEmployerJobs,
    getEmployerJobsSnapshot,
    getServerEmployerJobsSnapshot
  );
  const job = useMemo(
    () =>
      [...parseEmployerJobs(employerJobsSnapshot), ...DEMO_JOBS].find(
        (listedJob) => listedJob.id === id
      ) ?? null,
    [employerJobsSnapshot, id]
  );
  const [appliedJobId, setAppliedJobId] = useState<string | null>(null);
  const hasApplied = appliedJobId === id;

  return (
    <main className="min-h-screen bg-slate-50 pb-16 pt-24">
      <Navbar />
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <Link
          href="/jobs"
          className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-blue-700 hover:text-blue-900"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to jobs
        </Link>

        {!job && !isEmployerJobsSnapshotReady(employerJobsSnapshot) ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 text-slate-600">
            Loading job details…
          </div>
        ) : !job ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center">
            <h1 className="text-2xl font-bold text-slate-900">Job not found</h1>
            <p className="mt-2 text-slate-600">
              This listing may have been removed from this browser.
            </p>
            <Button
              asChild
              className="mt-5 bg-blue-700 text-white hover:bg-blue-800"
            >
              <Link href="/jobs">Browse open jobs</Link>
            </Button>
          </div>
        ) : (
          <div className="space-y-5">
            <Card className="border border-slate-200 bg-white shadow-sm">
              <CardContent className="p-6 sm:p-8">
                <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <span className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                      {job.category}
                    </span>
                    <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                      {job.title}
                    </h1>
                    <p className="mt-2 text-lg font-medium text-slate-600">
                      {job.company}
                    </p>
                  </div>
                  <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-blue-50 text-blue-700">
                    <BriefcaseBusiness className="size-7" aria-hidden="true" />
                  </div>
                </div>

                <div className="mt-7 flex flex-wrap gap-x-6 gap-y-3 border-y border-slate-100 py-5 text-sm text-slate-600">
                  <span className="inline-flex items-center gap-2">
                    <MapPin className="size-4 text-blue-700" aria-hidden="true" />
                    {job.location}
                  </span>
                  <span>{job.jobType}</span>
                  <span className="font-semibold text-slate-900">{job.salary}</span>
                </div>

                <div className="mt-6">
                  <h2 className="text-lg font-semibold text-slate-900">About the role</h2>
                  <p className="mt-3 leading-7 text-slate-600">{job.description}</p>
                </div>

                <div className="mt-7">
                  <h2 className="text-lg font-semibold text-slate-900">Requirements</h2>
                  <ul className="mt-3 space-y-2 text-slate-600">
                    {job.requirements.map((requirement) => (
                      <li key={requirement} className="flex gap-3 leading-6">
                        <span className="mt-2 size-1.5 shrink-0 rounded-full bg-blue-600" aria-hidden="true" />
                        <span>{requirement}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-8 border-t border-slate-100 pt-6">
                  <Button
                    type="button"
                    onClick={() => setAppliedJobId(id)}
                    disabled={hasApplied}
                    className="h-11 w-full bg-blue-700 text-white hover:bg-blue-800 disabled:bg-blue-400 sm:w-auto sm:px-10"
                  >
                    {hasApplied ? "Applied" : "Apply"}
                  </Button>
                  {hasApplied ? (
                    <p
                      role="status"
                      className="mt-4 flex items-center gap-2 text-sm text-emerald-700"
                    >
                      <CheckCircle2 className="size-4" aria-hidden="true" />
                      Demo application complete. Nothing was sent to the employer.
                    </p>
                  ) : (
                    <p className="mt-3 text-xs text-slate-500">
                      This is a demo interaction. Your application will not be sent.
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </main>
  );
}
