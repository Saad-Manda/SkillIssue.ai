"use client";
import { useRouter } from "next/navigation";
import {
  Briefcase, GraduationCap, Code, Trophy, Edit2, PlusCircle, ExternalLink
} from "lucide-react";
import { Github, Linkedin } from "@/components/primitives/SocialIcons";
import { AppCard } from "@/components/primitives/AppCard";
import { AppButton } from "@/components/primitives/AppButton";
import { InitialsAvatar } from "@/components/primitives/InitialsAvatar";
import { ProfileSectionSkeleton } from "@/components/primitives/Skeletons";
import { EmptyState } from "@/components/primitives/EmptyState";
import { useProfile } from "@/hooks/use-profile";
import { formatDate } from "@/lib/utils";
import { EMP_TYPE_LABELS, LOC_TYPE_LABELS } from "@/lib/constants";

export default function ProfileViewPage() {
  const router = useRouter();
  const { data: profile, isLoading } = useProfile();

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        <ProfileSectionSkeleton />
        <ProfileSectionSkeleton />
        <ProfileSectionSkeleton />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <EmptyState
          icon={PlusCircle}
          title="No profile yet"
          description="Build your comprehensive profile to get AI-tailored interview questions."
          action={
            <AppButton variant="brand" onClick={() => router.push("/profile/new")}>
              Build Profile
            </AppButton>
          }
        />
      </div>
    );
  }

  const currentRole = profile.experiences?.[0];

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 space-y-6">
      {/* Hero Card */}
      <AppCard>
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4 text-center sm:text-left">
            <InitialsAvatar name={profile.name} size="xl" />
            <div className="min-w-0">
              <h1 className="text-2xl font-semibold text-text-main">{profile.name}</h1>
              {currentRole && (
                <p className="text-base text-text-secondary mt-0.5">
                  {currentRole.role} at {currentRole.company}
                </p>
              )}
              <div className="flex flex-wrap justify-center sm:justify-start items-center gap-x-4 gap-y-2 mt-3 text-sm text-text-muted font-sans">
                {profile.mobile && (
                  <span>{profile.mobile}</span>
                )}
                {profile.github_url && (
                  <a
                    href={`https://${profile.github_url.replace(/^https?:\/\//, "")}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 text-brand-600 hover:text-brand-700 transition-colors"
                  >
                    <Github size={14} /> GitHub
                  </a>
                )}
                {profile.linkedin_url && (
                  <a
                    href={`https://${profile.linkedin_url.replace(/^https?:\/\//, "")}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 text-brand-600 hover:text-brand-700 transition-colors"
                  >
                    <Linkedin size={14} /> LinkedIn
                  </a>
                )}
              </div>
            </div>
          </div>

          <AppButton
            variant="outline"
            size="sm"
            leftIcon={<Edit2 size={14} />}
            onClick={() => router.push("/profile/edit")}
            className="flex-shrink-0 self-center sm:self-start"
          >
            Edit
          </AppButton>
        </div>

        {/* Skills */}
        {profile.skills?.length > 0 && (
          <div className="mt-6 pt-6 border-t border-warm-border">
            <p className="text-xs font-semibold uppercase tracking-widest text-text-muted mb-3 font-sans">
              Top Skills
            </p>
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-brand-50 text-brand-700 border border-brand-200"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
      </AppCard>

      {/* Experience */}
      {profile.experiences && profile.experiences.length > 0 && (
        <AppCard>
          <div className="flex items-center gap-2 mb-6 pb-4 border-b border-warm-border">
            <Briefcase size={18} className="text-brand-600" />
            <h2 className="text-lg font-semibold text-text-main">Experience</h2>
          </div>
          <div className="space-y-6">
            {profile.experiences.map((exp, i) => (
              <div key={i} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="h-2 w-2 rounded-full bg-brand-500 mt-1.5" />
                  {i < profile.experiences.length - 1 && (
                    <div className="flex-1 w-px bg-warm-border mt-2" />
                  )}
                </div>
                <div className="pb-2 min-w-0 flex-1">
                  <h3 className="font-semibold text-text-main">
                    {exp.role}{" "}
                    <span className="font-normal text-text-secondary font-sans">at {exp.company}</span>
                  </h3>
                  <p className="text-sm text-text-muted mt-0.5 font-sans">
                    {formatDate(exp.start_date)} – {exp.end_date ? formatDate(exp.end_date) : "Present"}
                    {" · "}{EMP_TYPE_LABELS[exp.emp_type] ?? exp.emp_type}
                    {exp.loc_type && ` · ${LOC_TYPE_LABELS[exp.loc_type] ?? exp.loc_type}`}
                  </p>
                  {exp.description && (
                    <p className="text-sm text-text-main mt-2 leading-relaxed font-sans whitespace-pre-wrap">{exp.description}</p>
                  )}
                  {exp.skills_used?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {exp.skills_used.map((s: string) => (
                        <span key={s} className="text-xs px-2 py-0.5 bg-warm-muted text-text-secondary rounded-md">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </AppCard>
      )}

      {/* Education */}
      {profile.educations && profile.educations.length > 0 && (
        <AppCard>
          <div className="flex items-center gap-2 mb-6 pb-4 border-b border-warm-border">
            <GraduationCap size={18} className="text-brand-600" />
            <h2 className="text-lg font-semibold text-text-main">Education</h2>
          </div>
          <div className="space-y-6">
            {profile.educations.map((edu, i) => (
              <div key={i} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="h-2 w-2 rounded-full bg-brand-500 mt-1.5" />
                  {i < profile.educations.length - 1 && (
                    <div className="flex-1 w-px bg-warm-border mt-2" />
                  )}
                </div>
                <div className="pb-2 min-w-0 flex-1">
                  <h3 className="font-semibold text-text-main">
                    {edu.degree}{" "}
                    <span className="font-normal text-text-secondary font-sans">from {edu.institute_name}</span>
                  </h3>
                  <p className="text-sm text-text-muted mt-0.5 font-sans font-normal">
                    {formatDate(edu.start_date)} – {edu.end_date ? formatDate(edu.end_date) : "Present"}
                    {edu.grade ? ` · GPA/Grade: ${edu.grade}` : ""}
                  </p>
                  {edu.courses?.length > 0 && (
                    <div className="mt-2 font-sans">
                      <span className="text-xs text-text-secondary font-medium mr-1.5">Courses:</span>
                      <span className="text-xs text-text-muted">{edu.courses.join(", ")}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </AppCard>
      )}

      {/* Projects */}
      {profile.projects && profile.projects.length > 0 && (
        <AppCard>
          <div className="flex items-center gap-2 mb-6 pb-4 border-b border-warm-border">
            <Code size={18} className="text-brand-600" />
            <h2 className="text-lg font-semibold text-text-main">Projects</h2>
          </div>
          <div className="space-y-6">
            {profile.projects.map((proj, i) => (
              <div key={i} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="h-2 w-2 rounded-full bg-brand-500 mt-1.5" />
                  {i < profile.projects.length - 1 && (
                    <div className="flex-1 w-px bg-warm-border mt-2" />
                  )}
                </div>
                <div className="pb-2 min-w-0 flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-text-main">{proj.title}</h3>
                    {proj.github_url && (
                      <a
                        href={`https://${proj.github_url.replace(/^https?:\/\//, "")}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-text-muted hover:text-brand-600 transition-colors"
                        aria-label="GitHub Repository"
                      >
                        <Github size={16} />
                      </a>
                    )}
                    {proj.deployed_url && (
                      <a
                        href={`https://${proj.deployed_url.replace(/^https?:\/\//, "")}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-text-muted hover:text-brand-600 transition-colors"
                        aria-label="Live Demo"
                      >
                        <ExternalLink size={16} />
                      </a>
                    )}
                  </div>
                  <p className="text-sm text-text-main mt-1 leading-relaxed font-sans whitespace-pre-wrap">{proj.description}</p>
                  {proj.skills_used?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {proj.skills_used.map((s: string) => (
                        <span key={s} className="text-xs px-2 py-0.5 bg-warm-muted text-text-secondary rounded-md font-sans">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </AppCard>
      )}

      {/* Leadership */}
      {profile.leaderships && profile.leaderships.length > 0 && (
        <AppCard>
          <div className="flex items-center gap-2 mb-6 pb-4 border-b border-warm-border">
            <Trophy size={18} className="text-brand-600" />
            <h2 className="text-lg font-semibold text-text-main">Leadership & Volunteering</h2>
          </div>
          <div className="space-y-6">
            {profile.leaderships.map((lead, i) => (
              <div key={i} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="h-2 w-2 rounded-full bg-brand-500 mt-1.5" />
                  {i < profile.leaderships.length - 1 && (
                    <div className="flex-1 w-px bg-warm-border mt-2" />
                  )}
                </div>
                <div className="pb-2 min-w-0 flex-1">
                  <h3 className="font-semibold text-text-main">
                    {lead.position}{" "}
                    <span className="font-normal text-text-secondary font-sans">at {lead.committee_name}</span>
                  </h3>
                  <p className="text-sm text-text-muted mt-0.5 font-sans font-normal">
                    {formatDate(lead.start_date)} – {lead.end_date ? formatDate(lead.end_date) : "Present"}
                  </p>
                  {lead.description && (
                    <p className="text-sm text-text-main mt-2 leading-relaxed font-sans whitespace-pre-wrap">{lead.description}</p>
                  )}
                  {lead.skills_used?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {lead.skills_used.map((s: string) => (
                        <span key={s} className="text-xs px-2 py-0.5 bg-warm-muted text-text-secondary rounded-md font-sans font-normal">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </AppCard>
      )}
    </div>
  );
}
