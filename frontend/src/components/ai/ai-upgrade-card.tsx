'use client';

export function UpgradeCard({ show }: { show: boolean }) {
  if (!show) return null;
  return (
    <div role="status" className="mx-auto my-6 max-w-lg rounded-xl border border-border p-6 text-sm text-text-secondary">
      Groq usage limit reached. Wait for the limit to reset, then retry. Both models share the server Groq key and its account limits.
    </div>
  );
}
