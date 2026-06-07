"use client";
import { useFieldArray, useFormContext } from "react-hook-form";
import { Plus, Trash2 } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppInput } from "@/components/primitives/AppInput";
import { AppTextarea } from "@/components/primitives/AppTextarea";
import { TagInput } from "@/components/primitives/TagInput";
import { AppCard } from "@/components/primitives/AppCard";

const defaultLeadership = {
  committee_name: "", position: "", skills_used: [], description: "", start_date: "", end_date: "", currently_active: false,
};

export function Step5Leadership() {
  const { register, watch, setValue, control } = useFormContext();
  const { fields, append, remove } = useFieldArray({ control, name: "leaderships" });
  const leaderships = watch("leaderships") ?? [];

  return (
    <div className="space-y-8">
      {/* Leadership Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-text-main">Leadership & Volunteering</h2>
            <p className="text-sm text-text-secondary mt-1">
              Add any club leadership, student government, or volunteering roles.
            </p>
          </div>
          <AppButton
            type="button"
            variant="outline"
            size="sm"
            leftIcon={<Plus size={14} />}
            onClick={() => append(defaultLeadership)}
          >
            Add
          </AppButton>
        </div>

        {fields.length === 0 && (
          <div className="text-center py-6 text-text-muted text-sm border-2 border-dashed border-warm-border rounded-xl">
            No leadership or volunteering roles added. (Optional)
          </div>
        )}

        {fields.map((field, i) => {
          const currentlyActive = leaderships[i]?.currently_active;
          const lsSkills = leaderships[i]?.skills_used ?? [];

          return (
            <AppCard key={field.id} variant="outlined" className="relative">
              <button
                type="button"
                onClick={() => remove(i)}
                className="absolute top-4 right-4 p-1.5 rounded-md text-text-muted hover:text-error hover:bg-error/10 transition-colors"
              >
                <Trash2 size={16} />
              </button>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pr-10">
                <AppInput label="Position / Title" placeholder="President / Lead Organizer" {...register(`leaderships.${i}.position`)} required />
                <AppInput label="Organization / Committee" placeholder="Computer Science Club" {...register(`leaderships.${i}.committee_name`)} required />
                
                <AppInput label="Start Date" type="date" {...register(`leaderships.${i}.start_date`)} required />

                <div className="flex flex-col gap-1.5">
                  <AppInput
                    label="End Date"
                    type="date"
                    disabled={currentlyActive}
                    {...register(`leaderships.${i}.end_date`)}
                  />
                  <label className="flex items-center gap-2 cursor-pointer mt-1 font-sans">
                    <input
                      type="checkbox"
                      className="rounded border-warm-border accent-brand-600"
                      checked={currentlyActive ?? false}
                      onChange={(e) =>
                        setValue(`leaderships.${i}.currently_active`, e.target.checked)
                      }
                    />
                    <span className="text-xs text-text-secondary">Currently active in this role</span>
                  </label>
                </div>

                <div className="sm:col-span-2">
                  <TagInput
                    label="Skills Used / Developed"
                    tags={lsSkills}
                    onChange={(tags) => setValue(`leaderships.${i}.skills_used`, tags)}
                    placeholder="Leadership, Public Speaking, Event Planning…"
                  />
                </div>

                <div className="sm:col-span-2">
                  <AppTextarea
                    label="Description"
                    placeholder="Describe your responsibilities and achievements in this role…"
                    {...register(`leaderships.${i}.description`)}
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
            onClick={() => append(defaultLeadership)}
          >
            Add another role
          </AppButton>
        )}
      </div>
    </div>
  );
}
