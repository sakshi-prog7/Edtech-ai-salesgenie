import { useEffect } from 'react'
import { CalendarClock, Sparkles, X } from 'lucide-react'

import { Avatar } from '@/components/common/Avatar'
import { Badge } from '@/components/common/Badge'
import type { BadgeVariant } from '@/components/common/Badge'
import { IconButton } from '@/components/common/IconButton'
import { IntentBadge, ScoreCell, nextBestAction } from '@/components/leads/LeadScore'
import { cn } from '@/utils/cn'
import type { RecentLead, RecentLeadStatus } from '@/types/dashboard'

const statusVariants: Record<RecentLeadStatus, BadgeVariant> = {
  New: 'neutral',
  Contacted: 'info',
  Qualified: 'brand',
  'Follow-up': 'warning',
  Converted: 'success',
}

interface LeadDetailDrawerProps {
  lead: RecentLead | null
  onClose: () => void
}

export function LeadDetailDrawer({ lead, onClose }: LeadDetailDrawerProps) {
  useEffect(() => {
    if (!lead) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [lead, onClose])

  const action = lead ? nextBestAction(lead.score) : null

  return (
    <div
      className={cn('fixed inset-0 z-50', !lead && 'pointer-events-none')}
      inert={!lead}
      aria-hidden={!lead}
    >
      {/* Backdrop */}
      <div
        className={cn(
          'absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity duration-200',
          lead ? 'opacity-100' : 'opacity-0',
        )}
        onClick={onClose}
      />

      {/* Panel */}
      <aside
        role="dialog"
        aria-modal="true"
        aria-label={lead ? `Lead details: ${lead.name}` : 'Lead details'}
        className={cn(
          'absolute inset-y-0 right-0 flex w-full max-w-md flex-col overflow-y-auto border-l border-slate-200 dark:border-white/10 bg-navy-900 shadow-2xl shadow-black/50 transition-transform duration-300',
          lead ? 'translate-x-0' : 'translate-x-full',
        )}
      >
        {lead && (
          <>
            <div className="flex items-start justify-between gap-3 border-b border-slate-200 dark:border-white/10 p-5">
              <div className="flex items-center gap-3.5">
                <Avatar name={lead.name} size="lg" />
                <div className="leading-tight">
                  <h2 className="text-lg font-semibold tracking-tight text-white">{lead.name}</h2>
                  <div className="mt-1.5">
                    <Badge variant={statusVariants[lead.status]} dot>
                      {lead.status}
                    </Badge>
                  </div>
                </div>
              </div>
              <IconButton label="Close lead details" onClick={onClose}>
                <X className="h-5 w-5" />
              </IconButton>
            </div>

            {/* AI intelligence */}
            <div className="relative m-5 overflow-hidden rounded-2xl border border-indigo-400/20 bg-gradient-to-br from-indigo-500/10 via-transparent to-purple-500/10 p-5">
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 rounded-2xl bg-[radial-gradient(120%_100%_at_100%_0%,rgba(124,92,255,0.14),transparent_55%)]"
              />
              <div className="relative">
                <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[0.24em] text-indigo-300">
                  <Sparkles className="h-3 w-3" />
                  AI Intelligence
                </p>
                <div className="mt-4 flex items-center justify-between gap-4">
                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                      AI Lead Score
                    </p>
                    <div className="mt-1.5">
                      <ScoreCell score={lead.score} large onDark />
                    </div>
                  </div>
                  <IntentBadge score={lead.score} onDark />
                </div>
                <div className="mt-5 flex items-start gap-2.5 rounded-xl border border-slate-200 dark:border-white/10 bg-white/[0.03] px-3.5 py-3">
                  {action && <action.icon className="mt-0.5 h-4 w-4 shrink-0 text-indigo-300" />}
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                      Recommended action
                    </p>
                    <p className="mt-0.5 text-[13px] leading-snug text-slate-800 dark:text-slate-200">{action?.text}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Lead information */}
            <div className="mx-5 mb-5">
              <h3 className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                Lead Information
              </h3>
              <dl className="mt-3 space-y-3">
                <div className="flex items-center justify-between gap-4 text-[13px]">
                  <dt className="text-slate-500">Course Interest</dt>
                  <dd className="font-medium text-slate-100">{lead.course}</dd>
                </div>
                <div className="flex items-center justify-between gap-4 text-[13px]">
                  <dt className="text-slate-500">Source</dt>
                  <dd className="font-medium text-slate-100">{lead.source}</dd>
                </div>
                <div className="flex items-center justify-between gap-4 text-[13px]">
                  <dt className="text-slate-500">Status</dt>
                  <dd className="font-medium text-slate-100">{lead.status}</dd>
                </div>
                <div className="flex items-center justify-between gap-4 text-[13px]">
                  <dt className="text-slate-500">Last Activity</dt>
                  <dd className="flex items-center gap-1.5 font-medium text-slate-100">
                    <CalendarClock className="h-3.5 w-3.5 text-slate-500" />
                    {lead.lastActivity}
                  </dd>
                </div>
              </dl>
            </div>
          </>
        )}
      </aside>
    </div>
  )
}
