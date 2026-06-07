"use client";
import { useFieldArray, useFormContext } from "react-hook-form";
import { Plus, Trash2, Link } from "lucide-react";
import { Github } from "@/components/primitives/SocialIcons";
import { AppButton } from "@/components/primitives/AppButton";
import { AppInput } from "@/components/primitives/AppInput";
import { AppTextarea } from "@/components/primitives/AppTextarea";
import { TagInput } from "@/components/primitives/TagInput";
import { AppCard } from "@/components/primitives/AppCard";

const defaultProject = {
  title: "", description: "", skills_used: [], github_url: "", deployed_url: "",
};

export function Step4Projects() {
  const { register, watch, setValue, control } = useFormContext();
  const { fields, append, remove } = useFieldArray({ control, name: "projects" });
  const projects = watch("projects") ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-text-main">Projects</h2>
          <p className="text-sm text-text-secondary mt-1">
            Add personal or academic projects that show your skills.
          </p>
        </div>
        <AppButton
          type="button"
          variant="outline"
          size="sm"
          leftIcon={<Plus size={14} />}
          onClick={() => append(defaultProject)}
        >
          Add
        </AppButton>
      </div>

      {fields.length === 0 && (
        <div className="text-center py-8 text-text-muted text-sm border-2 border-dashed border-warm-border rounded-xl">
          No projects added yet. Click &quot;Add&quot; to add your first project.
        </div>
      )}

      {fields.map((field, i) => {
        const skills = projects[i]?.skills_used ?? [];

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
              <AppInput label="Project Title" placeholder="E-Commerce API" {...register(`projects.${i}.title`)} required />
              <div className="sm:col-span-2">
                <AppTextarea label="Description" placeholder="Describe the project goals, implementation, and your contributions…" {...register(`projects.${i}.description`)} required />
              </div>
              <AppInput label="GitHub URL" placeholder="github.com/username/project" prefixIcon={<Github size={16} />} hint="Without https://" {...register(`projects.${i}.github_url`)} />
              <AppInput label="Deployed / Demo URL" placeholder="project-demo.com" prefixIcon={<Link size={16} />} hint="Without https://" {...register(`projects.${i}.deployed_url`)} />
              
              <div className="sm:col-span-2">
                <TagInput
                  label="Skills Used"
                  tags={skills}
                  onChange={(tags) => setValue(`projects.${i}.skills_used`, tags)}
                  placeholder="React, Express, PostgreSQL…"
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
          onClick={() => append(defaultProject)}
        >
          Add another project
        </AppButton>
      )}
    </div>
  );
}
