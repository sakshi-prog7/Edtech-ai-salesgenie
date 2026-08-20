import { useEffect, useState } from 'react'
import { Eye, Pencil, Plus, Trash2, UserPlus, Users } from 'lucide-react'

import { Badge } from '@/components/common/Badge'
import type { BadgeVariant } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import { Card } from '@/components/common/Card'
import { SelectInput } from '@/components/common/FormField'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { Modal } from '@/components/common/Modal'
import { PaginationBar } from '@/components/common/PaginationBar'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/common/ErrorState'
import { SearchInput } from '@/components/ui/SearchInput'
import { Skeleton } from '@/components/common/Skeleton'
import { useApiList } from '@/hooks/useApiList'
import { archiveLead, getLead, listLeads, deleteLead } from '@/services/crmApi'
import type { LeadDetail, LeadRecord } from '@/services/crmApi'
import { ApiError } from '@/services/authApi'
import { cn } from '@/utils/cn'
import { LeadFormModal } from '@/components/leads/LeadFormModal'

const STATUS_VARIANT: Record<string, BadgeVariant> = {
  NEW: 'info',
  CONTACTED: 'brand',
  QUALIFIED: 'success',
  NURTURING: 'warning',
  CONVERTED: 'success',
  LOST: 'danger',
}

const PRIORITY_VARIANT: Record<string, BadgeVariant> = {
  Low: 'neutral',
  Medium: 'warning',
  High: 'danger',
}

const fmtDate = (iso: string | null): string =>
  iso ? new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'

const LEAD_STATUSES = ['NEW', 'CONTACTED', 'QUALIFIED', 'NURTURING', 'CONVERTED', 'LOST']
const LEAD_PRIORITIES = ['Low', 'Medium', 'High']

interface LeadTableProps {
  initialQuery?: string
}

export function LeadTable({ initialQuery }: LeadTableProps) {
  const list = useApiList<LeadRecord>(listLeads, { pageSize: 10 })
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<LeadDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<LeadRecord | null>(null)
  const [archiveTarget, setArchiveTarget] = useState<LeadRecord | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<LeadRecord | null>(null)
  const [busy, setBusy] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    if (initialQuery) list.setSearch(initialQuery)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const openDetail = async (lead: LeadRecord) => {
    setSelectedId(lead.id)
    setDetailLoading(true)
    setDetail(null)
    try {
      setDetail(await getLead(lead.id))
    } catch (err) {
      setDetail(null)
      setFormError(err instanceof ApiError ? err.message : 'Could not load lead details.')
    } finally {
      setDetailLoading(false)
    }
  }

  const closeDetail = () => {
    setSelectedId(null)
    setDetail(null)
  }

  const openCreate = () => {
    setEditing(null)
    setFormError(null)
    setFormOpen(true)
  }

  const openEdit = (lead: LeadRecord) => {
    setEditing(lead)
    setFormError(null)
    setFormOpen(true)
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setBusy(true)
    try {
      await deleteLead(deleteTarget.id)
      setDeleteTarget(null)
      list.refresh()
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Could not delete the lead.')
    } finally {
      setBusy(false)
    }
  }

  const handleArchive = async () => {
    if (!archiveTarget) return
    setBusy(true)
    try {
      await archiveLead(archiveTarget.id)
      setArchiveTarget(null)
      list.refresh()
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Could not archive the lead.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <Card padding={false} className="overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-slate-100 px-4 py-4 sm:flex-row sm:items-center sm:px-5 dark:border-white/10">
          <div className="w-full sm:w-72">
            <SearchInput
              value={list.search}
              onChange={(e) => list.setSearch(e.target.value)}
              placeholder="Search name, email or course…"
              aria-label="Search leads"
            />
          </div>
          <div className="flex flex-wrap items-center gap-2 sm:ml-auto">
            <SelectInput
              id="lead-status-filter"
              label="Status"
              options={[{ value: '', label: 'All statuses' }, ...LEAD_STATUSES.map((s) => ({ value: s, label: s }))]}
              value={list.filters.status ?? ''}
              onChange={(e) => list.setFilter({ status: e.target.value || undefined })}
              className="h-8 w-36 text-[12px]"
            />
            <SelectInput
              id="lead-priority-filter"
              label="Priority"
              options={[{ value: '', label: 'All priorities' }, ...LEAD_PRIORITIES.map((p) => ({ value: p, label: p }))]}
              value={list.filters.priority ?? ''}
              onChange={(e) => list.setFilter({ priority: e.target.value || undefined })}
              className="h-8 w-36 text-[12px]"
            />
            <Button variant="primary" size="sm" onClick={openCreate}>
              <Plus className="h-3.5 w-3.5" />
              Add Lead
            </Button>
          </div>
        </div>

        {list.error ? (
          <div className="p-5">
            <ErrorState message={list.error} onRetry={list.refresh} />
          </div>
        ) : list.loading && list.items.length === 0 ? (
          <Skeleton className="m-5 h-80 rounded-xl" />
        ) : list.items.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No leads found"
            description="Add your first lead or adjust the search and filters."
            className="py-16"
          >
            <Button variant="secondary" size="sm" onClick={openCreate} className="mt-3">
              <Plus className="h-3.5 w-3.5" />
              Add Lead
            </Button>
          </EmptyState>
        ) : (
          <>
            <div className="hidden min-w-0 overflow-x-auto md:block">
              <table className="w-full min-w-[860px] text-left text-[13px]">
                <caption className="sr-only">Leads from the EDTECH AI database</caption>
                <thead>
                  <tr className="border-y border-slate-200 bg-white/[0.02] dark:border-white/10">
                    {['Lead', 'Contact', 'Status', 'Priority', 'Course Interest', 'Engagement', 'Created', ''].map((col) => (
                      <th key={col} scope="col" className="whitespace-nowrap px-5 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {list.items.map((lead) => (
                    <tr key={lead.id} className="transition-colors duration-200 hover:bg-[#FAF7FF] dark:hover:bg-white/[0.04]">
                      <td className="whitespace-nowrap px-5 py-3.5">
                        <p className="font-semibold text-slate-900 dark:text-slate-100">{lead.name}</p>
                        <p className="text-[11px] text-slate-500">{lead.source}</p>
                      </td>
                      <td className="whitespace-nowrap px-5 py-3.5">
                        <p className="text-slate-700 dark:text-slate-300">{lead.email || '—'}</p>
                        <p className="text-[11px] text-slate-500">{lead.phone || ''}</p>
                      </td>
                      <td className="whitespace-nowrap px-5 py-3.5">
                        <Badge variant={STATUS_VARIANT[lead.status] ?? 'neutral'} dot>{lead.status}</Badge>
                      </td>
                      <td className="whitespace-nowrap px-5 py-3.5">
                        <Badge variant={PRIORITY_VARIANT[lead.priority] ?? 'neutral'}>{lead.priority}</Badge>
                      </td>
                      <td className="whitespace-nowrap px-5 py-3.5 text-slate-700 dark:text-slate-300">
                        {lead.course_interest || '—'}
                      </td>
                      <td className="whitespace-nowrap px-5 py-3.5">
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-200 dark:bg-white/10">
                            <div className="h-full rounded-full bg-gradient-to-r from-violet-600 to-purple-400" style={{ width: `${Math.max(0, Math.min(100, lead.engagement))}%` }} />
                          </div>
                          <span className="text-[11.5px] tabular-nums text-slate-600 dark:text-slate-300">{Math.round(lead.engagement)}%</span>
                        </div>
                      </td>
                      <td className="whitespace-nowrap px-5 py-3.5 text-slate-500 dark:text-slate-400">{fmtDate(lead.created_at)}</td>
                      <td className="whitespace-nowrap px-5 py-3.5">
                        <div className="flex items-center justify-end gap-1">
                          <IconAction label="View" onClick={() => openDetail(lead)}><Eye className="h-3.5 w-3.5" /></IconAction>
                          <IconAction label="Edit" onClick={() => openEdit(lead)}><Pencil className="h-3.5 w-3.5" /></IconAction>
                          <IconAction label="Delete" danger onClick={() => setDeleteTarget(lead)}><Trash2 className="h-3.5 w-3.5" /></IconAction>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <ul className="divide-y divide-white/5 md:hidden">
              {list.items.map((lead) => (
                <li key={lead.id} className="px-4 py-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-[13.5px] font-semibold text-slate-900 dark:text-slate-100">{lead.name}</p>
                      <p className="truncate text-[11px] text-slate-500">{lead.email || lead.source}</p>
                    </div>
                    <Badge variant={STATUS_VARIANT[lead.status] ?? 'neutral'}>{lead.status}</Badge>
                  </div>
                  <div className="mt-3 flex items-center gap-2">
                    <Badge variant={PRIORITY_VARIANT[lead.priority] ?? 'neutral'}>{lead.priority}</Badge>
                    <span className="text-[11.5px] text-slate-500">{lead.course_interest || 'No course interest'} · {Math.round(lead.engagement)}% engaged</span>
                  </div>
                  <div className="mt-3 flex gap-2">
                    <Button variant="secondary" size="sm" onClick={() => openDetail(lead)} className="flex-1"><Eye className="h-3.5 w-3.5" /> View</Button>
                    <Button variant="secondary" size="sm" onClick={() => openEdit(lead)}><Pencil className="h-3.5 w-3.5" /></Button>
                  </div>
                </li>
              ))}
            </ul>

            <PaginationBar page={list.page} pages={list.pages} total={list.total} onPage={list.setPage} />
          </>
        )}
      </Card>

      <LeadFormModal
        open={formOpen}
        lead={editing}
        error={formError}
        onClose={() => setFormOpen(false)}
        onSaved={() => { setFormOpen(false); setEditing(null); list.refresh() }}
      />

      <Modal open={selectedId !== null} onClose={closeDetail} title={detail?.lead.name ?? 'Lead details'} size="lg">
        {detailLoading ? (
          <Skeleton className="h-64 rounded-xl" />
        ) : detail ? (
          <LeadDetailView lead={detail.lead} activities={detail.activities} onEdit={() => openEdit(detail.lead)} />
        ) : (
          <p className="text-[13px] text-slate-500">Could not load this lead.</p>
        )}
      </Modal>

      <ConfirmDialog open={archiveTarget !== null} title="Archive this lead?" description={`"${archiveTarget?.name ?? ''}" will be hidden from the default lead list.`} confirmLabel="Archive" busy={busy} onConfirm={handleArchive} onClose={() => setArchiveTarget(null)} />
      <ConfirmDialog open={deleteTarget !== null} title="Delete this lead?" description={`"${deleteTarget?.name ?? ''}" will be permanently removed. This cannot be undone.`} confirmLabel="Delete" busy={busy} onConfirm={handleDelete} onClose={() => setDeleteTarget(null)} />
    </>
  )
}

function IconAction({ label, danger, onClick, children }: { label: string; danger?: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button type="button" onClick={onClick} aria-label={label} title={label}
      className={cn('flex h-7 w-7 items-center justify-center rounded-lg border border-transparent transition-colors',
        danger ? 'text-slate-400 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600' : 'text-slate-400 hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700')}>
      {children}
    </button>
  )
}

function LeadDetailView({ lead, activities, onEdit }: { lead: LeadRecord; activities: LeadDetail['activities']; onEdit: () => void }) {
  const rows: Array<[string, string]> = [
    ['Email', lead.email ?? '—'], ['Phone', lead.phone ?? '—'], ['Source', lead.source],
    ['Course interest', lead.course_interest ?? '—'], ['Status', lead.status], ['Priority', lead.priority],
    ['Engagement', `${Math.round(lead.engagement)}%`], ['Interactions', String(lead.interactions)],
    ['Created', fmtDate(lead.created_at)], ['Last activity', fmtDate(lead.last_activity)],
  ]
  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant={STATUS_VARIANT[lead.status] ?? 'neutral'} dot>{lead.status}</Badge>
            <Badge variant={PRIORITY_VARIANT[lead.priority] ?? 'neutral'}>{lead.priority}</Badge>
          </div>
          {lead.notes && <p className="mt-3 text-[13px] leading-relaxed text-slate-600 dark:text-slate-300">{lead.notes}</p>}
        </div>
        <Button variant="secondary" size="sm" onClick={onEdit}><Pencil className="h-3.5 w-3.5" /> Edit</Button>
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-3">
        {rows.map(([k, v]) => (
          <div key={k}>
            <dt className="text-[10.5px] font-semibold uppercase tracking-wider text-slate-500">{k}</dt>
            <dd className="mt-0.5 truncate text-[12.5px] font-medium text-slate-900 dark:text-slate-100" title={v}>{v}</dd>
          </div>
        ))}
      </dl>
      {lead.score !== null && (
        <div className="rounded-xl border border-indigo-400/20 bg-indigo-50/60 p-4 dark:bg-indigo-500/[0.07]">
          <p className="text-[12px] font-semibold text-indigo-700 dark:text-indigo-300">AI Intent Score: <span className="text-[16px]">{Math.round(lead.score)}</span></p>
          {lead.score_reason && <p className="mt-1 text-[12px] leading-relaxed text-slate-600 dark:text-slate-400">{lead.score_reason}</p>}
        </div>
      )}
      <div>
        <h3 className="mb-2 flex items-center gap-1.5 text-[12.5px] font-semibold text-slate-700 dark:text-slate-200">
          <UserPlus className="h-3.5 w-3.5 text-indigo-500" /> Activity History
        </h3>
        {activities.length === 0 ? (
          <p className="text-[12.5px] text-slate-500">No activity recorded yet.</p>
        ) : (
          <ul className="space-y-2">
            {activities.map((a) => (
              <li key={a.id} className="rounded-lg border border-slate-200 px-3.5 py-2.5 dark:border-white/10">
                <p className="text-[12.5px] text-slate-700 dark:text-slate-300">{a.note}</p>
                <p className="mt-0.5 text-[11px] text-slate-500">{fmtDate(a.created_at)}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
