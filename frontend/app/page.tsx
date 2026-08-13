"use client";

/* API output sections are heterogeneous, schema-versioned JSON documents. */

import {
  ArrowRight,
  BarChart3,
  BriefcaseBusiness,
  CheckCircle2,
  ChevronRight,
  CircleGauge,
  ClipboardCheck,
  Database,
  FileSearch,
  FileText,
  FlaskConical,
  LogOut,
  Menu,
  Plus,
  Search,
  ShieldCheck,
  Upload,
  UserRoundCheck,
  X,
} from "lucide-react";
import React, { FormEvent, useEffect, useMemo, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "";

type User = { email: string; display_name: string; role: string };
type Case = {
  id: string; title: string; sku_id: string; channel: string; region: string;
  promotion_start_week: string; promotion_end_week: string; forecast_horizon_weeks: number;
  status: string; updated_at: string; dataset_id: string; description?: string;
};
type Output = {
  id: string; output_version: string; output_json: Record<string, any>;
  output_markdown: string; human_review_status: string; generated_at: string;
};
type View = "cases" | "create" | "datasets" | "evidence" | "assessment" |
  "investigation" | "simulations" | "brief" | "review" | "admin";

const nav: Array<{ id: View; label: string; icon: React.ElementType }> = [
  { id: "cases", label: "Case work queue", icon: BriefcaseBusiness },
  { id: "create", label: "Create diagnostic", icon: Plus },
  { id: "datasets", label: "Datasets", icon: Database },
  { id: "evidence", label: "Case evidence", icon: BarChart3 },
  { id: "assessment", label: "Growth assessment", icon: CircleGauge },
  { id: "investigation", label: "Investigation plan", icon: FileSearch },
  { id: "simulations", label: "Decision simulations", icon: FlaskConical },
  { id: "brief", label: "Executive brief", icon: FileText },
  { id: "review", label: "Human review", icon: UserRoundCheck },
  { id: "admin", label: "Admin & audit", icon: ShieldCheck },
];

function label(value?: string) {
  return (value || "Not available").replaceAll("_", " ").toLowerCase().replace(/(^|\s)\S/g, c => c.toUpperCase());
}

function Status({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`status status-${tone}`}><span />{children}</span>;
}

async function request(path: string, token: string, options: RequestInit = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : body.detail?.message || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

export default function HomePage() {
  const [token, setToken] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [view, setView] = useState<View>("cases");
  const [cases, setCases] = useState<Case[]>([]);
  const [selected, setSelected] = useState<Case | null>(null);
  const [output, setOutput] = useState<Output | null>(null);
  const [evidence, setEvidence] = useState<Record<string, any> | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [menu, setMenu] = useState(false);

  async function loadCases(auth = token) {
    const data = await request("/api/diagnostic-cases?page=1&page_size=100", auth);
    setCases(data.items);
    if (!selected && data.items.length) setSelected(data.items[0]);
  }

  async function loadCaseData(target: Case, auth = token) {
    setSelected(target); setOutput(null); setEvidence(null);
    const [evidenceResult, outputResult] = await Promise.allSettled([
      request(`/api/diagnostic-cases/${target.id}/forecast-evidence`, auth),
      request(`/api/diagnostic-cases/${target.id}/decision-intelligence/latest`, auth),
    ]);
    if (evidenceResult.status === "fulfilled") setEvidence(evidenceResult.value);
    if (outputResult.status === "fulfilled") setOutput(outputResult.value);
  }

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    const form = new FormData(event.currentTarget);
    try {
      const auth = await request("/api/auth/login", "", { method: "POST", body: JSON.stringify({ email: form.get("email"), password: form.get("password") }) });
      setToken(auth.access_token);
      const me = await request("/api/auth/me", auth.access_token);
      setUser(me); await loadCases(auth.access_token);
    } catch (err) { setError(err instanceof Error ? err.message : "Sign in failed"); }
    finally { setBusy(false); }
  }

  useEffect(() => { if (selected && token) void loadCaseData(selected); }, [selected?.id]); // eslint-disable-line react-hooks/exhaustive-deps, react-hooks/set-state-in-effect

  if (!token) return <Login onSubmit={login} busy={busy} error={error} />;

  function go(next: View) { setView(next); setMenu(false); setError(""); setNotice(""); }
  return (
    <div className="app-frame">
      <aside className={menu ? "sidebar open" : "sidebar"}>
        <div className="brand"><div className="brand-mark">V</div><div><b>VAI</b><small>Growth quality</small></div></div>
        <button className="mobile-close" onClick={() => setMenu(false)} aria-label="Close menu"><X /></button>
        <div className="nav-caption">Diagnostic workflow</div>
        <nav>{nav.map(({ id, label: itemLabel, icon: Icon }) => <button key={id} className={view === id ? "active" : ""} onClick={() => go(id)}><Icon size={18}/><span>{itemLabel}</span>{id === "cases" && cases.length > 0 && <em>{cases.length}</em>}</button>)}</nav>
        <div className="control-note"><ShieldCheck size={18}/><div><b>Human controlled</b><span>No action is executed by VAI.</span></div></div>
        <div className="profile"><div className="avatar">{user?.display_name?.[0] || "A"}</div><div><b>{user?.display_name}</b><span>{label(user?.role)}</span></div><button aria-label="Sign out" onClick={() => { setToken(""); setUser(null); }}><LogOut size={17}/></button></div>
      </aside>
      {menu && <button className="scrim" onClick={() => setMenu(false)} aria-label="Close navigation" />}
      <main className="workspace">
        <header className="topbar"><button className="menu-button" onClick={() => setMenu(true)}><Menu/></button><div className="case-context"><span>Active case</span><select value={selected?.id || ""} onChange={e => { const found = cases.find(item => item.id === e.target.value); if (found) setSelected(found); }}><option value="">No case selected</option>{cases.map(item => <option key={item.id} value={item.id}>{item.title}</option>)}</select></div><div className="api-state"><span/>System connected</div></header>
        <div className="content">
          {notice && <div className="toast success"><CheckCircle2/>{notice}</div>}
          {error && <div className="toast error"><X/>{error}</div>}
          {view === "cases" && <CasesView cases={cases} selected={selected} onSelect={item => { setSelected(item); go("assessment"); }} onCreate={() => go("create")}/>}
          {view === "create" && <CreateView token={token} onDone={async item => { await loadCases(); setSelected(item); setNotice("Diagnostic case created as a draft."); go("cases"); }} setError={setError}/>}
          {view === "datasets" && <DatasetView token={token} setError={setError} setNotice={setNotice}/>}
          {view === "evidence" && <EvidenceView selected={selected} evidence={evidence}/>}
          {view === "assessment" && <AssessmentView selected={selected} output={output} onGenerate={async () => { if (!selected) return; setBusy(true); try { const result = await request(`/api/diagnostic-cases/${selected.id}/decision-intelligence`, token, {method:"POST"}); setOutput(result); await loadCases(); setNotice("Decision-intelligence draft generated for human review."); } catch(err) { setError(err instanceof Error ? err.message : "Generation failed"); } finally { setBusy(false); } }} busy={busy}/>}
          {view === "investigation" && <InvestigationView output={output}/>}
          {view === "simulations" && <SimulationsView output={output}/>}
          {view === "brief" && <BriefView output={output}/>}
          {view === "review" && <ReviewView output={output} selected={selected} token={token} onReviewed={async () => { if (selected) await loadCaseData(selected); await loadCases(); setNotice("Human review was recorded and audited."); }}/>}
          {view === "admin" && <AdminView user={user} output={output}/>}
        </div>
      </main>
    </div>
  );
}

function Login({ onSubmit, busy, error }: { onSubmit: (e: FormEvent<HTMLFormElement>) => void; busy: boolean; error: string }) {
  return <main className="login-page"><section className="login-story"><div className="story-inner"><p className="eyebrow">VAI · FMCG commercial decision intelligence</p><h1>Forecast-Augmented<br/>Growth Quality<br/>Diagnostic</h1><p>Separate real demand from temporary, shifted, loaded, cannibalized, discount-dependent, or value-dilutive growth.</p><div className="story-steps"><span><b>01</b>TimesFM predicts movement.</span><span><b>02</b>VAI interprets growth quality.</span><span><b>03</b>Humans validate and decide.</span></div></div></section><section className="login-panel"><form onSubmit={onSubmit}><div className="login-logo">V</div><p className="kicker">Secure workspace</p><h2>Welcome back</h2><p className="muted">Sign in to access your controlled diagnostic work queue.</p>{error && <div className="form-error">{error}</div>}<label>Work email<input name="email" type="email" defaultValue="admin@example.com" required/></label><label>Password<input name="password" type="password" defaultValue="development-admin-only" required/></label><button className="primary" disabled={busy}>{busy ? "Signing in…" : "Sign in securely"}<ArrowRight size={18}/></button><p className="security"><ShieldCheck size={16}/>Human review is required before commercial action.</p></form></section></main>;
}

function PageHead({ eyebrow, title, intro, action }: { eyebrow: string; title: string; intro: string; action?: React.ReactNode }) { return <div className="page-head"><div><p className="kicker">{eyebrow}</p><h2>{title}</h2><p>{intro}</p></div>{action}</div>; }

function Empty({ title = "Select a diagnostic case", text = "Choose a case from the active-case menu to view this stage." }: { title?: string; text?: string }) { return <div className="empty"><FileSearch/><h3>{title}</h3><p>{text}</p></div>; }

function CasesView({ cases, selected, onSelect, onCreate }: { cases: Case[]; selected: Case|null; onSelect:(c:Case)=>void; onCreate:()=>void }) {
  const counts = useMemo(() => ({ active: cases.filter(c => !["COMPLETED","REJECTED"].includes(c.status)).length, review: cases.filter(c => c.status.includes("REVIEW")).length, draft: cases.filter(c => c.status === "DRAFT").length }), [cases]);
  return <><PageHead eyebrow="Controlled work queue" title="Diagnostic cases" intro="Move apparently positive growth signals through evidence, interpretation, and human review." action={<button className="primary compact" onClick={onCreate}><Plus/>New diagnostic</button>}/><div className="metric-row"><div><span>Open cases</span><strong>{counts.active}</strong><small>Across your permitted scope</small></div><div><span>Ready for review</span><strong>{counts.review}</strong><small>Human decision required</small></div><div><span>Drafts</span><strong>{counts.draft}</strong><small>Not yet submitted</small></div><div><span>Control status</span><strong className="word">Active</strong><small>No execution capability</small></div></div><section className="panel"><div className="panel-tools"><div><h3>Commercial diagnostics</h3><p>{cases.length} case{cases.length === 1 ? "" : "s"} in the current work queue</p></div><div className="search"><Search/><input placeholder="Search cases"/></div></div>{cases.length === 0 ? <Empty title="No diagnostic cases yet" text="Create a case after uploading and validating an FMCG dataset."/> : <div className="case-table"><div className="table-head"><span>Case / series</span><span>Market scope</span><span>Promotion window</span><span>Status</span><span>Updated</span><span/></div>{cases.map(item => <button key={item.id} className={selected?.id === item.id ? "case-row selected" : "case-row"} onClick={() => onSelect(item)}><span><b>{item.title}</b><small>{item.sku_id}</small></span><span><b>{label(item.channel)}</b><small>{label(item.region)}</small></span><span><b>{item.promotion_start_week}</b><small>to {item.promotion_end_week}</small></span><span><Status tone={item.status.includes("REVIEW") ? "amber" : item.status === "DRAFT" ? "neutral" : "green"}>{label(item.status)}</Status></span><span>{new Date(item.updated_at).toLocaleDateString()}</span><ChevronRight/></button>)}</div>}</section></>;
}

function CreateView({ token, onDone, setError }: {token:string;onDone:(c:Case)=>void;setError:(s:string)=>void}) {
  async function submit(e:FormEvent<HTMLFormElement>) { e.preventDefault(); const data=Object.fromEntries(new FormData(e.currentTarget)); try { const item=await request("/api/diagnostic-cases",token,{method:"POST",body:JSON.stringify({...data,forecast_horizon_weeks:Number(data.forecast_horizon_weeks)})}); onDone(item); } catch(err){setError(err instanceof Error?err.message:"Could not create case");} }
  return <><PageHead eyebrow="Step 2 of 10" title="Create diagnostic case" intro="Define one exact SKU × channel × region scope. The system will not broaden it automatically."/><form className="panel form-grid" onSubmit={submit}><div className="form-section"><h3>Case identity</h3><p>Name the management question and link a validated dataset.</p></div><label className="span-2">Case title<input name="title" placeholder="e.g. Spring promotion growth quality" required/></label><label>Validated dataset ID<input name="dataset_id" placeholder="UUID from dataset upload" required/></label><label>Forecast horizon<select name="forecast_horizon_weeks" defaultValue="6"><option value="4">4 weeks</option><option value="6">6 weeks</option><option value="8">8 weeks</option></select></label><div className="divider span-2"/><div className="form-section"><h3>Exact series grain</h3><p>These fields prevent evidence from leaking across commercial scopes.</p></div><label>SKU ID<input name="sku_id" placeholder="SKU-001" required/></label><label>Channel<input name="channel" placeholder="MODERN_TRADE" required/></label><label>Region<input name="region" placeholder="NORTH" required/></label><label>Promotion start<input name="promotion_start_week" type="date" required/></label><label>Promotion end<input name="promotion_end_week" type="date" required/></label><label className="span-2">Management concern<textarea name="management_concern_note" placeholder="What decision could this diagnostic affect?"/></label><div className="form-actions span-2"><button className="primary">Create draft case<ArrowRight/></button></div></form></>;
}

function DatasetView({token,setError,setNotice}:{token:string;setError:(s:string)=>void;setNotice:(s:string)=>void}) { const [dataset,setDataset]=useState<any>(null); const [report,setReport]=useState<any>(null); async function upload(e:FormEvent<HTMLFormElement>){e.preventDefault();const body=new FormData(e.currentTarget);try{const result=await request("/api/datasets",token,{method:"POST",body});setDataset(result);setNotice("Dataset uploaded. Run validation before using it in a case.");}catch(err){setError(err instanceof Error?err.message:"Upload failed");}} async function validate(){try{const result=await request(`/api/datasets/${dataset.id}/validate`,token,{method:"POST",body:JSON.stringify({currency:"USD",gross_margin_representation:"amount",stock_unit:"units"})});setReport(result);setNotice("Validation completed and report stored.");}catch(err){setError(err instanceof Error?err.message:"Validation failed");}} return <><PageHead eyebrow="Step 1 of 10" title="Dataset upload & validation" intro="Upload weekly FMCG evidence. Invalid rows and uncertainty remain visible; nothing is silently discarded."/><div className="two-col"><form className="panel upload-card" onSubmit={upload}><div className="upload-icon"><Upload/></div><h3>Upload commercial evidence</h3><p>CSV or XLSX · maximum 20 MB · exact weekly grain</p><label>Dataset name<input name="name" placeholder="Q2 promotion evidence" required/></label><label className="file-input"><input name="file" type="file" accept=".csv,.xlsx" required/><span><Upload/>Choose a file</span></label><button className="primary">Upload dataset</button></form><section className="panel"><h3>Validation control</h3>{!dataset?<div className="mini-empty">Upload a dataset to expose its validation controls.</div>:<><div className="dataset-ticket"><Database/><div><b>{dataset.name}</b><span>{dataset.original_filename}</span><code>{dataset.id}</code></div><Status>{label(dataset.upload_status)}</Status></div><button className="secondary wide" onClick={validate}><ClipboardCheck/>Run structured validation</button>{report&&<div className="validation-result"><Status tone={report.critical_errors.length?"red":"green"}>{label(report.overall_status)}</Status><div><span>Rows<strong>{report.row_count}</strong></span><span>Warnings<strong>{report.warnings.length}</strong></span><span>Critical<strong>{report.critical_errors.length}</strong></span></div><p>{report.forecast_eligible_series.length} forecast-eligible series</p></div>}</>}</section></div></> }

function EvidenceView({selected,evidence}:{selected:Case|null;evidence:any}) { if(!selected)return <Empty/>; return <><PageHead eyebrow="Step 4 of 10" title="Case evidence" intro="Actuals, baseline, forecast, and uncertainty are evidence aids—not commercial conclusions."/><CaseStrip item={selected}/>{!evidence?<Empty title="Forecast evidence not generated" text="Submit the case, calculate its baseline, and run a forecast through the API workflow."/>:<div className="evidence-grid"><section className="panel chart-panel"><div className="panel-title"><div><p className="kicker">Sell-out forecast</p><h3>{evidence.series_id}</h3></div><Status tone="green">{evidence.forecast_horizon} week horizon</Status></div><MiniChart values={evidence.forecasted_values_json.map((p:any)=>p.point_forecast)}/><div className="chart-legend"><span className="actual">Forecast movement</span><span className="band">Confidence interval</span></div></section><section className="panel signal-list"><h3>Forecast evidence</h3>{[["Direction",evidence.forecast_direction],["Baseline comparison",evidence.baseline_comparison],["Retention",evidence.post_promo_retention_status],["Decay",evidence.decay_signal],["Uncertainty",evidence.uncertainty_level]].map(([k,v])=><div key={k}><span>{k}</span><b>{label(v)}</b></div>)}</section><section className="panel full"><h3>Data-quality notes</h3>{evidence.data_quality_notes_json.length?<ul>{evidence.data_quality_notes_json.map((n:string)=><li key={n}>{n}</li>)}</ul>:<p className="muted">No additional quality notes were produced.</p>}</section></div>}</> }

function CaseStrip({item}:{item:Case}) { return <div className="case-strip"><div><span>SKU</span><b>{item.sku_id}</b></div><div><span>Channel</span><b>{label(item.channel)}</b></div><div><span>Region</span><b>{label(item.region)}</b></div><div><span>Status</span><Status tone="amber">{label(item.status)}</Status></div></div> }
function MiniChart({values}:{values:number[]}) { const max=Math.max(...values,1),min=Math.min(...values,0);const points=values.map((v,i)=>`${30+i*(620/Math.max(values.length-1,1))},${190-((v-min)/(max-min||1))*130}`).join(" ");return <svg className="mini-chart" viewBox="0 0 680 230" role="img" aria-label="Forecast evidence chart"><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#3f7257" stopOpacity=".28"/><stop offset="1" stopColor="#3f7257" stopOpacity="0"/></linearGradient></defs>{[40,80,120,160,200].map(y=><line key={y} x1="20" x2="660" y1={y} y2={y} stroke="#e4e9e5"/>)}<polygon points={`${points} 650,205 30,205`} fill="url(#area)"/><polyline points={points} fill="none" stroke="#2d6648" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>{points.split(" ").map((p,i)=>{const [x,y]=p.split(",");return <circle key={i} cx={x} cy={y} r="5" fill="#fff" stroke="#2d6648" strokeWidth="3"/>})}</svg> }

function AssessmentView({selected,output,onGenerate,busy}:{selected:Case|null;output:Output|null;onGenerate:()=>void;busy:boolean}) { if(!selected)return <Empty/>; const data=output?.output_json; return <><PageHead eyebrow="Step 5 of 10" title="Growth quality assessment" intro="Facts remain separate from interpretation, risk classification, and priority." action={!output&&selected.status==="INTERPRETING"?<button className="primary compact" onClick={onGenerate} disabled={busy}>{busy?"Generating…":"Generate draft"}<ArrowRight/></button>:undefined}/><CaseStrip item={selected}/>{!data?<Empty title="Assessment not available" text={selected.status === "INTERPRETING" ? "This case is ready. Generate its controlled decision-intelligence draft." : "Complete data validation, baseline, and forecasting before assessment."}/>:<><div className="assessment-hero"><div><p className="kicker">Candidate judgment · human validation pending</p><h3>{label(data.risk_classification?.primary || "No supported risk class")}</h3><p>{data.growth_signal_summary}</p></div><div><span>Priority</span><strong>{label(data.priority)}</strong><span>Evidence confidence</span><strong>{label(data.evidence_confidence)}</strong></div></div><div className="two-col"><section className="panel"><h3>Interpretation</h3><p className="callout">{data.growth_quality_judgment?.candidate_judgment ? "The signal should not yet be treated as final healthy growth." : "Evidence is insufficient for a risk classification."}</p><h4>Secondary classifications</h4><div className="tag-list">{data.risk_classification?.secondary?.map((x:string)=><span key={x}>{label(x)}</span>) || <span>None</span>}</div></section><section className="panel"><h3>Uncertainty</h3><ul>{(data.growth_quality_judgment?.uncertainty || ["No uncertainty notes recorded."]).map((x:string)=><li key={x}>{x}</li>)}</ul></section></div></>}</> }

function InvestigationView({output}:{output:Output|null}) { const items=output?.output_json.investigation_plan||[]; return <><PageHead eyebrow="Step 6 of 10" title="Investigation plan" intro="Every item names the exact commercial question, evidence gap, owner, and risk of acting early."/>{!items.length?<Empty title="No investigation plan yet" text="Generate the decision-intelligence draft for the active case."/>:<div className="card-stack">{items.map((item:any,i:number)=><section className="panel investigation" key={item.investigation_area}><div className="number">{String(i+1).padStart(2,"0")}</div><div className="investigation-main"><div className="panel-title"><div><p className="kicker">{label(item.investigation_area)}</p><h3>{item.question}</h3></div><Status tone={item.urgency==="TODAY"?"red":"amber"}>{label(item.urgency)}</Status></div><p>{item.why_it_matters}</p><div className="evidence-cols"><div><h4>Evidence available</h4>{item.available_evidence.length?item.available_evidence.map((x:string)=><span className="check" key={x}><CheckCircle2/>{x}</span>):<span className="muted">None confirmed</span>}</div><div><h4>Evidence still required</h4>{item.missing_evidence.map((x:string)=><span key={x}><FileSearch/>{x}</span>)}</div></div><footer><span><b>Human owner</b>{label(item.recommended_human_owner)}</span><span><b>Decision affected</b>{label(item.decision_affected)}</span><span><b>Confidence</b>{label(item.confidence)}</span></footer></div></section>)}</div>}</> }

function SimulationsView({output}:{output:Output|null}) { const items=output?.output_json.decision_simulation||[]; return <><PageHead eyebrow="Step 7 of 10" title="Neutral decision simulations" intro="Compare plausible benefits and risks. VAI does not rank, select, optimize, or execute an option."/><div className="safety-banner"><ShieldCheck/><div><b>Simulation only</b><span>Every option is conditional and requires human review before selection.</span></div></div>{!items.length?<Empty title="No simulations yet"/>:<div className="simulation-grid">{items.map((item:any)=><section className="panel simulation" key={item.option}><p className="kicker">Option under review</p><h3>{label(item.option)}</h3><p>{item.decision_being_tested}</p><div className="sim-block positive"><b>Potential benefit</b>{item.plausible_benefits.map((x:string)=><span key={x}>{x}</span>)}</div><div className="sim-block risk"><b>Commercial risk</b>{item.plausible_risks.slice(0,2).map((x:string)=><span key={x}>{x}</span>)}</div><footer><span>{label(item.confidence)} confidence</span><span>Human review required</span></footer></section>)}</div>}</> }

function BriefView({output}:{output:Output|null}) { const d=output?.output_json; return <><PageHead eyebrow="Step 8 of 10" title="Executive brief" intro="Leadership-ready evidence and interpretation, visibly marked until a human completes review."/>{!d?<Empty title="Executive brief not generated"/>:<article className="brief"><header><div><p>VAI · FMCG growth quality</p><h2>Executive decision intelligence</h2><span>Generated {new Date(output!.generated_at).toLocaleString()}</span></div><Status tone="amber">Draft · Human review pending</Status></header><section><b>01</b><div><h3>Growth signal summary</h3><p>{d.growth_signal_summary}</p></div></section><section><b>02</b><div><h3>Growth-quality judgment</h3><p>{label(d.risk_classification.primary || "No supported risk class")}</p><div className="tag-list">{d.risk_classification.secondary.map((x:string)=><span key={x}>{label(x)}</span>)}</div></div></section><section><b>03</b><div><h3>Priority & ownership</h3><div className="brief-grid"><span><small>Priority</small>{label(d.priority)}</span><span><small>Human owner</small>{label(d.recommended_human_owner)}</span><span><small>Confidence</small>{label(d.evidence_confidence)}</span><span><small>Decision affected</small>{label(d.decision_affected)}</span></div></div></section><section><b>04</b><div><h3>Next verification actions</h3><ol>{d.next_verification_actions.map((x:string)=><li key={x}>{x}</li>)}</ol></div></section><footer>{d.final_human_review_statement}</footer></article>}</> }

function ReviewView({output,selected,token,onReviewed}:{output:Output|null;selected:Case|null;token:string;onReviewed:()=>Promise<void>}) { const [reviewError,setReviewError]=useState(""); async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();if(!selected)return;const data=new FormData(e.currentTarget);const reviewStatus=String(data.get("review_status"));const comments=String(data.get("reviewer_comments")||"");const evidence=String(data.get("evidence_request")||"");try{await request(`/api/diagnostic-cases/${selected.id}/reviews`,token,{method:"POST",body:JSON.stringify({review_status:reviewStatus,validated_risk_class:data.get("validated_risk_class")||null,reviewer_comments:comments||null,requested_evidence:evidence?[{evidence,reason:comments||"Required before commercial decision",owner:"COMMERCIAL_DIRECTOR"}]:[],final_decision_note:data.get("final_decision_note")||null})});await onReviewed();}catch(err){setReviewError(err instanceof Error?err.message:"Review failed");}} return <><PageHead eyebrow="Step 9 of 10" title="Human review" intro="Validate, correct, request evidence, or reject—without overwriting the original draft."/>{!output?<Empty title="Nothing is ready for review"/>:<div className="two-col review-layout"><form className="panel" onSubmit={submit}><div className="review-state"><div><ClipboardCheck/><span>Current review status</span><b>{label(output.human_review_status)}</b></div></div>{reviewError&&<div className="form-error">{reviewError}</div>}<label>Review decision<select name="review_status" defaultValue="VALIDATED"><option value="VALIDATED">Validate</option><option value="VALIDATED_WITH_CHANGES">Validate with changes</option><option value="MORE_EVIDENCE_REQUIRED">Request more evidence</option><option value="REJECTED">Reject</option></select></label><label>Corrected classification (when changed)<input name="validated_risk_class" placeholder="TEMPORARY_UPLIFT"/></label><label>Reviewer comments<textarea name="reviewer_comments" placeholder="State the evidence behind the human judgment."/></label><label>Specific evidence request<input name="evidence_request" placeholder="Required when requesting more evidence"/></label><label>Final leadership note<textarea name="final_decision_note" placeholder="Human note; no action is executed here."/></label><button className="primary wide"><UserRoundCheck/>Record attributed review</button></form><section className="panel control-boundary"><ShieldCheck/><h3>Control boundary</h3><p>This form records a human judgment and audit trail. It cannot trigger budget, pricing, replenishment, customer communication, or any other commercial execution.</p></section></div>}</> }

function AdminView({user,output}:{user:User|null;output:Output|null}) { return <><PageHead eyebrow="Step 10 of 10" title="Admin & system control" intro="Operational metadata without secrets or raw sensitive payloads."/><div className="metric-row"><div><span>API</span><strong className="word green">Healthy</strong><small>Connected on port 8000</small></div><div><span>Classifier</span><strong className="word">1.0.0</strong><small>Versioned deterministic rules</small></div><div><span>Output</span><strong className="word">{output?.output_version.split("/")[1]||"1.0.0"}</strong><small>Frozen 12-section contract</small></div><div><span>Forecast</span><strong className="word">Mock</strong><small>Replaceable adapter boundary</small></div></div><div className="two-col"><section className="panel"><h3>Current access</h3><div className="admin-row"><div className="avatar">{user?.display_name?.[0]}</div><div><b>{user?.display_name}</b><span>{user?.email}</span></div><Status tone="green">{label(user?.role)}</Status></div></section><section className="panel"><h3>System boundaries</h3>{["No autonomous agents","No execution controls","Human review mandatory","Evidence keys traceable"].map(x=><div className="boundary" key={x}><CheckCircle2/>{x}</div>)}</section></div></> }
