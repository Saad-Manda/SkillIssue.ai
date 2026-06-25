"use client";

import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { Dialog, DialogPortal, DialogOverlay, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { AppButton } from "./AppButton";
import { CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface InterviewCompleteModalProps {
  open: boolean;
  onNavigate: () => void;
}

const CustomDialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-md translate-x-[-50%] translate-y-[-50%] gap-6 border bg-white p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-2xl border-warm-border",
        className
      )}
      onPointerDownOutside={(e) => e.preventDefault()}
      onEscapeKeyDown={(e) => e.preventDefault()}
      {...props}
    >
      {children}
    </DialogPrimitive.Content>
  </DialogPortal>
));
CustomDialogContent.displayName = "CustomDialogContent";

export function InterviewCompleteModal({ open, onNavigate }: InterviewCompleteModalProps) {
  return (
    <Dialog open={open}>
      <CustomDialogContent>
        <DialogHeader className="flex flex-col items-center text-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-50 border border-green-100">
            <CheckCircle2 size={32} className="text-green-600 animate-pulse" />
          </div>
          <div className="space-y-2">
            <DialogTitle className="text-xl font-bold text-text-main">
              Interview Complete!
            </DialogTitle>
            <DialogDescription className="text-text-secondary text-sm max-w-xs">
              All topics and phases have been successfully covered. Your readiness report is ready.
            </DialogDescription>
          </div>
        </DialogHeader>
        <DialogFooter className="sm:justify-center">
          <AppButton
            variant="brand"
            size="lg"
            className="w-full sm:max-w-xs"
            onClick={onNavigate}
          >
            View Report →
          </AppButton>
        </DialogFooter>
      </CustomDialogContent>
    </Dialog>
  );
}
