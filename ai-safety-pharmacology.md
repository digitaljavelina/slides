---
marp: true
theme: default
paginate: true
style: |
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@200;300;400;500;600&display=swap');
  section { background: #fafafa; color: #1a1a1a; font-family: 'Inter', sans-serif; font-weight: 300; padding: 56px 72px; line-height: 1.5; }
  h1 { font-family: 'Space Grotesk'; font-weight: 700; font-size: 2.4em; color: #0f172a; letter-spacing: -0.025em; line-height: 1.05; margin: 0 0 8px; }
  h2 { font-family: 'Inter'; font-weight: 300; font-size: 1.15em; color: #64748b; margin: 0 0 24px; }
  h3 { font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.6em; color: #2563eb; text-transform: uppercase; letter-spacing: 0.18em; margin: 0 0 6px; }
  strong { color: #2563eb; font-weight: 500; }
  em { color: #475569; font-style: normal; font-weight: 400; }
  section.lead { display: flex; flex-direction: column; justify-content: center; align-items: flex-start; }
  section.lead h1 { font-size: 2.8em; line-height: 1.05; }
  section::after { font-family: 'Space Grotesk'; font-size: 0.55em; color: #cbd5e1; }
  footer { color: #94a3b8; font-size: 0.6em; font-family: 'Inter'; font-weight: 400; }
  ul { padding-left: 1.2em; }
  ul li { color: #475569; font-size: 0.78em; margin: 6px 0; font-weight: 300; }
footer: "Miller et al. · J. Pharmacol. Toxicol. Methods · 2026 · doi.org/10.1016/j.vascn.2026.108424"
---

<!-- _class: lead -->
<!-- _footer: '' -->

<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 24px;">
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.6"><path d="M12 2L4 6v6c0 5 3.5 9.5 8 10 4.5-.5 8-5 8-10V6l-8-4z"/><path d="M9 12l2 2 4-4"/></svg>
  <span style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.65em; letter-spacing: 0.2em; text-transform: uppercase; color: #2563eb;">Review · Safety Pharmacology</span>
</div>

# The Emerging Use of AI in<br>Safety Pharmacology &amp; Toxicology

## A review of foundations, applications, survey data, and regulation

<div style="margin-top: 36px; display: flex; gap: 30px; font-size: 0.7em; color: #64748b; font-weight: 400;">
  <div><span style="color:#94a3b8; font-size:0.85em; display:block; letter-spacing:0.1em; text-transform:uppercase;">Source</span>Miller, Treleaven, El Amrani, Rossman, Winters, et al.</div>
  <div><span style="color:#94a3b8; font-size:0.85em; display:block; letter-spacing:0.1em; text-transform:uppercase;">Journal</span>J. Pharmacol. Toxicol. Methods · In press</div>
  <div><span style="color:#94a3b8; font-size:0.85em; display:block; letter-spacing:0.1em; text-transform:uppercase;">DOI</span>10.1016/j.vascn.2026.108424</div>
</div>

---

### The Data Problem

# Why AI, why now?

<div style="display: flex; gap: 14px; margin-top: 8px;">
  <div style="flex: 1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 18px;">
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 10px;">New Modalities</div>
    <div style="font-size: 0.72em; color: #475569; line-height: 1.6;">Monoclonal antibodies<br>Antibody–drug conjugates<br>RNA-based therapeutics</div>
  </div>
  <div style="flex: 1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 18px;">
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 10px;">Heterogeneous Data</div>
    <div style="font-size: 0.72em; color: #475569; line-height: 1.6;">Chemical structure<br>Ion channel & receptor assays<br>In vivo telemetry · In silico sims</div>
  </div>
  <div style="flex: 1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 18px;">
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 10px;">Decision Pressure</div>
    <div style="font-size: 0.72em; color: #475569; line-height: 1.6;">Faster go / no-go calls<br>Patterns across multidim. data<br>Beyond single-biomarker rules</div>
  </div>
</div>

<div style="margin-top: 28px; background: linear-gradient(180deg, #eff6ff 0%, #fafafa 100%); border: 1px solid #dbeafe; border-radius: 12px; padding: 22px 26px; display: flex; align-items: center; gap: 28px;">
  <div>
    <div style="font-family: 'Space Grotesk'; font-weight: 700; font-size: 2.4em; color: #2563eb; line-height: 1;">~63%</div>
    <div style="font-size: 0.62em; color: #64748b; margin-top: 4px; letter-spacing: 0.05em;">of pharma allocate up to 10% of tech investment to <strong>generative AI</strong></div>
  </div>
  <div style="flex: 1; border-left: 1px solid #dbeafe; padding-left: 28px;">
    <div style="font-family: 'Space Grotesk'; font-weight: 700; font-size: 2.4em; color: #2563eb; line-height: 1;">~24%</div>
    <div style="font-size: 0.62em; color: #64748b; margin-top: 4px; letter-spacing: 0.05em;">directed toward <strong>innovation, R&amp;D</strong> · 2024 industry survey</div>
  </div>
</div>

---

### Foundations

# Three forces converged

<div style="display: flex; gap: 16px; margin-top: 16px;">
  <div style="flex: 1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 22px; position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #2563eb, transparent);"></div>
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.4"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="2" x2="9" y2="4"/><line x1="15" y1="2" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="22"/><line x1="15" y1="20" x2="15" y2="22"/><line x1="20" y1="9" x2="22" y2="9"/><line x1="20" y1="15" x2="22" y2="15"/><line x1="2" y1="9" x2="4" y2="9"/><line x1="2" y1="15" x2="4" y2="15"/></svg>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 14px;">Compute</div>
    <div style="font-size: 0.7em; color: #64748b; margin-top: 8px; line-height: 1.6;">GPU-driven training at scale; HPC convergence with NSF cyberinfrastructure.</div>
  </div>
  <div style="flex: 1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 22px; position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #2563eb, transparent);"></div>
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.4"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></svg>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 14px;">Data</div>
    <div style="font-size: 0.7em; color: #64748b; margin-top: 8px; line-height: 1.6;">Vast curated training datasets — chemistry, ECG archives, slide repositories.</div>
  </div>
  <div style="flex: 1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 22px; position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #2563eb, transparent);"></div>
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.4"><circle cx="12" cy="12" r="3"/><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><line x1="7" y1="7" x2="10" y2="10"/><line x1="17" y1="7" x2="14" y2="10"/><line x1="7" y1="17" x2="10" y2="14"/><line x1="17" y1="17" x2="14" y2="14"/></svg>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 14px;">Algorithms</div>
    <div style="font-size: 0.7em; color: #64748b; margin-top: 8px; line-height: 1.6;">Deep learning, graph neural networks, transformers, foundation models.</div>
  </div>
</div>

<div style="margin-top: 26px; padding: 18px 22px; background: #fff; border-left: 3px solid #2563eb; border-radius: 0 8px 8px 0;">
  <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #2563eb; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 6px;">Historical note</div>
  <div style="font-size: 0.72em; color: #475569; line-height: 1.6;">AI is not new — <strong>Stanford AI Lab (1963)</strong> and <strong>UK Department of Machine Intelligence at Edinburgh (1966)</strong> predate today's pharma applications by decades. What changed is the convergence above.</div>
</div>

---

### Cardiovascular

# AI for cardiac safety prediction

<div style="display: flex; gap: 14px; margin-top: 12px;">
  <div style="flex: 1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 20px;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.6"><circle cx="12" cy="12" r="3"/><circle cx="5" cy="6" r="1.5"/><circle cx="19" cy="6" r="1.5"/><circle cx="5" cy="18" r="1.5"/><circle cx="19" cy="18" r="1.5"/><line x1="7" y1="7" x2="10" y2="10"/><line x1="17" y1="7" x2="14" y2="10"/><line x1="7" y1="17" x2="10" y2="14"/><line x1="17" y1="17" x2="14" y2="14"/></svg>
      <span style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.6em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase;">hERG screening</span>
    </div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.95em; color: #0f172a; line-height: 1.3;">GNN &amp; QSAR<br>classifiers</div>
    <div style="font-size: 0.68em; color: #64748b; margin-top: 10px; line-height: 1.5;">High accuracy on external validation sets.</div>
    <div style="font-size: 0.6em; color: #94a3b8; margin-top: 10px;">Zhang 2022 · Xu 2025</div>
  </div>
  <div style="flex: 1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 20px;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.6"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
      <span style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.6em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase;">Torsadogenic risk</span>
    </div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.95em; color: #0f172a; line-height: 1.3;">CiPA multi-channel<br>ML classifiers</div>
    <div style="font-size: 0.68em; color: #64748b; margin-top: 10px; line-height: 1.5;">Outperform single-biomarker thresholds.</div>
    <div style="font-size: 0.6em; color: #94a3b8; margin-top: 10px;">Zhang, Tarabanis, Jethani 2024</div>
  </div>
  <div style="flex: 1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 20px;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.6"><path d="M3 12h3l3-9 4 18 3-9h5"/></svg>
      <span style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.6em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase;">Clinical ECG</span>
    </div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.95em; color: #0f172a; line-height: 1.3;">QTNet<br>QT prolongation</div>
    <div style="font-size: 0.68em; color: #64748b; margin-top: 10px; line-height: 1.5;">Drug-induced QT prediction from ECG, single-lead deep learning.</div>
    <div style="font-size: 0.6em; color: #94a3b8; margin-top: 10px;">JACC 2024 · PLOS Digit Health 2024</div>
  </div>
</div>

<div style="margin-top: 24px; padding: 14px 20px; background: #fff; border: 1px solid #eaeaea; border-radius: 8px; font-size: 0.7em; color: #475569;">
  <strong>Pattern across cardiac AI:</strong> integrate chemical structure with on- and off-target activity to stratify risk earlier in development — but most studies remain retrospective.
</div>

---

### Other Core-Battery Systems

# Beyond the heart

<div style="display: flex; flex-direction: column; gap: 10px; margin-top: 12px;">
  <div class="row" style="display: flex; align-items: center; gap: 18px; padding: 14px 18px; background: #fff; border: 1px solid #eaeaea; border-radius: 8px;">
    <div style="width: 38px; height: 38px; border-radius: 8px; background: #eff6ff; display: flex; align-items: center; justify-content: center;">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5"><path d="M12 2a4 4 0 0 0-4 4v1a4 4 0 0 0-4 4 4 4 0 0 0 1 2.6 4 4 0 0 0 0 4.4 4 4 0 0 0 4 2 4 4 0 0 0 3 1 4 4 0 0 0 3-1 4 4 0 0 0 4-2 4 4 0 0 0 0-4.4 4 4 0 0 0 1-2.6 4 4 0 0 0-4-4V6a4 4 0 0 0-4-4z"/></svg>
    </div>
    <div style="flex: 1;">
      <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.78em; color: #0f172a;">Central nervous system</div>
      <div style="font-size: 0.68em; color: #64748b; margin-top: 2px;">Blood–brain barrier permeability — masked graph transformers and LLM + ML hybrids predict from molecular structure.</div>
    </div>
    <div style="font-size: 0.6em; color: #94a3b8;">Cha 2025 · Sci Rep 2024</div>
  </div>
  <div class="row" style="display: flex; align-items: center; gap: 18px; padding: 14px 18px; background: #fff; border: 1px solid #eaeaea; border-radius: 8px;">
    <div style="width: 38px; height: 38px; border-radius: 8px; background: #eff6ff; display: flex; align-items: center; justify-content: center;">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5"><path d="M3 12c1-3 3-5 6-5s5 2 6 5-1 5-4 5-5-1-6-3z"/><path d="M14 12h7"/></svg>
    </div>
    <div style="flex: 1;">
      <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.78em; color: #0f172a;">Respiratory</div>
      <div style="font-size: 0.68em; color: #64748b; margin-top: 2px;">Unsupervised classification of plethysmography signals using advanced visual representations.</div>
    </div>
    <div style="font-size: 0.6em; color: #94a3b8;">Front Physiol 2023</div>
  </div>
  <div class="row" style="display: flex; align-items: center; gap: 18px; padding: 14px 18px; background: #fff; border: 1px solid #eaeaea; border-radius: 8px;">
    <div style="width: 38px; height: 38px; border-radius: 8px; background: #eff6ff; display: flex; align-items: center; justify-content: center;">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5"><path d="M3 12h3l2-4 4 8 2-4h7"/></svg>
    </div>
    <div style="flex: 1;">
      <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.78em; color: #0f172a;">In vitro electrophysiology</div>
      <div style="font-size: 0.68em; color: #64748b; margin-top: 2px;">ML and complex-network analysis of MEA neuronal biosensor data to characterize drug effects.</div>
    </div>
    <div style="font-size: 0.6em; color: #94a3b8;">Sci Rep 2025</div>
  </div>
  <div class="row" style="display: flex; align-items: center; gap: 18px; padding: 14px 18px; background: #fff; border: 1px solid #eaeaea; border-radius: 8px;">
    <div style="width: 38px; height: 38px; border-radius: 8px; background: #eff6ff; display: flex; align-items: center; justify-content: center;">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5"><circle cx="12" cy="8" r="4"/><path d="M5 22a7 7 0 0 1 14 0"/></svg>
    </div>
    <div style="flex: 1;">
      <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.78em; color: #0f172a;">Behavioral &amp; in vivo monitoring</div>
      <div style="font-size: 0.68em; color: #64748b; margin-top: 2px;">Computer-vision pipelines for canine activity and open-field rodent experiments — high-usability animal behavior analysis.</div>
    </div>
    <div style="font-size: 0.6em; color: #94a3b8;">Front Toxicol 2026 · Appl Sci 2024</div>
  </div>
</div>

---

### Toxicologic Pathology

# AI reads the slide

<div style="display: flex; gap: 24px; margin-top: 16px; align-items: stretch;">
  <div style="flex: 1.1; background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 24px;">
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #94a3b8; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 14px;">Headline finding</div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 1.15em; color: #0f172a; line-height: 1.3;">Deep-learning frameworks trained on large slide archives <strong>match or exceed board-certified pathologist performance</strong> in lesion identification.</div>
    <div style="margin-top: 18px; font-size: 0.66em; color: #94a3b8;">Jaume et al., 2024</div>
  </div>
  <div style="flex: 0.9; display: flex; flex-direction: column; gap: 10px;">
    <div style="background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 16px 18px;">
      <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #2563eb; letter-spacing: 0.15em; text-transform: uppercase;">Whole-slide classification</div>
      <div style="font-size: 0.7em; color: #475569; margin-top: 6px; line-height: 1.5;">Weakly supervised frameworks for digital pathology in animal studies.</div>
    </div>
    <div style="background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 16px 18px;">
      <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #2563eb; letter-spacing: 0.15em; text-transform: uppercase;">Open tooling</div>
      <div style="font-size: 0.7em; color: #475569; margin-top: 6px; line-height: 1.5;">QuPath and similar packages anchor the digital-pathology stack.</div>
    </div>
    <div style="background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 16px 18px;">
      <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #2563eb; letter-spacing: 0.15em; text-transform: uppercase;">Multi-endpoint toxicity</div>
      <div style="font-size: 0.7em; color: #475569; margin-top: 6px; line-height: 1.5;">Hepato-, nephro-, cardiotoxicity prediction from molecular features.</div>
    </div>
  </div>
</div>

<div style="margin-top: 22px; padding: 12px 20px; background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; font-size: 0.68em; color: #9a3412;">
  <strong style="color:#c2410c;">Caveat:</strong> most studies remain <em>retrospective</em>. Prospective examples where AI surfaced safety signals missed by traditional methods are still limited.
</div>

---

### SPS 2024 Survey

# Where the field actually stands

<div style="display: flex; gap: 28px; margin-top: 12px; align-items: center;">
  <div style="flex: 0 0 auto; text-align: center;">
    <svg width="220" height="220" viewBox="0 0 220 220">
      <circle cx="110" cy="110" r="90" fill="none" stroke="#e2e8f0" stroke-width="22"/>
      <circle cx="110" cy="110" r="90" fill="none" stroke="#2563eb" stroke-width="22" stroke-dasharray="565" stroke-dashoffset="273" stroke-linecap="butt" transform="rotate(-90 110 110)"/>
      <text x="110" y="105" text-anchor="middle" fill="#0f172a" font-family="Space Grotesk" font-size="38" font-weight="700">52%</text>
      <text x="110" y="128" text-anchor="middle" fill="#64748b" font-family="Inter" font-size="11" font-weight="400">using or planning AI</text>
    </svg>
    <div style="margin-top: 10px; font-size: 0.62em; color: #94a3b8; font-family: 'Space Grotesk'; letter-spacing: 0.12em; text-transform: uppercase;">N = 89 SPS members</div>
  </div>
  <div style="flex: 1;">
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #94a3b8; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 12px;">First-ever SPS AI survey · 2024 Annual Meeting</div>
    <div style="font-size: 0.78em; color: #0f172a; font-weight: 500; line-height: 1.4; margin-bottom: 14px;">Conducted in the symposium <em>"Innovative Technologies with Application to Safety Pharmacology."</em></div>
    <div style="display: flex; flex-direction: column; gap: 8px;">
      <div style="display: flex; justify-content: space-between; padding: 10px 14px; background: #fff; border: 1px solid #eaeaea; border-radius: 6px; font-size: 0.7em;">
        <span style="color: #475569;">Total respondents</span>
        <span style="font-family: 'Space Grotesk'; font-weight: 600; color: #0f172a;">N = 89</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 10px 14px; background: #eff6ff; border: 1px solid #dbeafe; border-radius: 6px; font-size: 0.7em;">
        <span style="color: #1e40af;">Reporting current or planned AI use</span>
        <span style="font-family: 'Space Grotesk'; font-weight: 600; color: #2563eb;">n = 46</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 10px 14px; background: #fff; border: 1px solid #eaeaea; border-radius: 6px; font-size: 0.7em;">
        <span style="color: #475569;">Subset answered on phase &amp; perceived impact</span>
        <span style="font-family: 'Space Grotesk'; font-weight: 600; color: #0f172a;">n = 46</span>
      </div>
    </div>
  </div>
</div>

---

### Regulatory Landscape

# Guidance is catching up

<div style="position: relative; margin-top: 24px; padding-left: 14px; border-left: 2px solid #dbeafe;">

  <div style="position: relative; padding: 12px 0 18px 26px;">
    <div style="position: absolute; left: -22px; top: 16px; width: 14px; height: 14px; border-radius: 50%; background: #fff; border: 2px solid #2563eb;"></div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #2563eb; letter-spacing: 0.15em; text-transform: uppercase;">2024</div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 4px;">EMA Reflection Paper · EU AI Act</div>
    <div style="font-size: 0.7em; color: #64748b; margin-top: 4px; line-height: 1.5;">EMA reflection paper on AI in the medicinal product lifecycle. Regulation (EU) 2024/1689 — harmonised AI rules.</div>
  </div>

  <div style="position: relative; padding: 12px 0 18px 26px;">
    <div style="position: absolute; left: -22px; top: 16px; width: 14px; height: 14px; border-radius: 50%; background: #2563eb; border: 2px solid #2563eb;"></div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #2563eb; letter-spacing: 0.15em; text-transform: uppercase;">January 2025</div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 4px;">FDA Draft Guidance · first AI-specific</div>
    <div style="font-size: 0.7em; color: #64748b; margin-top: 4px; line-height: 1.5;"><em>"Considerations for the Use of Artificial Intelligence to Support Regulatory Decision-Making for Drug and Biological Products"</em> — credibility, governance, risk management.</div>
  </div>

  <div style="position: relative; padding: 12px 0 18px 26px;">
    <div style="position: absolute; left: -22px; top: 16px; width: 14px; height: 14px; border-radius: 50%; background: #fff; border: 2px solid #2563eb;"></div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #2563eb; letter-spacing: 0.15em; text-transform: uppercase;">2025</div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 4px;">FDA Roadmap to Reducing Animal Testing</div>
    <div style="font-size: 0.7em; color: #64748b; margin-top: 4px; line-height: 1.5;">Aligned push toward in silico and AI-enabled non-clinical evaluation in preclinical safety studies.</div>
  </div>

  <div style="position: relative; padding: 12px 0 6px 26px;">
    <div style="position: absolute; left: -22px; top: 16px; width: 14px; height: 14px; border-radius: 50%; background: #fff; border: 2px solid #cbd5e1;"></div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #94a3b8; letter-spacing: 0.15em; text-transform: uppercase;">2026 onward</div>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 4px;">Guiding Principles of Good AI Practice in Drug Development</div>
    <div style="font-size: 0.7em; color: #64748b; margin-top: 4px; line-height: 1.5;">Cross-stakeholder principles emerging as the framework consolidates.</div>
  </div>

</div>

---

### Challenges

# What still has to be solved

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px;">
  <div style="background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 18px;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="1.6"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/></svg>
      <span style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.6em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase;">Data quality</span>
    </div>
    <div style="font-size: 0.7em; color: #475569; line-height: 1.55;">Domain-specific datasets are <strong>small, heterogeneous, and biased</strong> by historical screening practices.</div>
  </div>
  <div style="background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 18px;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="1.6"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      <span style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.6em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase;">Validation gaps</span>
    </div>
    <div style="font-size: 0.7em; color: #475569; line-height: 1.55;">Few <em>prospective</em> studies; most evidence is retrospective and limited to internal benchmarks.</div>
  </div>
  <div style="background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 18px;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="1.6"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
      <span style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.6em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase;">Interpretability</span>
    </div>
    <div style="font-size: 0.7em; color: #475569; line-height: 1.55;"><strong>Explainable AI</strong> remains a regulatory expectation — opaque predictions don't carry weight in safety review.</div>
  </div>
  <div style="background: #fff; border: 1px solid #eaeaea; border-radius: 10px; padding: 18px;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="1.6"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
      <span style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.6em; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase;">Implementation</span>
    </div>
    <div style="font-size: 0.7em; color: #475569; line-height: 1.55;">Regulatory acceptance, governance, and integration into established study workflows lag behind capability.</div>
  </div>
</div>

<div style="margin-top: 18px; font-size: 0.68em; color: #64748b; text-align: center; font-style: italic;">
  The community's caution is appropriate, not obstructionist.
</div>

---

### Future Directions

# Where the field is heading

<div style="display: flex; gap: 14px; margin-top: 16px;">
  <div style="flex: 1; background: linear-gradient(180deg, #eff6ff 0%, #fff 100%); border: 1px solid #dbeafe; border-radius: 10px; padding: 22px;">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15 15 0 0 1 0 20"/><path d="M12 2a15 15 0 0 0 0 20"/></svg>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 12px;">Multimodal foundation models</div>
    <div style="font-size: 0.7em; color: #475569; margin-top: 8px; line-height: 1.55;">Joint reasoning over chemical structures, assay readouts, imaging, and textual reports.</div>
  </div>
  <div style="flex: 1; background: linear-gradient(180deg, #eff6ff 0%, #fff 100%); border: 1px solid #dbeafe; border-radius: 10px; padding: 22px;">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5"><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="18" r="3"/><line x1="9" y1="6" x2="15" y2="6"/><line x1="9" y1="18" x2="15" y2="18"/><line x1="6" y1="9" x2="6" y2="15"/><line x1="18" y1="9" x2="18" y2="15"/></svg>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 12px;">Federated learning</div>
    <div style="font-size: 0.7em; color: #475569; margin-top: 8px; line-height: 1.55;">Cross-pharma model training without sharing proprietary data — e.g. <strong>MELLODDY</strong>.</div>
  </div>
  <div style="flex: 1; background: linear-gradient(180deg, #eff6ff 0%, #fff 100%); border: 1px solid #dbeafe; border-radius: 10px; padding: 22px;">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/></svg>
    <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.85em; color: #0f172a; margin-top: 12px;">Organ-on-chip + AI</div>
    <div style="font-size: 0.7em; color: #475569; margin-top: 8px; line-height: 1.55;">Integration of microphysiological systems with AI-driven readouts to advance non-animal evaluation.</div>
  </div>
</div>

<div style="margin-top: 32px; padding: 22px 26px; background: #0f172a; border-radius: 12px; text-align: center;">
  <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 0.55em; color: #60a5fa; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 10px;">Bottom line</div>
  <div style="font-family: 'Space Grotesk'; font-weight: 500; font-size: 1.1em; color: #fff; line-height: 1.4;">AI is a <span style="color: #60a5fa;">supportive computational tool</span> — not a replacement for safety-pharmacology judgment.</div>
</div>
