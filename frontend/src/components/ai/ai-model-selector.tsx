'use client';

import { useState, useEffect, useMemo } from 'react';
import { Lightning } from '@phosphor-icons/react';
import type { ReactNode } from 'react';
import type { ModelItem, ModelTier } from '@/lib/api/ai-api';
import { aiApi } from '@/lib/api/ai-api';
import { MODEL_ICONS, KraitIcon, GroqIcon, getIconByKey } from './ai-model-icons';

/* ─── Fallback models (static, if API fails) ────────────── */

const FALLBACK_MODELS: ModelItem[] = [
  { id: 'openai/gpt-oss-120b', name: 'Krait · Groq', tier: 'groq', provider: 'groq', backendModel: 'openai/gpt-oss-120b' },
  { id: 'openai/gpt-oss-20b', name: 'Groq · Fast', tier: 'groq', provider: 'groq', backendModel: 'openai/gpt-oss-20b' },
];

/* ─── Group config ──────────────────────────────────────── */

const GROUP_ORDER: { tier: ModelTier; label: string; icon: ReactNode }[] = [
  { tier: 'kraivor', label: 'Kraivor AI', icon: null },
  { tier: 'groq', label: 'Groq', icon: null },
  { tier: 'free', label: 'Free Models', icon: null },
  { tier: 'byok', label: 'BYOK Models', icon: null },
];

/* ─── Component props ───────────────────────────────────── */

export interface ModelSelectorProps {
  selected: string;
  onSelect: (id: string) => void;
  models?: ModelItem[];
}

/* ─── Component ────────────────────────────────────────── */

export function ModelSelector({ selected, onSelect, models: modelsProp }: ModelSelectorProps) {
  const [fetchedModels, setFetchedModels] = useState<ModelItem[] | null>(null);
  const [loading, setLoading] = useState(!modelsProp);

  useEffect(() => {
    if (modelsProp) return;
    let cancelled = false;
    setLoading(true);
    aiApi
      .listModels()
      .then(data => {
        if (!cancelled) setFetchedModels(data.models);
      })
      .catch(() => {
        if (!cancelled) setFetchedModels(FALLBACK_MODELS);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [modelsProp]);

  const allModels = (Array.isArray(modelsProp) && modelsProp.length > 0)
    ? modelsProp
    : Array.isArray(fetchedModels) && fetchedModels.length > 0
      ? fetchedModels
      : FALLBACK_MODELS;

  const grouped = useMemo(() => {
    const map = new Map<ModelTier, ModelItem[]>();
    for (const m of allModels) {
      const arr = map.get(m.tier) ?? [];
      arr.push(m);
      map.set(m.tier, arr);
    }
    return map;
  }, [allModels]);

  if (loading) {
    return (
      <div className="w-64 bg-[#18181C] border border-[#27272A] rounded-xl shadow-2xl p-4 flex items-center justify-center">
        <span className="text-[12px] text-[#5e5e72] animate-pulse">Loading models...</span>
      </div>
    );
  }

  let hasPrev = false;

  return (
    <div
      className="w-64 bg-[#18181C] border border-[#27272A] rounded-xl shadow-2xl pointer-events-auto"
      onPointerDown={e => e.stopPropagation()}
    >
      <div className="max-h-[400px] overflow-y-auto overflow-x-clip p-0">
        {GROUP_ORDER.map(({ tier, label, icon: groupIcon }) => {
          const models = grouped.get(tier);
          if (!models || models.length === 0) return null;

          if (hasPrev) {
            return (
              <div key={tier}>
                <div className="border-t border-[#27272A] mx-3 mt-1.5" />
                <GroupHeader label={label} icon={groupIcon} tier={tier} />
                <div>
                  {models.map(m => (
                    <ModelRow key={m.id} model={m} selected={selected} onSelect={onSelect} />
                  ))}
                </div>
              </div>
            );
          }

          hasPrev = true;
          return (
            <div key={tier}>
              <GroupHeader label={label} icon={groupIcon} tier={tier} />
              <div>
                {models.map(m => (
                  <ModelRow key={m.id} model={m} selected={selected} onSelect={onSelect} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── Group header ──────────────────────────────────────── */

function GroupHeader({ label, icon }: { label: string; icon: ReactNode; tier: ModelTier }) {
  return (
    <div className="flex items-center gap-1.5 px-3 pt-3 pb-1">
      {icon && <span className="w-4 h-4 flex items-center justify-center">{icon}</span>}
      <span className="text-[10px] uppercase tracking-[0.12em] font-medium text-[#5e5e72]">
        {label}
      </span>
    </div>
  );
}

/* ─── Model row ────────────────────────────────────────── */

function ModelRow({
  model,
  selected,
  onSelect,
}: {
  model: ModelItem;
  selected: string;
  onSelect: (id: string) => void;
}) {
  const active = selected === model.id;
  const dbIcon = getIconByKey(model.iconKey, { size: 16, className: 'shrink-0' });
  const iconFn = MODEL_ICONS[model.id];
  const fallbackIcon = iconFn ? iconFn({ size: 16, className: 'shrink-0' }) : null;
  const IconComponent = dbIcon || fallbackIcon;

  return (
    <button
      onPointerDown={e => e.stopPropagation()}
      onClick={() => onSelect(model.id)}
      className={`w-full flex items-center gap-2.5 px-3 py-[7px] text-left transition-all duration-150 ${
        active
          ? 'bg-[#1f1f24] text-venom-yellow'
          : 'text-[#9898a6] hover:bg-[#1f1f24] hover:text-[#f2f2f3]'
      }`}
    >
      <span className="w-4 h-4 flex items-center justify-center shrink-0">
        {IconComponent}
      </span>
      <span className="text-[13px] font-medium flex-1 truncate">{model.name}</span>
    </button>
  );
}

/* ─── Exports (backward compat) ─────────────────────────── */

export function getModelIcon(id: string, models?: ModelItem[]) {
  if (models && models.length > 0) {
    const m = models.find(m => m.id === id);
    if (m?.iconKey) {
      const dbIcon = getIconByKey(m.iconKey, { size: 14, className: 'shrink-0' });
      if (dbIcon) return dbIcon;
    }
  }
  const fn = MODEL_ICONS[id];
  if (fn) return fn();
  return <KraitIcon />;
}

export function getModelName(id: string, models?: ModelItem[]) {
  if (models && models.length > 0) {
    const m = models.find(m => m.id === id);
    if (m?.name) return m.name;
  }
  return id;
}

export function getModelGroup(id: string): ModelTier {
  const m = FALLBACK_MODELS.find(m => m.id === id);
  return m?.tier ?? 'kraivor';
}
