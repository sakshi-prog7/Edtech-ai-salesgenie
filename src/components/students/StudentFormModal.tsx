import { useEffect, useState } from 'react'

import { Button } from '@/components/common/Button'
import { Modal } from '@/components/common/Modal'
import { SelectInput, TextArea, TextInput } from '@/components/common/FormField'
import { createStudent, updateStudent, listCounselors } from '@/services/crmApi'
import type { StudentRecord, CounselorUser } from '@/services/crmApi'
import { ApiError } from '@/services/authApi'

const ACADEMIC_LEVELS = ['Bachelor (12th pass)', 'Bachelor degree', 'Master degree', 'Working professional']
const ADMISSION_STATUSES = ['Not Applied', 'Application Submitted', 'Under Review', 'Accepted', 'Waitlisted', 'Rejected', 'Enrolled']
const COURSE_OPTIONS = ['Data Science', 'AI & ML', 'Business Analytics', 'Digital Marketing', 'Cybersecurity', 'Cloud Computing', 'Full Stack Development', 'Other']

interface StudentFormModalProps {
  open: boolean
  student: StudentRecord | null
  onClose: () => void
  onSaved: () => void
}

export function StudentFormModal({ open, student, onClose, onSaved }: StudentFormModalProps) {
  const [name, setName] = useState(student?.name ?? '')
  const [email, setEmail] = useState(student?.email ?? '')
  const [phone, setPhone] = useState(student?.phone ?? '')
  const [academicLevel, setAcademicLevel] = useState(student?.academic_level ?? 'Bachelor (12th pass)')
  const [interests, setInterests] = useState(student?.interests ?? '')
  const [admissionStatus, setAdmissionStatus] = useState('Not Applied')
  const [counselorId, setCounselorId] = useState('')
  const [notes, setNotes] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)
  const [counselors, setCounselors] = useState<CounselorUser[]>([])

  useEffect(() => {
    if (!open) return
    listCounselors().then((res) => setCounselors(res.users)).catch(() => {})
    setName(student?.name ?? '')
    setEmail(student?.email ?? '')
    setPhone(student?.phone ?? '')
    setAcademicLevel(student?.academic_level ?? 'Bachelor (12th pass)')
    setInterests(student?.interests ?? '')
    setAdmissionStatus('Not Applied')
    setCounselorId('')
    setNotes('')
    setErrors({})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, student?.id])

  const submit = async () => {
    const e: Record<string, string> = {}
    if (name.trim().length < 2) e.name = 'Name must be at least 2 characters.'
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) e.email = 'Enter a valid email address.'
    setErrors(e)
    if (Object.keys(e).length > 0) return

    setBusy(true)
    const payload: Record<string, unknown> = {
      name: name.trim(),
      email: email.trim() || null,
      phone: phone.trim() || null,
      academicLevel: academicLevel || null,
      interests: interests.trim() || null,
    }
    try {
      if (student) await updateStudent(student.id, payload)
      else await createStudent(payload)
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
      title={student ? 'Edit Student' : 'Create New Student'}
      description={student ? `Update ${student.name}'s profile.` : 'Add a new student to the system.'}
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={onClose} disabled={busy}>Cancel</Button>
          <Button variant="primary" size="sm" onClick={submit} disabled={busy}>
            {busy ? 'Saving…' : student ? 'Save changes' : 'Create Student'}
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        {errors.form && (
          <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-[12.5px] font-medium text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300">
            {errors.form}
          </p>
        )}
        <TextInput id="student-name" label="Student Name" required value={name} onChange={(e) => setName(e.target.value)} error={errors.name} placeholder="e.g. Ananya Gupta" />
        <div className="grid gap-4 sm:grid-cols-2">
          <TextInput id="student-email" label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} error={errors.email} placeholder="student@example.edu" />
          <TextInput id="student-phone" label="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91 …" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <TextInput id="student-dob" label="Date of Birth" type="date" hint="Optional" />
          <TextInput id="student-location" label="Location" placeholder="e.g. Mumbai, India" hint="Optional" />
        </div>
        <SelectInput
          id="student-level"
          label="Education Level"
          options={ACADEMIC_LEVELS.map((l) => ({ value: l, label: l }))}
          value={academicLevel}
          onChange={(e) => setAcademicLevel(e.target.value)}
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <SelectInput
            id="student-course"
            label="Interested Course"
            options={[{ value: '', label: 'Select course…' }, ...COURSE_OPTIONS.map((c) => ({ value: c, label: c }))]}
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
          />
          <SelectInput
            id="student-admission-status"
            label="Admission Status"
            options={ADMISSION_STATUSES.map((s) => ({ value: s, label: s }))}
            value={admissionStatus}
            onChange={(e) => setAdmissionStatus(e.target.value)}
          />
        </div>
        <SelectInput
          id="student-counselor"
          label="Assigned Counselor"
          options={[{ value: '', label: 'Select counselor…' }, ...counselors.map((c) => ({ value: c.id, label: `${c.name} (${c.role})` }))]}
          value={counselorId}
          onChange={(e) => setCounselorId(e.target.value)}
          hint="Optional — assign a counselor for this student"
        />
        <TextArea id="student-notes" label="Notes" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Academic background, special requirements…" />
      </div>
    </Modal>
  )
}
