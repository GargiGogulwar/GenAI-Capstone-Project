export function BillingView() {
  return (
    <div className="space-y-4">
      <h2 className="text-base font-semibold text-text-primary">Free access</h2>
      <p className="text-sm text-text-secondary">
        Kraivor is free to use. No subscription or payment details are required.
      </p>
      <p className="text-sm text-text-secondary">
        AI requests are subject to the configured Groq account limits. If a limit is reached, wait and retry.
      </p>
    </div>
  );
}