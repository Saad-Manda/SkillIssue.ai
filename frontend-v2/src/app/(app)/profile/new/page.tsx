"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Check, ChevronRight, Save, CheckCircle2 } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppCard } from "@/components/primitives/AppCard";
import { useCreateProfile, useUpdateProfile, useProfile } from "@/hooks/use-profile";
import { useAuthStore } from "@/store/auth-store";
import { cn } from "@/lib/utils";
import type { Experience, Education, Project, Leadership } from "@/types/api";

// Import step components
import { Step1BasicInfo }    from "./_steps/Step1BasicInfo";
import { Step2Experience }   from "./_steps/Step2Experience";
import { Step3Education }    from "./_steps/Step3Education";
import { Step4Projects }     from "./_steps/Step4Projects";
import { Step5Leadership }   from "./_steps/Step5Leadership";
import { Step6Review }       from "./_steps/Step6Review";

const STEPS = [
  { id: 1, label: "Basic Info",   short: "Info"       },
  { id: 2, label: "Experience",   short: "Work"       },
  { id: 3, label: "Education",    short: "Education"  },
  { id: 4, label: "Projects",     short: "Projects"   },
  { id: 5, label: "Leadership",   short: "Leadership" },
  { id: 6, label: "Review & Save", short: "Review"     },
];

// Merged full profile schema (validate all at save)
const fullProfileSchema = z.object({
  name:         z.string().min(1, "Name is required"),
  mobile:       z.string().optional(),
  github_url:   z.string().optional(),
  linkedin_url: z.string().optional(),
  skills:       z.array(z.string()).min(1, "Add at least one skill"),
  experiences:  z.array(z.any()),
  educations:   z.array(z.any()),
  projects:     z.array(z.any()),
  leaderships:  z.array(z.any()),
});

type FullProfileForm = z.infer<typeof fullProfileSchema>;

export default function ProfileWizardPage() {
  const router = useRouter();
  const pathname = usePathname();
  const isEdit = pathname.includes("/edit");
  const { user } = useAuthStore();
  const { data: existingProfile } = useProfile();
  const createProfile = useCreateProfile();
  const updateProfile = useUpdateProfile();

  const [currentStep, setCurrentStep] = useState(1);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const hasSaved = useRef(false);

  const methods = useForm<FullProfileForm>({
    resolver: zodResolver(fullProfileSchema),
    defaultValues: {
      name: "", mobile: "", github_url: "", linkedin_url: "",
      skills: [], experiences: [], educations: [], projects: [], leaderships: [],
    },
  });

  // Pre-fill from existing profile (edit mode or if profile exists)
  useEffect(() => {
    if (existingProfile && !hasSaved.current) {
      methods.reset({
        name:         existingProfile.name ?? "",
        mobile:       existingProfile.mobile ?? "",
        github_url:   existingProfile.github_url ?? "",
        linkedin_url: existingProfile.linkedin_url ?? "",
        skills:       existingProfile.skills ?? [],
        experiences:  existingProfile.experiences?.map(ex => ({
          ...ex,
          end_date: ex.end_date ?? "",
          currently_working: !ex.end_date,
          skills_used: ex.skills_used ?? [],
        })) ?? [],
        educations:  existingProfile.educations?.map(ed => ({
          ...ed,
          end_date: ed.end_date ?? "",
          currently_studying: !ed.end_date,
          courses: ed.courses ?? [],
        })) ?? [],
        projects:    existingProfile.projects?.map(p => ({
          ...p,
          skills_used: p.skills_used ?? [],
        })) ?? [],
        leaderships: existingProfile.leaderships?.map(l => ({
          ...l,
          end_date: l.end_date ?? "",
          currently_active: !l.end_date,
          skills_used: l.skills_used ?? [],
        })) ?? [],
      });
    }
  }, [existingProfile, methods]);

  const handleSave = async (data: FullProfileForm) => {
    try {
      const payload = {
        name:         data.name,
        mobile:       data.mobile,
        github_url:   data.github_url,
        linkedin_url: data.linkedin_url,
        skills:       data.skills,
        experiences:  data.experiences.map((ex: Experience) => ({
          role: ex.role,
          company: ex.company,
          emp_type: ex.emp_type,
          loc_type: ex.loc_type,
          location: ex.location || undefined,
          start_date: ex.start_date,
          end_date: ex.end_date || undefined,
          description: ex.description || undefined,
          skills_used: ex.skills_used ?? [],
        })),
        educations:  data.educations.map((ed: Omit<Education, "grade"> & { grade?: string | number }) => ({
          institute_name: ed.institute_name,
          degree: ed.degree,
          grade: parseFloat(String(ed.grade ?? "")) || 0,
          courses: ed.courses ?? [],
          start_date: ed.start_date,
          end_date: ed.end_date || undefined,
        })),
        projects:    data.projects.map((p: Project) => ({
          title: p.title,
          description: p.description,
          skills_used: p.skills_used ?? [],
          github_url: p.github_url || undefined,
          deployed_url: p.deployed_url || undefined,
        })),
        leaderships: data.leaderships.map((l: Leadership) => ({
          committee_name: l.committee_name,
          position: l.position,
          skills_used: l.skills_used ?? [],
          description: l.description || undefined,
          start_date: l.start_date,
          end_date: l.end_date || undefined,
        })),
      };

      if (isEdit || existingProfile) {
        await updateProfile.mutateAsync(payload);
      } else {
        await createProfile.mutateAsync({
          ...payload,
          user_id:        user?.id ?? "",
          email:          user?.email ?? "",
          username:       user?.username ?? "",
          is_active:      true,
        });
      }
      hasSaved.current = true;
      setSaveSuccess(true);
    } catch (err) {
      console.error(err);
    }
  };

  const StepContent = [
    Step1BasicInfo,
    Step2Experience,
    Step3Education,
    Step4Projects,
    Step5Leadership,
    Step6Review,
  ][currentStep - 1];

  const isSaving = createProfile.isPending || updateProfile.isPending;

  return (
    <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-main">
          {isEdit ? "Edit Profile" : "Build Your Profile"}
        </h1>
        <p className="text-sm text-text-secondary mt-1">
          A comprehensive profile helps the AI ask better, more targeted questions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Step sidebar */}
        <div className="lg:col-span-1">
          <AppCard className="sticky top-20">
            <nav aria-label="Profile wizard steps" className="space-y-1">
              {STEPS.map((step) => {
                const isActive    = step.id === currentStep;
                const isClickable = isEdit || step.id <= currentStep;
                return (
                  <button
                    key={step.id}
                    type="button"
                    onClick={() => isClickable && setCurrentStep(step.id)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-colors",
                      isActive    && "bg-brand-50 text-brand-700 font-medium",
                      !isActive && isClickable && "text-text-secondary hover:bg-warm-muted cursor-pointer",
                      !isActive && !isClickable && "text-text-muted cursor-not-allowed"
                    )}
                    disabled={!isClickable}
                  >
                    <div className={cn(
                      "flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold flex-shrink-0",
                      isActive    && "bg-brand-600 text-white",
                      !isActive && isClickable && "bg-success/15 text-success",
                      !isActive && !isClickable && "bg-warm-muted text-text-muted"
                    )}>
                      {!isActive && isClickable ? <Check size={12} /> : step.id}
                    </div>
                    <span className="hidden lg:block">{step.label}</span>
                    <span className="block lg:hidden">{step.short}</span>
                  </button>
                );
              })}
            </nav>

            {/* Save button at bottom of sidebar (shows on final step) */}
            {currentStep === 6 && (
              <div className="mt-4 pt-4 border-t border-warm-border">
                <AppButton
                  type="button"
                  variant="brand"
                  size="sm"
                  fullWidth
                  isLoading={isSaving}
                  leftIcon={<Save size={14} />}
                  onClick={() => methods.handleSubmit(handleSave)()}
                >
                  {saveSuccess ? "Saved!" : "Save Profile"}
                </AppButton>
              </div>
            )}
          </AppCard>
        </div>

        {/* Step content */}
        <div className="lg:col-span-3">
          <FormProvider {...methods}>
            <form
              onSubmit={(e) => {
                e.preventDefault();
              }}
              className="space-y-6"
            >
              <AppCard>
                {currentStep === 6 ? (
                  <Step6Review onEditStep={(step) => setCurrentStep(step)} />
                ) : (
                  <StepContent />
                )}
              </AppCard>

              {/* Navigation and Success buttons */}
              <div className="flex flex-col gap-4 mt-6">
                {saveSuccess && (
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-success/10 border border-success/30 rounded-xl px-4 py-3">
                    <div className="flex items-center gap-2 text-sm text-success font-medium">
                      <CheckCircle2 size={16} className="text-success flex-shrink-0" />
                      <span>Profile saved successfully!</span>
                    </div>
                    <div className="flex gap-2 w-full sm:w-auto justify-end">
                      <AppButton
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => router.push("/profile")}
                      >
                        View Profile
                      </AppButton>
                      <AppButton
                        type="button"
                        variant="brand"
                        size="sm"
                        onClick={() => router.push("/dashboard")}
                      >
                        Go to Dashboard
                      </AppButton>
                    </div>
                  </div>
                )}

                <div className="flex justify-between">
                  <AppButton
                    type="button"
                    variant="outline"
                    onClick={() =>
                      currentStep > 1
                        ? setCurrentStep((s) => s - 1)
                        : router.push("/dashboard")
                    }
                  >
                    {currentStep === 1 ? "Cancel" : "← Back"}
                  </AppButton>

                  {currentStep < 6 ? (
                    <AppButton
                      type="button"
                      variant="brand"
                      rightIcon={<ChevronRight size={16} />}
                      onClick={async () => {
                        // Validate only fields relevant to current step if desired,
                        // or just allow user to transition steps freely.
                        // For a smooth experience, we allow transitioning.
                        setCurrentStep((s) => s + 1);
                      }}
                    >
                      Continue
                    </AppButton>
                  ) : (
                    <AppButton
                      type="button"
                      variant="brand"
                      isLoading={isSaving}
                      leftIcon={<Save size={16} />}
                      onClick={() => methods.handleSubmit(handleSave)()}
                    >
                      {saveSuccess ? "Saved!" : "Save Profile"}
                    </AppButton>
                  )}
                </div>
              </div>
            </form>
          </FormProvider>
        </div>
      </div>
    </div>
  );
}
