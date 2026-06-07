"use client";
import { useFieldArray, useFormContext } from "react-hook-form";
import { Plus, Trash2 } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppInput } from "@/components/primitives/AppInput";
import { TagInput } from "@/components/primitives/TagInput";
import { AppCard } from "@/components/primitives/AppCard";

const defaultEducation = {
  institute_name: "", degree: "", grade: "",
  courses: [], start_date: "", end_date: "", currently_studying: false,
};

export function Step3Education() {
  const { register, watch, setValue, control } = useFormContext();
  const { fields, append, remove } = useFieldArray({ control, name: "educations" });
  const educations = watch("educations") ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-text-main">Education</h2>
          <p className="text-sm text-text-secondary mt-1">
            Add your academic background, most recent first.
          </p>
        </div>
        <AppButton
          type="button"
          variant="outline"
          size="sm"
          leftIcon={<Plus size={14} />}
          onClick={() => append(defaultEducation)}
        >
          Add
        </AppButton>
      </div>

      {fields.length === 0 && (
        <div className="text-center py-8 text-text-muted text-sm border-2 border-dashed border-warm-border rounded-xl">
          No education added yet. Click &quot;Add&quot; to add your first degree or school.
        </div>
      )}

      {fields.map((field, i) => {
        const currentlyStudying = educations[i]?.currently_studying;
        const courses = educations[i]?.courses ?? [];

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
              <AppInput label="School / Institute" placeholder="Stanford University" {...register(`educations.${i}.institute_name`)} required />
              <AppInput label="Degree / Field of Study" placeholder="B.S. in Computer Science" {...register(`educations.${i}.degree`)} required />
              <AppInput label="Grade / GPA" placeholder="3.8 / 4.0 or 85%" {...register(`educations.${i}.grade`)} />

              <AppInput label="Start Date" type="date" {...register(`educations.${i}.start_date`)} required />

              <div className="flex flex-col gap-1.5">
                <AppInput
                  label="End Date"
                  type="date"
                  disabled={currentlyStudying}
                  {...register(`educations.${i}.end_date`)}
                />
                <label className="flex items-center gap-2 cursor-pointer mt-1">
                  <input
                    type="checkbox"
                    className="rounded border-warm-border accent-brand-600"
                    checked={currentlyStudying ?? false}
                    onChange={(e) =>
                      setValue(`educations.${i}.currently_studying`, e.target.checked)
                    }
                  />
                  <span className="text-xs text-text-secondary">Currently studying here</span>
                </label>
              </div>

              <div className="sm:col-span-2">
                <TagInput
                  label="Relevant Courses"
                  tags={courses}
                  onChange={(tags) => setValue(`educations.${i}.courses`, tags)}
                  placeholder="Algorithms, Database Systems, Web Development…"
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
          onClick={() => append(defaultEducation)}
        >
          Add another education
        </AppButton>
      )}
    </div>
  );
}
