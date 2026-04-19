import streamlit as st
import pandas as pd
import json
import io
import calendar
from datetime import date, datetime
from copy import deepcopy

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="IASL Crew Planning Portal",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Source+Sans+3:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
}

h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2 {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 0.04em;
}

/* Header strip */
.iasl-header {
    background: linear-gradient(135deg, #0a1628 0%, #112240 60%, #1a3a5c 100%);
    border-bottom: 3px solid #00b4d8;
    padding: 18px 32px;
    border-radius: 8px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.iasl-logo-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #00b4d8;
    letter-spacing: 0.12em;
}
.iasl-subtitle {
    font-size: 0.8rem;
    color: #8ecae6;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: -4px;
}
.iasl-stat-chip {
    background: rgba(0,180,216,0.12);
    border: 1px solid rgba(0,180,216,0.35);
    border-radius: 20px;
    padding: 4px 14px;
    color: #90e0ef;
    font-size: 0.82rem;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    letter-spacing: 0.06em;
    display: inline-block;
    margin: 2px 4px;
}

/* Summary cards */
.summary-card {
    background: linear-gradient(135deg, #112240, #0d1b2a);
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 14px 18px;
    text-align: center;
}
.summary-card .val {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #00b4d8;
    line-height: 1;
}
.summary-card .lbl {
    font-size: 0.78rem;
    color: #8ecae6;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 4px;
}

/* Gap cells */
.cell-ok   { background:#1a3a2a; color:#4ade80; border-radius:4px; padding:3px 8px; font-weight:600; font-size:0.82rem; }
.cell-warn { background:#3a2a0a; color:#fbbf24; border-radius:4px; padding:3px 8px; font-weight:600; font-size:0.82rem; }
.cell-crit { background:#3a0a0a; color:#f87171; border-radius:4px; padding:3px 8px; font-weight:600; font-size:0.82rem; }
.cell-over { background:#0a1a3a; color:#93c5fd; border-radius:4px; padding:3px 8px; font-weight:600; font-size:0.82rem; }

/* Conflict badge */
.conflict-badge {
    background: #7f1d1d;
    border: 1px solid #ef4444;
    border-radius: 6px;
    padding: 8px 14px;
    color: #fca5a5;
    font-size: 0.85rem;
    margin: 6px 0;
}

/* Cascade badge */
.cascade-badge {
    background: #172554;
    border-left: 3px solid #3b82f6;
    border-radius: 0 6px 6px 0;
    padding: 8px 14px;
    color: #93c5fd;
    font-size: 0.85rem;
    margin: 4px 0;
}

/* Section headers */
.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #00b4d8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 6px;
    margin: 18px 0 12px 0;
}

/* Tab style override */
.stTabs [data-baseweb="tab-list"] {
    background: #0a1628;
    border-radius: 8px 8px 0 0;
    gap: 4px;
    padding: 6px 6px 0 6px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #8ecae6;
    border-radius: 6px 6px 0 0;
    padding: 8px 24px;
    background: transparent;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #112240 !important;
    color: #00b4d8 !important;
    border-top: 2px solid #00b4d8 !important;
}

/* Dataframe tweaks */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* Expander */
.streamlit-expanderHeader {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    color: #8ecae6;
    letter-spacing: 0.06em;
}

/* Progress bar labels */
.prog-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: #8ecae6;
    margin-bottom: 2px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
FLEETS = ["A330", "A320", "ATR 72", "DHC-8"]
FUNCTIONS = ["Captain", "First Officer"]
DESIGNATIONS = ["TRE", "TRI", "LI"]
PILOT_TYPES = ["Local", "Expat"]
STATUSES = ["Active", "On Type Rating", "On Leave"]
ACTION_TYPES = ["Fleet Change", "Type Rating", "Command Upgrade", "Cadet Hire", "Expat Hire"]
TR_MODES = ["Internal", "External"]

# Required crew sets per fleet (CPT count = FO count = sets)
FLEET_CONFIG = {
    "A330":  {"sets_per_ac": 7, "aircraft": 1, "phase_out": False},
    "A320":  {"sets_per_ac": 5, "aircraft": 1, "phase_out": False},
    "ATR 72":{"sets_per_ac": 6, "aircraft": 5, "phase_out": False},
    "DHC-8": {"sets_per_ac": 5, "aircraft": 3, "phase_out": True},
}

# Training durations in months
TRANSITION_RULES = {
    ("DHC-8",  "Captain",       "ATR 72", "Captain"):       2,
    ("DHC-8",  "First Officer", "ATR 72", "First Officer"): 2,
    ("ATR 72", "Captain",       "A320",   "First Officer"): 2,
    ("ATR 72", "First Officer", "A320",   "First Officer"): 2,
    ("DHC-8",  "Captain",       "A320",   "First Officer"): 2,
    ("DHC-8",  "First Officer", "A320",   "First Officer"): 2,
    ("A320",   "First Officer", "A330",   "First Officer"): 1,
    ("A320",   "Captain",       "A330",   "Captain"):       1,   # command upgrade eligible
}
COMMAND_UPGRADE_DURATION = 1   # months

MONTHS_SHORT = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    if "pilots" not in st.session_state:
        st.session_state.pilots = []          # list of dicts
    if "actions" not in st.session_state:
        st.session_state.actions = []         # list of dicts
    if "plan_start" not in st.session_state:
        today = date.today()
        st.session_state.plan_start = (today.month, today.year)
    if "plan_end" not in st.session_state:
        today = date.today()
        end_year = today.year + 1
        st.session_state.plan_end = (today.month, end_year)
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1

init_state()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def get_required_sets(fleet):
    cfg = FLEET_CONFIG[fleet]
    return cfg["sets_per_ac"] * cfg["aircraft"]

def month_range(start_m, start_y, end_m, end_y):
    """Return list of (month, year) tuples inclusive."""
    result = []
    m, y = start_m, start_y
    while (y < end_y) or (y == end_y and m <= end_m):
        result.append((m, y))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return result

def months_between(m1, y1, m2, y2):
    """Number of months from (m1,y1) to (m2,y2) inclusive."""
    return (y2 - y1) * 12 + (m2 - m1) + 1

def add_months(m, y, n):
    """Add n months to (m, y)."""
    total = (y * 12 + m - 1) + n
    return (total % 12) + 1, total // 12

def action_months(action):
    """Return list of (month, year) that action is active."""
    sm, sy = action["start_month"], action["start_year"]
    dur = action.get("duration_months", 1)
    em, ey = add_months(sm, sy, dur - 1)
    return month_range(sm, sy, em, ey)

def pilot_name_by_id(pid):
    for p in st.session_state.pilots:
        if p["id"] == pid:
            return p["name"]
    return str(pid)

def pilots_for_fleet_func(fleet, func):
    return [p for p in st.session_state.pilots if p["fleet"] == fleet and p["function"] == func]

def active_pilots_in_month(fleet, func, month, year):
    """Count pilots on a fleet+function that are active in a given month."""
    count = 0
    for p in st.session_state.pilots:
        if p["fleet"] != fleet or p["function"] != func:
            continue
        # Check if pilot is tied up in any action during this month
        busy = False
        for a in st.session_state.actions:
            if a.get("trainee1") == p["id"] or a.get("trainee2") == p["id"] or a.get("instructor") == p["id"]:
                if (month, year) in action_months(a):
                    busy = True
                    break
        if not busy:
            count += 1
    return count

def detect_conflicts():
    """Return list of conflict descriptions."""
    conflicts = []
    pilot_action_months = {}  # pilot_id -> list of (month, year, action_label)
    for a in st.session_state.actions:
        a_months = action_months(a)
        label = a.get("label", a["type"])
        for pid_key in ["instructor", "trainee1", "trainee2"]:
            pid = a.get(pid_key)
            if pid and pid != "TBD":
                if pid not in pilot_action_months:
                    pilot_action_months[pid] = []
                for my in a_months:
                    pilot_action_months[pid].append((my[0], my[1], label, a["id"]))

    for pid, entries in pilot_action_months.items():
        # group by month
        month_actions = {}
        for m, y, lbl, aid in entries:
            key = (m, y)
            if key not in month_actions:
                month_actions[key] = []
            month_actions[key].append((lbl, aid))
        for (m, y), acts in month_actions.items():
            unique_ids = list({aid for _, aid in acts})
            if len(unique_ids) > 1:
                pname = pilot_name_by_id(pid)
                conflicts.append(
                    f"⚠ Conflict: {pname} is assigned to multiple actions in "
                    f"{MONTHS_SHORT[m-1]} {y}: {', '.join(set(l for l,_ in acts))}"
                )
    return list(set(conflicts))

def cascade_recommendation(action):
    """Given a command upgrade action, return cascade text."""
    fleet = action.get("fleet", "")
    trainee_id = action.get("trainee1") or action.get("trainee2")
    trainee_name = pilot_name_by_id(trainee_id) if trainee_id and trainee_id != "TBD" else "TBD"
    em, ey = add_months(action["start_month"], action["start_year"], action.get("duration_months", 1))
    month_str = f"{MONTHS_SHORT[em-1]} {ey}"
    rec = (f"When {trainee_name} upgrades to {fleet} Captain in {month_str}, "
           f"the vacated {fleet} FO slot opens. "
           f"Recommended action: recruit or transition a pilot to {fleet} FO "
           f"starting {month_str} (2-month type rating if from ATR/DHC-8, "
           f"1 month if from A320).")
    return rec

def localisation_eligibility():
    """Return list of dicts: expat position + whether a local is eligible."""
    results = []
    for p in st.session_state.pilots:
        if p["type"] != "Expat":
            continue
        fleet = p["fleet"]
        func  = p["function"]
        # Find local pilots that could transition to this slot
        eligible_locals = []
        for lp in st.session_state.pilots:
            if lp["type"] != "Local" or lp["fleet"] == fleet:
                continue
            # Check transition path
            key = (lp["fleet"], lp["function"], fleet, func)
            if key in TRANSITION_RULES:
                eligible_locals.append(lp["name"])
            # Command upgrade path: local FO on same fleet → Captain
            if lp["fleet"] == fleet and lp["function"] == "First Officer" and func == "Captain":
                eligible_locals.append(lp["name"] + " (Cmd Upgrade)")
        results.append({
            "expat_name": p["name"],
            "fleet": fleet,
            "function": func,
            "eligible_locals": eligible_locals,
            "can_localise": len(eligible_locals) > 0,
        })
    return results

def projected_localisation(months):
    """Simple projection: current local% per fleet over planning months (static)."""
    data = {}
    for fleet in FLEETS:
        total = [p for p in st.session_state.pilots if p["fleet"] == fleet]
        local = [p for p in total if p["type"] == "Local"]
        pct = (len(local) / len(total) * 100) if total else 0
        data[fleet] = [round(pct, 1)] * len(months)
    return data

def save_session_json():
    payload = {
        "pilots":      st.session_state.pilots,
        "actions":     st.session_state.actions,
        "plan_start":  list(st.session_state.plan_start),
        "plan_end":    list(st.session_state.plan_end),
        "next_id":     st.session_state.next_id,
    }
    return json.dumps(payload, indent=2).encode("utf-8")

def load_session_json(data_bytes):
    payload = json.loads(data_bytes)
    st.session_state.pilots    = payload.get("pilots", [])
    st.session_state.actions   = payload.get("actions", [])
    st.session_state.plan_start= tuple(payload.get("plan_start", [date.today().month, date.today().year]))
    st.session_state.plan_end  = tuple(payload.get("plan_end",   [date.today().month, date.today().year + 1]))
    st.session_state.next_id   = payload.get("next_id", 1)

def next_id():
    nid = st.session_state.next_id
    st.session_state.next_id += 1
    return nid

# ─────────────────────────────────────────────
#  TOP HEADER
# ─────────────────────────────────────────────
sm, sy = st.session_state.plan_start
em, ey = st.session_state.plan_end
total_ac = sum(c["aircraft"] for c in FLEET_CONFIG.values())
total_pilots = len(st.session_state.pilots)

st.markdown(f"""
<div class="iasl-header">
  <div>
    <div class="iasl-logo-text">✈ IASL</div>
    <div class="iasl-subtitle">Island Aviation Services Limited · Crew Planning Portal</div>
  </div>
  <div style="text-align:right;">
    <span class="iasl-stat-chip">👥 {total_pilots} Pilots</span>
    <span class="iasl-stat-chip">✈ {total_ac} Aircraft</span>
    <span class="iasl-stat-chip">📅 {MONTHS_SHORT[sm-1]} {sy} – {MONTHS_SHORT[em-1]} {ey}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Save / Load row
col_sv, col_ld, col_sp = st.columns([1, 1, 6])
with col_sv:
    st.download_button(
        "💾 Save Session",
        data=save_session_json(),
        file_name="iasl_crew_plan.json",
        mime="application/json",
        use_container_width=True,
    )
with col_ld:
    uploaded_json = st.file_uploader("📂 Load Session", type=["json"], label_visibility="collapsed")
    if uploaded_json:
        load_session_json(uploaded_json.read())
        st.success("Session loaded.")
        st.rerun()

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🗂  Pilot Registry", "📅  Planning Timeline", "🌍  Localisation Tracker"])

# ═══════════════════════════════════════════════════════
#  TAB 1 — PILOT REGISTRY
# ═══════════════════════════════════════════════════════
with tab1:

    # ── Summary bar ───────────────────────────────────
    st.markdown('<div class="section-header">Fleet Summary</div>', unsafe_allow_html=True)
    pilots = st.session_state.pilots
    locals_count = sum(1 for p in pilots if p["type"] == "Local")
    expats_count = sum(1 for p in pilots if p["type"] == "Expat")

    cols = st.columns(6)
    with cols[0]:
        st.markdown(f'<div class="summary-card"><div class="val">{len(pilots)}</div><div class="lbl">Total Pilots</div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="summary-card"><div class="val">{locals_count}</div><div class="lbl">Local</div></div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="summary-card"><div class="val">{expats_count}</div><div class="lbl">Expat</div></div>', unsafe_allow_html=True)
    for i, fleet in enumerate(FLEETS):
        with cols[3 + i] if i < 3 else cols[3]:
            pass
    fleet_cols = st.columns(4)
    for i, fleet in enumerate(FLEETS):
        cnt = sum(1 for p in pilots if p["fleet"] == fleet)
        req = get_required_sets(fleet) * 2
        with fleet_cols[i]:
            st.markdown(f'<div class="summary-card"><div class="val">{cnt}</div><div class="lbl">{fleet}<br><span style="font-size:0.7rem;color:#4ade80;">Req: {req}</span></div></div>', unsafe_allow_html=True)

    st.markdown("")

    # ── Add Pilot Form ─────────────────────────────────
    st.markdown('<div class="section-header">Add Pilot</div>', unsafe_allow_html=True)
    with st.form("add_pilot_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            emp_id    = st.text_input("Employee ID *")
            full_name = st.text_input("Full Name *")
        with c2:
            nat       = st.selectbox("Nationality", PILOT_TYPES)
            fleet_sel = st.selectbox("Fleet", FLEETS)
        with c3:
            func_sel  = st.selectbox("Function", FUNCTIONS)
            status_sel= st.selectbox("Status", STATUSES)
        desig_sel = st.multiselect("Designations", DESIGNATIONS)
        submitted = st.form_submit_button("➕ Add Pilot", use_container_width=True)
        if submitted:
            if not emp_id.strip() or not full_name.strip():
                st.error("Employee ID and Full Name are required.")
            elif any(p["emp_id"] == emp_id.strip() for p in st.session_state.pilots):
                st.error(f"Employee ID '{emp_id}' already exists.")
            else:
                st.session_state.pilots.append({
                    "id":          next_id(),
                    "emp_id":      emp_id.strip(),
                    "name":        full_name.strip(),
                    "type":        nat,
                    "fleet":       fleet_sel,
                    "function":    func_sel,
                    "status":      status_sel,
                    "designations": desig_sel,
                })
                st.success(f"Pilot {full_name} added.")
                st.rerun()

    # ── CSV Bulk Import ────────────────────────────────
    st.markdown('<div class="section-header">Bulk Import via CSV</div>', unsafe_allow_html=True)
    st.markdown("""
**CSV Template format** (headers must match exactly):

`Employee ID, Full Name, Nationality, Fleet, Function, Designations, Status`

- **Nationality**: `Local` or `Expat`
- **Fleet**: `A330`, `A320`, `ATR 72`, `DHC-8`
- **Function**: `Captain` or `First Officer`
- **Designations**: semicolon-separated, e.g. `TRE;TRI` (leave blank if none)
- **Status**: `Active`, `On Type Rating`, `On Leave`
""")
    csv_template = "Employee ID,Full Name,Nationality,Fleet,Function,Designations,Status\nEMP001,Ahmed Rasheed,Local,ATR 72,First Officer,,Active\nEMP002,John Smith,Expat,A320,Captain,TRE,Active\n"
    st.download_button("⬇ Download CSV Template", data=csv_template.encode(), file_name="iasl_pilot_template.csv", mime="text/csv")

    uploaded_csv = st.file_uploader("Upload Pilot CSV", type=["csv"], key="csv_upload")
    if uploaded_csv:
        try:
            df_csv = pd.read_csv(uploaded_csv)
            df_csv.columns = [c.strip() for c in df_csv.columns]
            added, skipped = 0, 0
            for _, row in df_csv.iterrows():
                eid = str(row.get("Employee ID", "")).strip()
                nm  = str(row.get("Full Name", "")).strip()
                if not eid or not nm:
                    skipped += 1; continue
                if any(p["emp_id"] == eid for p in st.session_state.pilots):
                    skipped += 1; continue
                nat_v  = row.get("Nationality","Local")
                flt_v  = row.get("Fleet","ATR 72")
                func_v = row.get("Function","First Officer")
                des_v  = str(row.get("Designations","")).strip()
                des_list = [d.strip() for d in des_v.split(";") if d.strip() in DESIGNATIONS] if des_v else []
                stat_v = row.get("Status","Active")
                st.session_state.pilots.append({
                    "id":           next_id(),
                    "emp_id":       eid,
                    "name":         nm,
                    "type":         nat_v if nat_v in PILOT_TYPES else "Local",
                    "fleet":        flt_v if flt_v in FLEETS else "ATR 72",
                    "function":     func_v if func_v in FUNCTIONS else "First Officer",
                    "status":       stat_v if stat_v in STATUSES else "Active",
                    "designations": des_list,
                })
                added += 1
            st.success(f"Imported {added} pilots. Skipped {skipped}.")
            st.rerun()
        except Exception as e:
            st.error(f"CSV parse error: {e}")

    # ── Filters ────────────────────────────────────────
    st.markdown('<div class="section-header">Pilot Registry</div>', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        filt_fleet = st.selectbox("Filter Fleet", ["All"] + FLEETS, key="filt_fleet")
    with fc2:
        filt_func  = st.selectbox("Filter Function", ["All"] + FUNCTIONS, key="filt_func")
    with fc3:
        filt_type  = st.selectbox("Filter Type", ["All"] + PILOT_TYPES, key="filt_type")
    with fc4:
        filt_status= st.selectbox("Filter Status", ["All"] + STATUSES, key="filt_status")

    filtered = [p for p in st.session_state.pilots if
        (filt_fleet  == "All" or p["fleet"]    == filt_fleet) and
        (filt_func   == "All" or p["function"] == filt_func)  and
        (filt_type   == "All" or p["type"]     == filt_type)  and
        (filt_status == "All" or p["status"]   == filt_status)
    ]

    if not filtered:
        st.info("No pilots match the current filters.")
    else:
        # Display table with edit/delete
        for idx, p in enumerate(filtered):
            cols = st.columns([1.2, 2.2, 1, 1.2, 1.4, 1.6, 1.4, 0.7, 0.7])
            cols[0].write(p["emp_id"])
            cols[1].write(p["name"])
            cols[2].write(p["type"])
            cols[3].write(p["fleet"])
            cols[4].write(p["function"])
            cols[5].write(", ".join(p["designations"]) if p["designations"] else "—")
            cols[6].write(p["status"])

            # Edit
            if cols[7].button("✏", key=f"edit_{p['id']}"):
                st.session_state[f"editing_{p['id']}"] = True

            # Delete
            if cols[8].button("🗑", key=f"del_{p['id']}"):
                st.session_state.pilots = [x for x in st.session_state.pilots if x["id"] != p["id"]]
                st.rerun()

            # Inline edit form
            if st.session_state.get(f"editing_{p['id']}", False):
                with st.form(f"edit_form_{p['id']}"):
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        new_name   = st.text_input("Full Name",   value=p["name"])
                        new_emp_id = st.text_input("Employee ID", value=p["emp_id"])
                    with ec2:
                        new_type   = st.selectbox("Nationality", PILOT_TYPES,  index=PILOT_TYPES.index(p["type"]))
                        new_fleet  = st.selectbox("Fleet",       FLEETS,       index=FLEETS.index(p["fleet"]))
                    with ec3:
                        new_func   = st.selectbox("Function",    FUNCTIONS,    index=FUNCTIONS.index(p["function"]))
                        new_status = st.selectbox("Status",      STATUSES,     index=STATUSES.index(p["status"]))
                    new_desig = st.multiselect("Designations", DESIGNATIONS, default=p["designations"])
                    save_edit = st.form_submit_button("💾 Save Changes")
                    if save_edit:
                        for x in st.session_state.pilots:
                            if x["id"] == p["id"]:
                                x["name"]         = new_name
                                x["emp_id"]       = new_emp_id
                                x["type"]         = new_type
                                x["fleet"]        = new_fleet
                                x["function"]     = new_func
                                x["status"]       = new_status
                                x["designations"] = new_desig
                        del st.session_state[f"editing_{p['id']}"]
                        st.rerun()

# ═══════════════════════════════════════════════════════
#  TAB 2 — PLANNING TIMELINE
# ═══════════════════════════════════════════════════════
with tab2:

    # ── Planning Period Selector ───────────────────────
    st.markdown('<div class="section-header">Planning Period</div>', unsafe_allow_html=True)
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        ps_month = st.selectbox("Start Month", range(1,13),
            index=st.session_state.plan_start[0]-1,
            format_func=lambda m: MONTHS_SHORT[m-1], key="ps_m")
    with pc2:
        ps_year  = st.number_input("Start Year", min_value=2020, max_value=2040,
            value=st.session_state.plan_start[1], step=1, key="ps_y")
    with pc3:
        pe_month = st.selectbox("End Month", range(1,13),
            index=st.session_state.plan_end[0]-1,
            format_func=lambda m: MONTHS_SHORT[m-1], key="pe_m")
    with pc4:
        pe_year  = st.number_input("End Year", min_value=2020, max_value=2040,
            value=st.session_state.plan_end[1], step=1, key="pe_y")

    st.session_state.plan_start = (ps_month, int(ps_year))
    st.session_state.plan_end   = (pe_month, int(pe_year))

    months = month_range(ps_month, int(ps_year), pe_month, int(pe_year))

    # ── Conflict Warnings ─────────────────────────────
    conflicts = detect_conflicts()
    if conflicts:
        st.markdown('<div class="section-header">⚠ Conflict Warnings</div>', unsafe_allow_html=True)
        for c in conflicts:
            st.markdown(f'<div class="conflict-badge">{c}</div>', unsafe_allow_html=True)

    # ── Planning Grid ─────────────────────────────────
    st.markdown('<div class="section-header">Crew Coverage Grid</div>', unsafe_allow_html=True)

    if not months:
        st.warning("Invalid planning period.")
    else:
        # Build header
        header_cols = st.columns([1.2] + [2] * len(FLEETS))
        header_cols[0].markdown("**Month**")
        for i, fl in enumerate(FLEETS):
            req = get_required_sets(fl)
            header_cols[i+1].markdown(f"**{fl}**<br><small>Req: {req}C / {req}FO</small>", unsafe_allow_html=True)

        for (mo, yr) in months:
            row_cols = st.columns([1.2] + [2] * len(FLEETS))
            row_cols[0].markdown(f"**{MONTHS_SHORT[mo-1]} {yr}**")
            for i, fl in enumerate(FLEETS):
                req = get_required_sets(fl)
                cpt_filled = active_pilots_in_month(fl, "Captain", mo, yr)
                fo_filled  = active_pilots_in_month(fl, "First Officer", mo, yr)
                cpt_gap    = req - cpt_filled
                fo_gap     = req - fo_filled

                def gap_class(gap):
                    if gap <= 0 and gap > -2: return "cell-ok"
                    if gap < -1: return "cell-over"
                    if gap == 1: return "cell-warn"
                    return "cell-crit"

                cpt_cls = gap_class(cpt_gap)
                fo_cls  = gap_class(fo_gap)

                cell_html = (
                    f'<span class="{cpt_cls}">CPT {cpt_filled}/{req}</span> '
                    f'<span class="{fo_cls}">FO {fo_filled}/{req}</span>'
                )
                row_cols[i+1].markdown(cell_html, unsafe_allow_html=True)

        st.markdown("""
<small style="color:#8ecae6;">
🟢 OK &nbsp;|&nbsp; 🟡 Gap=1 &nbsp;|&nbsp; 🔴 Gap≥2 &nbsp;|&nbsp; 🔵 Overstaffed
</small>""", unsafe_allow_html=True)

    # ── Add Action Form ────────────────────────────────
    st.markdown('<div class="section-header">Add Planned Action</div>', unsafe_allow_html=True)

    with st.form("add_action_form", clear_on_submit=True):
        ac1, ac2 = st.columns(2)
        with ac1:
            action_type = st.selectbox("Action Type", ACTION_TYPES)
            action_fleet= st.selectbox("Fleet", FLEETS, key="af")
        with ac2:
            a_start_m   = st.selectbox("Start Month", range(1,13),
                index=ps_month-1, format_func=lambda m: MONTHS_SHORT[m-1], key="asm")
            a_start_y   = st.number_input("Start Year", min_value=2020, max_value=2040,
                value=int(ps_year), step=1, key="asy")

        # Dynamic fields
        tr_mode      = None
        instructor   = None
        trainee1     = None
        trainee2     = None
        action_label = ""
        duration     = 1

        pilot_options_tbd = ["TBD"] + [p["name"] for p in st.session_state.pilots]
        pilot_options     = [p["name"] for p in st.session_state.pilots]

        if action_type in ["Type Rating", "Command Upgrade"]:
            af1, af2 = st.columns(2)
            with af1:
                tr_mode = st.selectbox("Mode", TR_MODES)
            with af2:
                if action_type == "Type Rating":
                    duration = st.number_input("Duration (months)", min_value=1, max_value=6, value=2, step=1)
                else:
                    duration = COMMAND_UPGRADE_DURATION
                    st.info(f"Command Upgrade duration: {duration} month(s)")

            t1, t2 = st.columns(2)
            with t1:
                trainee1 = st.selectbox("Trainee 1", pilot_options_tbd)
            with t2:
                trainee2 = st.selectbox("Trainee 2", pilot_options_tbd)

            if tr_mode == "Internal":
                instructor = st.selectbox("Instructor (Captain)", pilot_options_tbd)
            else:
                instructor = "External"

            action_label = f"{action_type} ({tr_mode}) on {action_fleet}"

        elif action_type == "Fleet Change":
            fc1_, fc2_ = st.columns(2)
            with fc1_:
                from_fleet = st.selectbox("From Fleet", FLEETS, key="from_f")
                from_func  = st.selectbox("From Function", FUNCTIONS, key="from_fn")
            with fc2_:
                to_fleet   = st.selectbox("To Fleet", FLEETS, key="to_f")
                to_func    = st.selectbox("To Function", FUNCTIONS, key="to_fn")
            trainee1 = st.selectbox("Pilot", pilot_options_tbd, key="fc_pilot")
            key = (from_fleet, from_func, to_fleet, to_func)
            duration = TRANSITION_RULES.get(key, 2)
            st.info(f"Duration: {duration} month(s) based on transition rules.")
            action_label = f"Fleet Change: {from_fleet} {from_func} → {to_fleet} {to_func}"

        elif action_type == "Cadet Hire":
            trainee1 = st.text_input("Cadet Name (or TBD)")
            duration = 2
            action_label = f"Cadet Hire → ATR 72 FO"
            st.info("Cadet → ATR 72 First Officer. Duration: 2 months.")

        elif action_type == "Expat Hire":
            trainee1 = st.text_input("Expat Name (or TBD)")
            eh_func  = st.selectbox("Function", FUNCTIONS, key="eh_func")
            duration = 0
            action_label = f"Expat Hire: {action_fleet} {eh_func}"

        notes = st.text_input("Notes (optional)")
        submit_action = st.form_submit_button("➕ Add Action", use_container_width=True)

        if submit_action:
            def resolve_pid(name_or_tbd):
                if not name_or_tbd or name_or_tbd == "TBD":
                    return "TBD"
                for p in st.session_state.pilots:
                    if p["name"] == name_or_tbd:
                        return p["id"]
                return name_or_tbd  # free text

            new_action = {
                "id":             next_id(),
                "type":           action_type,
                "fleet":          action_fleet,
                "start_month":    int(a_start_m),
                "start_year":     int(a_start_y),
                "duration_months":int(duration),
                "tr_mode":        tr_mode,
                "instructor":     resolve_pid(instructor) if instructor else None,
                "trainee1":       resolve_pid(trainee1)   if trainee1  else None,
                "trainee2":       resolve_pid(trainee2)   if trainee2  else None,
                "label":          action_label,
                "notes":          notes,
            }
            st.session_state.actions.append(new_action)
            st.success(f"Action added: {action_label}")
            st.rerun()

    # ── Action List with Cascade ───────────────────────
    if st.session_state.actions:
        st.markdown('<div class="section-header">Planned Actions</div>', unsafe_allow_html=True)
        for a in st.session_state.actions:
            em_, ey_ = add_months(a["start_month"], a["start_year"], a.get("duration_months", 1) - 1)
            span = f"{MONTHS_SHORT[a['start_month']-1]} {a['start_year']} → {MONTHS_SHORT[em_-1]} {ey_}"

            def pid_display(val):
                if val is None: return "—"
                if val == "TBD" or val == "External": return str(val)
                return pilot_name_by_id(val)

            details = f"**{a['label']}** | {span}"
            if a.get("trainee1"): details += f" | T1: {pid_display(a['trainee1'])}"
            if a.get("trainee2"): details += f" | T2: {pid_display(a['trainee2'])}"
            if a.get("instructor"): details += f" | Instr: {pid_display(a['instructor'])}"
            if a.get("notes"):   details += f" | {a['notes']}"

            dcol1, dcol2 = st.columns([10, 1])
            with dcol1:
                st.markdown(details)
                # Cascade recommendation for command upgrades
                if a["type"] == "Command Upgrade":
                    casc = cascade_recommendation(a)
                    st.markdown(f'<div class="cascade-badge">⛓ Cascade: {casc}</div>', unsafe_allow_html=True)
            with dcol2:
                if st.button("🗑", key=f"del_action_{a['id']}"):
                    st.session_state.actions = [x for x in st.session_state.actions if x["id"] != a["id"]]
                    st.rerun()
            st.markdown("---")

# ═══════════════════════════════════════════════════════
#  TAB 3 — LOCALISATION TRACKER
# ═══════════════════════════════════════════════════════
with tab3:

    st.markdown('<div class="section-header">Local vs Expat Ratio by Fleet</div>', unsafe_allow_html=True)

    for fleet in FLEETS:
        fleet_pilots = [p for p in st.session_state.pilots if p["fleet"] == fleet]
        local_cnt  = sum(1 for p in fleet_pilots if p["type"] == "Local")
        expat_cnt  = sum(1 for p in fleet_pilots if p["type"] == "Expat")
        total_cnt  = len(fleet_pilots)
        req_sets   = get_required_sets(fleet)
        req_total  = req_sets * 2
        local_pct  = (local_cnt / total_cnt * 100) if total_cnt > 0 else 0

        st.markdown(f'<div class="prog-label"><span>{fleet}</span><span>{local_cnt}L / {expat_cnt}E of {total_cnt} pilots (target {req_total})</span></div>', unsafe_allow_html=True)
        st.progress(min(local_pct / 100, 1.0))

    # ── Expat Position Table ───────────────────────────
    st.markdown('<div class="section-header">Expat Positions & Localisation Eligibility</div>', unsafe_allow_html=True)

    elig = localisation_eligibility()
    if not elig:
        st.info("No expat positions in the registry.")
    else:
        rows = []
        for e in elig:
            rows.append({
                "Name":          e["expat_name"],
                "Fleet":         e["fleet"],
                "Function":      e["function"],
                "Can Localise?": "✅ Yes" if e["can_localise"] else "❌ No",
                "Eligible Locals": ", ".join(e["eligible_locals"]) if e["eligible_locals"] else "None identified",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Recommended Next Actions ───────────────────────
    st.markdown('<div class="section-header">Recommended Next Localisation Actions</div>', unsafe_allow_html=True)
    ready = [e for e in elig if e["can_localise"]]
    if not ready:
        st.info("No immediate localisation opportunities identified based on current pilot registry.")
    else:
        for e in ready:
            for lname in e["eligible_locals"]:
                if "Cmd Upgrade" in lname:
                    rec = f"🔼 **Command Upgrade**: {lname.replace(' (Cmd Upgrade)','')} can upgrade to {e['fleet']} Captain, replacing expat **{e['expat_name']}** (1 month)"
                else:
                    key_match = None
                    for lp in st.session_state.pilots:
                        if lp["name"] == lname:
                            k = (lp["fleet"], lp["function"], e["fleet"], e["function"])
                            dur = TRANSITION_RULES.get(k, 2)
                            key_match = (lp["fleet"], lp["function"], dur)
                            break
                    if key_match:
                        rec = (f"🔄 **Type Rating**: {lname} ({key_match[0]} {key_match[1]}) → "
                               f"{e['fleet']} {e['function']} ({key_match[2]}mo), "
                               f"replacing expat **{e['expat_name']}**")
                    else:
                        rec = f"🔄 **Transition**: {lname} → {e['fleet']} {e['function']}, replacing expat **{e['expat_name']}**"
                st.markdown(f"- {rec}")

    # ── Localisation Projection Chart ─────────────────
    st.markdown('<div class="section-header">Projected Local % Over Planning Period</div>', unsafe_allow_html=True)

    months_list = month_range(
        st.session_state.plan_start[0], st.session_state.plan_start[1],
        st.session_state.plan_end[0],   st.session_state.plan_end[1]
    )

    if not months_list:
        st.warning("Set a valid planning period in the Planning Timeline tab.")
    else:
        proj = projected_localisation(months_list)
        month_labels = [f"{MONTHS_SHORT[m-1]} {y}" for m, y in months_list]

        chart_data = pd.DataFrame(proj, index=month_labels)
        st.line_chart(chart_data, use_container_width=True)
        st.caption("Note: Projection is based on current pilot registry. Add actions in the Planning Timeline to model future transitions.")
