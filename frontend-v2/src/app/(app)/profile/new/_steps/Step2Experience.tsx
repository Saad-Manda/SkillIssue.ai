"use client";
import { useFieldArray, useFormContext } from "react-hook-form";
import { Plus, Trash2 } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppInput } from "@/components/primitives/AppInput";
import { AppTextarea } from "@/components/primitives/AppTextarea";
import { TagInput } from "@/components/primitives/TagInput";
import { AppCard } from "@/components/primitives/AppCard";

const defaultExperience = {
  role: "", company: "", emp_type: "full_time",
  start_date: "", end_date: "", currently_working: false,
  loc_type: "onsite", location: "", description: "", skills_used: [],
};

export function Step2Experience() {
  const { register, watch, setValue, control } = useFormContext();
  const { fields, append, remove } = useFieldArray({ control, name: "experiences" });
  const experiences = watch("experiences") ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-text-main">Work Experience</h2>
          <p className="text-sm text-text-secondary mt-1">
            Add your professional history, most recent first.
          </p>
        </div>
        <AppButton
          type="button"
          variant="outline"
          size="sm"
          leftIcon={<Plus size={14} />}
          onClick={() => append(defaultExperience)}
        >
          Add
        </AppButton>
      </div>

      {fields.length === 0 && (
        <div className="text-center py-8 text-text-muted text-sm border-2 border-dashed border-warm-border rounded-xl">
          No experience added yet. Click &quot;Add&quot; to add your first role.
        </div>
      )}

      {fields.map((field, i) => {
        const currentlyWorking = experiences[i]?.currently_working;
        const skills = experiences[i]?.skills_used ?? [];

        return (
          <AppCard key={field.id} variant="outlined" className="relative">
            {/* Remove button */}
            <button
              type="button"
              onClick={() => remove(i)}
              className="absolute top-4 right-4 p-1.5 rounded-md text-text-muted hover:text-error hover:bg-error/10 transition-colors"
            >
              <Trash2 size={16} />
            </button>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pr-10">
              <AppInput label="Role / Title" placeholder="Senior Engineer" {...register(`experiences.${i}.role`)} required />
              <AppInput label="Company" placeholder="Acme Corp" {...register(`experiences.${i}.company`)} required />

              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-text-main">Employment Type</label>
                <select
                  className="w-full rounded-lg border border-warm-border bg-white px-3 py-2.5 text-sm text-text-main focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-600/20 font-sans"
                  {...register(`experiences.${i}.emp_type`)}
                >
                  <option value="full_time">Full-time</option>
                  <option value="part_time">Part-time</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-text-main">Location Type</label>
                <select
                  className="w-full rounded-lg border border-warm-border bg-white px-3 py-2.5 text-sm text-text-main focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-600/20 font-sans"
                  {...register(`experiences.${i}.loc_type`)}
                >
                  <option value="onsite">On-site</option>
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>

              <AppInput label="Start Date" type="date" {...register(`experiences.${i}.start_date`)} required />

              <div className="flex flex-col gap-1.5">
                <AppInput
                  label="End Date"
                  type="date"
                  disabled={currentlyWorking}
                  {...register(`experiences.${i}.end_date`)}
                />
                <label className="flex items-center gap-2 cursor-pointer mt-1">
                  <input
                    type="checkbox"
                    className="rounded border-warm-border accent-brand-600"
                    checked={currentlyWorking ?? false}
                    onChange={(e) =>
                      setValue(`experiences.${i}.currently_working`, e.target.checked)
                    }
                  />
                  <span className="text-xs text-text-secondary">Currently working here</span>
                </label>
              </div>

              <div className="sm:col-span-2">
                <TagInput
                  label="Skills Used"
                  tags={skills}
                  onChange={(tags) => setValue(`experiences.${i}.skills_used`, tags)}
                  placeholder="React, Node.js, AWS…"
                />
              </div>

              <div className="sm:col-span-2">
                <AppTextarea
                  label="Description"
                  placeholder="Describe your key responsibilities and achievements…"
                  {...register(`experiences.${i}.description`)}
                />
              </div>
            </div>
          </AppCard>
        );
      })}

      {fields.length > 0 && (
        <AppButton
          type="button"
          variant="ghost"
          size="sm"
          leftIcon={<Plus size={14} />}
          onClick={() => append(defaultExperience)}
        >
          Add another experience
        </AppButton>
      )}
    </div>
  );
}
