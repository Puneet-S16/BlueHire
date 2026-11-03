"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, BriefcaseBusiness, CheckCircle2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { JOB_CATEGORIES, saveEmployerJob } from "@/lib/jobs";

const fieldClassName =
  "mt-2 h-11 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100";

export default function EmployerPage() {
  const [message, setMessage] = useState("");
  const [hasSaved, setHasSaved] = useState(false);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const form = event.currentTarget;
    const formData = new FormData(form);
    const job = {
      id: `employer-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      title: String(formData.get("title")).trim(),
      company: String(formData.get("company")).trim(),
      location: String(formData.get("location")).trim(),
      salary: String(formData.get("salary")).trim(),
      category: String(formData.get("category")),
      description: String(formData.get("description")).trim(),
      jobType: "Employer posted",
      requirements: ["See the job description for role requirements."],
    };

    if (saveEmployerJob(job)) {
      setHasSaved(true);
      setMessage(`“${job.title}” has been saved in this browser.`);
      form.reset();
    } else {
      setHasSaved(false);
      setMessage("This browser could not save the job. Check its storage settings and try again.");
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 pb-16 pt-24">
      <Navbar />
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <Link
          href="/jobs"
          className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-blue-700 hover:text-blue-900"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Browse jobs
        </Link>

        <div className="grid gap-8 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)] lg:items-start">
          <section className="pt-2">
            <div className="mb-4 flex size-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-700">
              <BriefcaseBusiness className="size-6" aria-hidden="true" />
            </div>
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-700">
              For employers
            </p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Share your next opportunity.
            </h1>
            <p className="mt-4 max-w-lg leading-7 text-slate-600">
              Add a role to the BlueHire demo job board. Your post is saved in
              this browser and appears in the jobs list on this device.
            </p>
            <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm leading-6 text-blue-900">
              Demo posting only. No account is needed, and your listing is not
              sent to a server.
            </div>
          </section>

          <Card className="border border-slate-200 bg-white shadow-sm">
            <CardContent className="p-5 sm:p-7">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid gap-5 sm:grid-cols-2">
                  <label className="block text-sm font-medium text-slate-700">
                    Job title
                    <input
                      name="title"
                      required
                      maxLength={100}
                      placeholder="e.g. Residential Electrician"
                      className={fieldClassName}
                    />
                  </label>
                  <label className="block text-sm font-medium text-slate-700">
                    Company
                    <input
                      name="company"
                      required
                      maxLength={100}
                      placeholder="Company name"
                      className={fieldClassName}
                    />
                  </label>
                  <label className="block text-sm font-medium text-slate-700">
                    Location
                    <input
                      name="location"
                      required
                      maxLength={100}
                      placeholder="City, State"
                      className={fieldClassName}
                    />
                  </label>
                  <label className="block text-sm font-medium text-slate-700">
                    Salary
                    <input
                      name="salary"
                      required
                      maxLength={80}
                      placeholder="e.g. $28–$35 per hour"
                      className={fieldClassName}
                    />
                  </label>
                  <label className="block text-sm font-medium text-slate-700 sm:col-span-2">
                    Category
                    <select
                      name="category"
                      required
                      defaultValue=""
                      className={fieldClassName}
                    >
                      <option value="" disabled>
                        Choose a category
                      </option>
                      {JOB_CATEGORIES.map((category) => (
                        <option key={category} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block text-sm font-medium text-slate-700 sm:col-span-2">
                    Description
                    <textarea
                      name="description"
                      required
                      maxLength={2000}
                      rows={5}
                      placeholder="Describe the work, schedule, and experience you are looking for."
                      className="mt-2 w-full resize-y rounded-lg border border-slate-200 bg-white px-3 py-3 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    />
                  </label>
                </div>

                {message ? (
                  <div
                    role={hasSaved ? "status" : "alert"}
                    className={`flex items-start gap-2 rounded-lg p-3 text-sm leading-6 ${
                      hasSaved
                        ? "bg-emerald-50 text-emerald-800"
                        : "bg-amber-50 text-amber-900"
                    }`}
                  >
                    {hasSaved ? (
                      <CheckCircle2 className="mt-1 size-4 shrink-0" aria-hidden="true" />
                    ) : null}
                    <span>{message}</span>
                  </div>
                ) : null}

                <Button
                  type="submit"
                  className="h-11 w-full bg-blue-700 text-white hover:bg-blue-800 sm:w-auto sm:px-8"
                >
                  Save job posting
                </Button>
              </form>

              {hasSaved ? (
                <Link
                  href="/jobs"
                  className="mt-5 inline-flex text-sm font-semibold text-blue-700 hover:text-blue-900"
                >
                  View the job board <span aria-hidden="true">→</span>
                </Link>
              ) : null}
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
