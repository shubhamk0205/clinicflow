import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = '/api/appointments';
const STATUSES = ['SCHEDULED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED'];
const DEPARTMENTS = ['GENERAL', 'CARDIOLOGY', 'DERMATOLOGY', 'PEDIATRICS', 'ORTHOPEDICS'];
const NEXT_STATUS = { SCHEDULED: 'CHECKED_IN', CHECKED_IN: 'COMPLETED' };

const label = (s) => s.charAt(0) + s.slice(1).toLowerCase().replace('_', ' ');
const today = () =>
  new Date().toLocaleDateString([], { weekday: 'long', day: 'numeric', month: 'long' }).toUpperCase();
const formatTime = (iso) =>
  new Date(iso).toLocaleString([], { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });

function App() {
  const [appointments, setAppointments] = useState([]);
  const [stats, setStats] = useState({ total: 0, scheduled: 0, checkedIn: 0, completed: 0, cancelled: 0 });
  const [filter, setFilter] = useState('ALL');
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      setError('');
      const [a, s] = await Promise.all([fetch(API), fetch(`${API}/stats`)]);
      if (!a.ok || !s.ok) throw Error('Backend unavailable');
      setAppointments(await a.json());
      setStats(await s.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const setStatus = async (appt, status) => {
    await fetch(`${API}/${appt.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    load();
  };

  const remove = async (appt) => {
    await fetch(`${API}/${appt.id}`, { method: 'DELETE' });
    load();
  };

  const create = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const f = new FormData(form);
    const res = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_name: f.get('patient_name'),
        patient_phone: f.get('patient_phone'),
        doctor: f.get('doctor'),
        department: f.get('department'),
        scheduled_at: new Date(f.get('scheduled_at')).toISOString(),
        reason: f.get('reason'),
      }),
    });
    if (!res.ok) { setError('Could not book appointment'); return; }
    form.reset();
    setShowForm(false);
    load();
  };

  const visible = filter === 'ALL' ? appointments : appointments.filter((a) => a.status === filter);
  const upcoming = appointments.filter((a) => a.status === 'SCHEDULED' || a.status === 'CHECKED_IN').slice(0, 4);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">✚</span>
          <div><b>ClinicFlow</b><small>Appointment desk</small></div>
        </div>
        <nav>
          <a className="active">▦ <span>Dashboard</span></a>
          <a>◷ <span>Appointments</span></a>
          <a>☺ <span>Patients</span></a>
          <a>⚕ <span>Doctors</span></a>
        </nav>
        <div className="side-bottom">
          <div className="profile">
            <div className="avatar">SK</div>
            <div><b>Shubham Kapoor</b><small>Front desk admin</small></div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header>
          <div>
            <p className="eyebrow">CLINIC / {today()}</p>
            <h1>Appointments overview</h1>
            <p className="muted">Book, check in and complete patient visits.</p>
          </div>
          <button className="primary" onClick={() => setShowForm(true)}>＋ Book appointment</button>
        </header>

        {error && <div className="alert">⚠ {error}. Make sure the backend and PostgreSQL are running, then refresh.</div>}

        <section className="stats">
          <Stat label="Total" value={stats.total} tone="neutral" />
          <Stat label="Scheduled" value={stats.scheduled} tone="scheduled" />
          <Stat label="Checked in" value={stats.checkedIn} tone="checked_in" />
          <Stat label="Completed" value={stats.completed} tone="completed" />
          <Stat label="Cancelled" value={stats.cancelled} tone="cancelled" />
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-head">
              <h2>Appointments</h2>
              <div className="filters">
                {['ALL', ...STATUSES].map((s) => (
                  <button key={s} className={filter === s ? 'selected' : ''} onClick={() => setFilter(s)}>
                    {s === 'ALL' ? 'All' : label(s)}
                  </button>
                ))}
              </div>
            </div>
            {loading ? (
              <div className="empty">Loading appointments…</div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr><th>Patient</th><th>Doctor</th><th>Department</th><th>When</th><th>Status</th><th></th></tr>
                  </thead>
                  <tbody>
                    {visible.map((a) => (
                      <tr key={a.id}>
                        <td><b>{a.patient_name}</b><small>{a.reason || a.patient_phone}</small></td>
                        <td>{a.doctor}</td>
                        <td><span className="dept">{label(a.department)}</span></td>
                        <td>{formatTime(a.scheduled_at)}</td>
                        <td><span className={`status ${a.status.toLowerCase()}`}>{label(a.status)}</span></td>
                        <td>
                          <div className="actions">
                            {NEXT_STATUS[a.status] && (
                              <button className="small" onClick={() => setStatus(a, NEXT_STATUS[a.status])}>
                                {a.status === 'SCHEDULED' ? 'Check in' : 'Complete'}
                              </button>
                            )}
                            {a.status === 'SCHEDULED' && (
                              <button className="small ghost" onClick={() => setStatus(a, 'CANCELLED')}>Cancel</button>
                            )}
                            <button className="icon-btn" title="Delete" onClick={() => remove(a)}>✕</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {!visible.length && <div className="empty">No appointments here.</div>}
              </div>
            )}
          </div>

          <aside className="panel">
            <div className="panel-head"><h2>Up next</h2></div>
            {upcoming.length ? upcoming.map((a) => (
              <div className="queue-row" key={a.id}>
                <span className={`dot ${a.status.toLowerCase()}`}></span>
                <div><b>{a.patient_name}</b><small>{a.doctor} · {formatTime(a.scheduled_at)}</small></div>
              </div>
            )) : <div className="empty">Queue is empty.</div>}
          </aside>
        </section>

        {showForm && (
          <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && setShowForm(false)}>
            <form className="modal" onSubmit={create}>
              <div className="modal-head">
                <h2>Book appointment</h2>
                <button type="button" className="close" onClick={() => setShowForm(false)}>×</button>
              </div>
              <div className="form-row">
                <label>Patient name<input name="patient_name" required placeholder="e.g. Priya Verma" /></label>
                <label>Phone<input name="patient_phone" placeholder="98xxxxxxxx" /></label>
              </div>
              <div className="form-row">
                <label>Doctor<input name="doctor" required placeholder="e.g. Dr. Mehta" /></label>
                <label>Department
                  <select name="department">{DEPARTMENTS.map((d) => <option key={d} value={d}>{label(d)}</option>)}</select>
                </label>
              </div>
              <label>Date &amp; time<input name="scheduled_at" type="datetime-local" required /></label>
              <label>Reason for visit<textarea name="reason" placeholder="Symptoms or purpose of visit" /></label>
              <button className="primary full">Book appointment</button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}

function Stat({ label, value, tone }) {
  return (
    <div className={`stat ${tone}`}>
      <small>{label}</small>
      <strong>{value}</strong>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
