import { useEffect, useState } from 'react'

import { Button } from '@/components/common/Button'
import { Modal } from '@/components/common/Modal'
import { SelectInput, TextArea, TextInput } from '@/components/common/FormField'
import { createCourse, updateCourse } from '@/services/crmApi'
import type { CourseRecord } from '@/services/crmApi'
import { ApiError } from '@/services/authApi'

const COURSE_CATEGORIES = ['Data Science', 'Artificial Intelligence', 'Programming', 'Business', 'Marketing', 'Finance', 'Computer Science', 'Psychology']
const COURSE_MODES = ['Online', 'Offline', 'Hybrid']
const COURSE_STATUSES = ['active', 'archived']

interface CourseFormModalProps {
  open: boolean
  course: CourseRecord | null
  onClose: () => void
  onSaved: () => void
}

export function CourseFormModal({ open, course, onClose, onSaved }: CourseFormModalProps) {
  const [code, setCode] = useState(course?.code ?? '')
  const [title, setTitle] = useState(course?.title ?? '')
  const [category, setCategory] = useState(course?.category ?? 'Technology')
  const [durationWeeks, setDurationWeeks] = useState(String(course?.duration_weeks ?? 24))
  const [fees, setFees] = useState(String(course?.fees ?? 0))
  const [mode, setMode] = useState('Online')
  const [capacity, setCapacity] = useState('60')
  const [instructor, setInstructor] = useState('')
  const [eligibility, setEligibility] = useState(course?.eligibility ?? '')
  const [description, setDescription] = useState(course?.description ?? '')
  const [status, setStatus] = useState<string>(course?.status ?? 'active')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!open) return
    setCode(course?.code ?? '')
    setTitle(course?.title ?? '')
    setCategory(course?.category ?? 'Technology')
    setDurationWeeks(String(course?.duration_weeks ?? 24))
    setFees(String(course?.fees ?? 0))
    setMode('Online')
    setCapacity('60')
    setInstructor('')
    setEligibility(course?.eligibility ?? '')
    setDescription(course?.description ?? '')
    setStatus(course?.status ?? 'active')
    setErrors({})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, course?.id])

  const submit = async () => {
    const e: Record<string, string> = {}
    if (!code.trim()) e.code = 'Course code is required.'
    if (title.trim().length < 3) e.title = 'Title must be at least 3 characters.'
    const weeks = Number(durationWeeks)
    const fee = Number(fees)
    if (!Number.isFinite(weeks) || weeks <= 0) e.durationWeeks = 'Enter a valid number of weeks.'
    if (!Number.isFinite(fee) || fee < 0) e.fees = 'Enter a valid fee amount.'
    setErrors(e)
    if (Object.keys(e).length > 0) return

    setBusy(true)
    const payload: Record<string, unknown> = {
      code: code.trim().toUpperCase(),
      title: title.trim(),
      category,
      durationWeeks: weeks,
      fees: fee,
      eligibility: eligibility.trim() || null,
      description: description.trim() || null,
      status,
    }
    try {
      if (course) await updateCourse(course.id, payload)
      else await createCourse(payload)
      onSaved()
    } catch (err) {
      setErrors({ form: err instanceof ApiError ? err.message : 'Something went wrong. Please try again.' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={course ? 'Edit Course' : 'Create New Course'}
      description={course ? `Update ${course.title}.` : 'Add a new program to the catalog.'}
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={onClose} disabled={busy}>Cancel</Button>
          <Button variant="primary" size="sm" onClick={submit} disabled={busy}>
            {busy ? 'Saving…' : course ? 'Save changes' : 'Create Course'}
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        {errors.form && (
          <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-[12.5px] font-medium text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300">{errors.form}</p>
        )}
        <div className="grid gap-4 sm:grid-cols-2">
          <TextInput id="course-code" label="Course Code" required value={code} onChange={(e) => setCode(e.target.value)} error={errors.code} placeholder="e.g. DS-101" />
          <TextInput id="course-title" label="Course Name" required value={title} onChange={(e) => setTitle(e.target.value)} error={errors.title} placeholder="e.g. Data Science Fundamentals" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <SelectInput id="course-category" label="Category" options={COURSE_CATEGORIES.map((c) => ({ value: c, label: c }))} value={category} onChange={(e) => setCategory(e.target.value)} />
          <SelectInput id="course-mode" label="Mode" options={COURSE_MODES.map((m) => ({ value: m, label: m }))} value={mode} onChange={(e) => setMode(e.target.value)} />
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <TextInput id="course-duration" label="Duration (weeks)" type="number" min={1} required value={durationWeeks} onChange={(e) => setDurationWeeks(e.target.value)} error={errors.durationWeeks} />
          <TextInput id="course-fees" label="Fee (₹)" type="number" min={0} required value={fees} onChange={(e) => setFees(e.target.value)} error={errors.fees} />
          <TextInput id="course-capacity" label="Capacity" type="number" min={1} value={capacity} onChange={(e) => setCapacity(e.target.value)} placeholder="60" />
        </div>
        <TextInput id="course-instructor" label="Instructor" value={instructor} onChange={(e) => setInstructor(e.target.value)} placeholder="e.g. Dr. Smith" hint="Optional — primary instructor" />
        <TextInput id="course-eligibility" label="Eligibility" value={eligibility} onChange={(e) => setEligibility(e.target.value)} placeholder="e.g. 12th pass with Mathematics" />
        <TextArea id="course-description" label="Description" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Course overview, learning outcomes…" />
        <SelectInput id="course-status" label="Status" options={COURSE_STATUSES.map((s) => ({ value: s, label: s.charAt(0).toUpperCase() + s.slice(1) }))} value={status} onChange={(e) => setStatus(e.target.value)} />
      </div>
    </Modal>
  )
}
