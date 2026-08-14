"use client";
import { useFormContext } from "react-hook-form";
import { AppInput } from "@/components/primitives/AppInput";
import { TagInput } from "@/components/primitives/TagInput";
import { Phone, User } from "lucide-react";
import { Github, Linkedin } from "@/components/primitives/SocialIcons";

export function Step1BasicInfo() {
  const { register, watch, setValue, formState: { errors } } = useFormContext();
  const skills = watch("skills") as string[];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-main">Basic Information</h2>
        <p className="text-sm text-text-secondary mt-1">
          Your name, contact details, and top skills.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <AppInput
          label="Full Name"
          placeholder="John Doe"
          autoComplete="name"
          prefixIcon={<User size={16} />}
          error={errors.name?.message as string}
          {...register("name")}
          required
        />
        <AppInput
          label="Mobile"
          type="tel"
          placeholder="+1 (555) 000-0000"
          autoComplete="tel"
          prefixIcon={<Phone size={16} />}
          error={errors.mobile?.message as string}
          {...register("mobile")}
        />
        <AppInput
          label="GitHub URL"
          placeholder="github.com/username"
          prefixIcon={<Github size={16} />}
          hint="Without https://"
          error={errors.github_url?.message as string}
          {...register("github_url")}
        />
        <AppInput
          label="LinkedIn URL"
          placeholder="linkedin.com/in/username"
          prefixIcon={<Linkedin size={16} />}
          hint="Without https://"
          error={errors.linkedin_url?.message as string}
          {...register("linkedin_url")}
        />
      </div>

      <TagInput
        label="Top Skills"
        hint="Type a skill and press Enter. These are used to tailor interview questions."
        tags={skills ?? []}
        onChange={(tags) => setValue("skills", tags, { shouldValidate: true })}
        placeholder="e.g. Python, System Design, React…"
        error={errors.skills?.message as string}
      />
    </div>
  );
}
