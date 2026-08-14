"use client";
import { useFormContext } from "react-hook-form";
import {
  Briefcase, GraduationCap, Code, Trophy, Edit2, User, ExternalLink
} from "lucide-react";
import { Github } from "@/components/primitives/SocialIcons";
import { AppCard } from "@/components/primitives/AppCard";
import type { Experience, Education, Project, Leadership } from "@/types/api";
import { EMP_TYPE_LABELS, LOC_TYPE_LABELS } from "@/lib/constants";
import { formatDate } from "@/lib/utils";

interface Step6ReviewProps {
  onEditStep?: (step: number) => void;
}

export function Step6Review({ onEditStep }: Step6ReviewProps) {
  const { watch } = useFormContext();

  const name = watch("name");
  const mobile = watch("mobile");
  const github_url = watch("github_url");
  const linkedin_url = watch("linkedin_url");
  const skills = (watch("skills") as string[]) ?? [];
  const experiences = (watch("experiences") as Experience[]) ?? [];
  const educations = (watch("educations") as Education[]) ?? [];
  const projects = (watch("projects") as Project[]) ?? [];
  const leaderships = (watch("leaderships") as Leadership[]) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-main">Review Your Profile</h2>
        <p className="text-sm text-text-secondary mt-1">
          Please review your information below before saving. You can edit any section by clicking its Edit button.
        </p>
      </div>

      {/* Basic Info & Skills */}
      <AppCard variant="outlined" className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <User size={18} className="text-brand-600" />
            <h3 className="font-semibold text-text-main">Basic Information</h3>
          </div>
          {onEditStep && (
            <button
              type="button"
              onClick={() => onEditStep(1)}
              className="flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700 transition-colors font-medium font-sans"
            >
              <Edit2 size={12} /> Edit
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm font-sans mb-4">
          <div>
            <span className="block text-text-muted text-xs uppercase tracking-wider">Name</span>
            <span className="text-text-main font-medium">{name || "—"}</span>
          </div>
          <div>
            <span className="block text-text-muted text-xs uppercase tracking-wider">Mobile</span>
            <span className="text-text-main font-medium">{mobile || "—"}</span>
          </div>
          <div>
            <span className="block text-text-muted text-xs uppercase tracking-wider">GitHub</span>
            {github_url ? (
              <span className="text-text-main font-medium">{github_url}</span>
            ) : (
              <span className="text-text-muted italic">—</span>
            )}
          </div>
          <div>
            <span className="block text-text-muted text-xs uppercase tracking-wider">LinkedIn</span>
            {linkedin_url ? (
              <span className="text-text-main font-medium">{linkedin_url}</span>
            ) : (
              <span className="text-text-muted italic">—</span>
            )}
          </div>
        </div>

        {skills.length > 0 && (
          <div className="pt-4 border-t border-warm-border">
            <span className="block text-text-muted text-xs uppercase tracking-wider mb-2">Top Skills</span>
            <div className="flex flex-wrap gap-1.5">
              {skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-brand-50 text-brand-700 border border-brand-200"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
      </AppCard>

      {/* Experience */}
      <AppCard variant="outlined" className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Briefcase size={18} className="text-brand-600" />
            <h3 className="font-semibold text-text-main">Work Experience</h3>
          </div>
          {onEditStep && (
            <button
              type="button"
              onClick={() => onEditStep(2)}
              className="flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700 transition-colors font-medium font-sans"
            >
              <Edit2 size={12} /> Edit
            </button>
          )}
        </div>

        {experiences.length === 0 ? (
          <p className="text-sm text-text-muted italic font-sans">No work experience added. (Optional)</p>
        ) : (
          <div className="space-y-4">
            {experiences.map((exp, i) => (
              <div key={i} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="h-1.5 w-1.5 rounded-full bg-brand-500 mt-1.5" />
                  {i < experiences.length - 1 && (
                    <div className="flex-1 w-px bg-warm-border mt-2" />
                  )}
                </div>
                <div className="min-w-0 flex-1 font-sans">
                  <h4 className="font-medium text-sm text-text-main">
                    {exp.role}{" "}
                    <span className="font-normal text-text-secondary">at {exp.company}</span>
                  </h4>
                  <p className="text-xs text-text-muted mt-0.5">
                    {exp.start_date ? formatDate(exp.start_date) : "—"} – {exp.end_date ? formatDate(exp.end_date) : "Present"}
                    {" · "}{EMP_TYPE_LABELS[exp.emp_type] ?? exp.emp_type}
                    {exp.loc_type && ` · ${LOC_TYPE_LABELS[exp.loc_type] ?? exp.loc_type}`}
                  </p>
                  {exp.description && (
                    <p className="text-xs text-text-secondary mt-1.5 leading-relaxed whitespace-pre-wrap">{exp.description}</p>
                  )}
                  {exp.skills_used && exp.skills_used.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {exp.skills_used.map((s) => (
                        <span key={s} className="text-[10px] px-1.5 py-0.5 bg-warm-muted text-text-secondary rounded">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </AppCard>

      {/* Education */}
      <AppCard variant="outlined" className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <GraduationCap size={18} className="text-brand-600" />
            <h3 className="font-semibold text-text-main">Education</h3>
          </div>
          {onEditStep && (
            <button
              type="button"
              onClick={() => onEditStep(3)}
              className="flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700 transition-colors font-medium font-sans"
            >
              <Edit2 size={12} /> Edit
            </button>
          )}
        </div>

        {educations.length === 0 ? (
          <p className="text-sm text-text-muted italic font-sans">No education details added. (Optional)</p>
        ) : (
          <div className="space-y-4">
            {educations.map((edu, i) => (
              <div key={i} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="h-1.5 w-1.5 rounded-full bg-brand-500 mt-1.5" />
                  {i < educations.length - 1 && (
                    <div className="flex-1 w-px bg-warm-border mt-2" />
                  )}
                </div>
                <div className="min-w-0 flex-1 font-sans">
                  <h4 className="font-medium text-sm text-text-main">
                    {edu.degree}{" "}
                    <span className="font-normal text-text-secondary">from {edu.institute_name}</span>
                  </h4>
                  <p className="text-xs text-text-muted mt-0.5">
                    {edu.start_date ? formatDate(edu.start_date) : "—"} – {edu.end_date ? formatDate(edu.end_date) : "Present"}
                    {edu.grade ? ` · GPA/Grade: ${edu.grade}` : ""}
                  </p>
                  {edu.courses && edu.courses.length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-1">
                      {edu.courses.map((course) => (
                        <span key={course} className="text-[10px] px-1.5 py-0.5 bg-brand-50/50 text-brand-700/80 rounded border border-brand-100">
                          {course}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </AppCard>

      {/* Projects */}
      <AppCard variant="outlined" className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Code size={18} className="text-brand-600" />
            <h3 className="font-semibold text-text-main">Projects</h3>
          </div>
          {onEditStep && (
            <button
              type="button"
              onClick={() => onEditStep(4)}
              className="flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700 transition-colors font-medium font-sans"
            >
              <Edit2 size={12} /> Edit
            </button>
          )}
        </div>

        {projects.length === 0 ? (
          <p className="text-sm text-text-muted italic font-sans">No projects added. (Optional)</p>
        ) : (
          <div className="space-y-4">
            {projects.map((proj, i) => (
              <div key={i} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="h-1.5 w-1.5 rounded-full bg-brand-500 mt-1.5" />
                  {i < projects.length - 1 && (
                    <div className="flex-1 w-px bg-warm-border mt-2" />
                  )}
                </div>
                <div className="min-w-0 flex-1 font-sans">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium text-sm text-text-main">{proj.title}</h4>
                    {proj.github_url && (
                      <a
                        href={`https://${proj.github_url.replace(/^https?:\/\//, "")}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-text-muted hover:text-brand-600 transition-colors"
                      >
                        <Github size={12} />
                      </a>
                    )}
                    {proj.deployed_url && (
                      <a
                        href={`https://${proj.deployed_url.replace(/^https?:\/\//, "")}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-text-muted hover:text-brand-600 transition-colors"
                      >
                        <ExternalLink size={12} />
                      </a>
                    )}
                  </div>
                  {proj.description && (
                    <p className="text-xs text-text-secondary mt-1 leading-relaxed whitespace-pre-wrap">{proj.description}</p>
                  )}
                  {proj.skills_used && proj.skills_used.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {proj.skills_used.map((s) => (
                        <span key={s} className="text-[10px] px-1.5 py-0.5 bg-warm-muted text-text-secondary rounded">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </AppCard>

      {/* Leadership */}
      <AppCard variant="outlined" className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Trophy size={18} className="text-brand-600" />
            <h3 className="font-semibold text-text-main">Leadership & Volunteering</h3>
          </div>
          {onEditStep && (
            <button
              type="button"
              onClick={() => onEditStep(5)}
              className="flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700 transition-colors font-medium font-sans"
            >
              <Edit2 size={12} /> Edit
            </button>
          )}
        </div>

        {leaderships.length === 0 ? (
          <p className="text-sm text-text-muted italic font-sans">No leadership or volunteering roles added. (Optional)</p>
        ) : (
          <div className="space-y-4">
            {leaderships.map((lead, i) => (
              <div key={i} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="h-1.5 w-1.5 rounded-full bg-brand-500 mt-1.5" />
                  {i < leaderships.length - 1 && (
                    <div className="flex-1 w-px bg-warm-border mt-2" />
                  )}
                </div>
                <div className="min-w-0 flex-1 font-sans">
                  <h4 className="font-medium text-sm text-text-main">
                    {lead.position}{" "}
                    <span className="font-normal text-text-secondary">at {lead.committee_name}</span>
                  </h4>
                  <p className="text-xs text-text-muted mt-0.5">
                    {lead.start_date ? formatDate(lead.start_date) : "—"} – {lead.end_date ? formatDate(lead.end_date) : "Present"}
                  </p>
                  {lead.description && (
                    <p className="text-xs text-text-secondary mt-1.5 leading-relaxed whitespace-pre-wrap">{lead.description}</p>
                  )}
                  {lead.skills_used && lead.skills_used.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {lead.skills_used.map((s) => (
                        <span key={s} className="text-[10px] px-1.5 py-0.5 bg-warm-muted text-text-secondary rounded">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </AppCard>
    </div>
  );
}
