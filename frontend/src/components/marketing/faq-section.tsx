'use client';

import { useState } from 'react';
import { CaretDown } from '@phosphor-icons/react';

const FAQS = [
  { question: 'Is Kraivor free to use?', answer: 'Yes. No subscription, paid plan, or payment details are required.' },
  { question: 'What can I do with Kraivor?', answer: 'Connect a repository, analyze code, add supporting documents, and ask AI questions grounded in your workspace.' },
  { question: 'Are there AI usage limits?', answer: 'AI requests depend on the configured Groq account limits. When a limit is reached, wait for it to reset and retry.' },
  { question: 'How does background analysis work?', answer: 'Repository analysis runs in background workers. You can follow its progress and open the report when it is ready.' },
];

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="divide-y divide-[var(--krait-border)]">
      {FAQS.map((faq, i) => {
        const isOpen = openIndex === i;
        return (
          <div key={i}>
            <button
              onClick={() => setOpenIndex(isOpen ? null : i)}
              className="flex w-full items-center justify-between py-4 text-left transition-colors"
            >
              <h4 className="text-sm font-medium text-[var(--text-primary)] pr-4">{faq.question}</h4>
              <CaretDown
                size={14}
                weight="bold"
                className={`shrink-0 text-[var(--text-tertiary)] transition-transform ${
                  isOpen ? 'rotate-180' : ''
                }`}
              />
            </button>
            <div className={`overflow-hidden transition-all ${isOpen ? 'max-h-40 pb-4' : 'max-h-0'}`}>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{faq.answer}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
