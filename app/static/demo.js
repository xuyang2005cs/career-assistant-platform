const sampleJobDescription = `Company: Example Tech
Role: Python Backend Intern
Location: Beijing

Requirements:
Python, FastAPI, SQL, Git, Linux`;

const state = { jobs: [], extraction: null, sourceText: "" };
const elements = {
  jobsBody: document.querySelector("#jobs-body"),
  resultCount: document.querySelector("#result-count"),
  statusFilter: document.querySelector("#status-filter"),
  keywordFilter: document.querySelector("#keyword-filter"),
  jdText: document.querySelector("#jd-text"),
  preview: document.querySelector("#preview"),
  previewTitle: document.querySelector("#preview-title-input"),
  previewCompany: document.querySelector("#preview-company"),
  previewLocation: document.querySelector("#preview-location"),
  skillList: document.querySelector("#skill-list"),
  extractionMethod: document.querySelector("#extraction-method"),
  fallbackNote: document.querySelector("#fallback-note"),
  toast: document.querySelector("#toast"),
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const payload = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    const message = payload?.error?.message || `Request failed with status ${response.status}`;
    throw new Error(message);
  }
  return payload;
}

function showToast(message, isError = false) {
  elements.toast.textContent = message;
  elements.toast.classList.toggle("error", isError);
  elements.toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => { elements.toast.hidden = true; }, 3500);
}

function updateMetrics(jobs) {
  const counts = jobs.reduce((summary, job) => {
    summary[job.status] = (summary[job.status] || 0) + 1;
    return summary;
  }, {});
  document.querySelector("#metric-total").textContent = jobs.length;
  for (const status of ["saved", "applied", "interview", "offer"]) {
    document.querySelector(`#metric-${status}`).textContent = counts[status] || 0;
  }
}

function renderJobs() {
  const status = elements.statusFilter.value;
  const keyword = elements.keywordFilter.value.trim().toLowerCase();
  const visibleJobs = state.jobs.filter((job) => {
    const statusMatches = !status || job.status === status;
    const keywordMatches = !keyword || [job.title, job.company, job.location || ""]
      .some((value) => value.toLowerCase().includes(keyword));
    return statusMatches && keywordMatches;
  });

  if (!visibleJobs.length) {
    elements.jobsBody.innerHTML = '<tr><td colspan="4" class="table-message">No jobs match these filters.</td></tr>';
  } else {
    elements.jobsBody.replaceChildren(...visibleJobs.map((job) => {
      const row = document.createElement("tr");
      for (const value of [job.title, job.company, job.location || "—"]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.append(cell);
      }
      const statusCell = document.createElement("td");
      const pill = document.createElement("span");
      pill.className = `status-pill status-${job.status}`;
      pill.textContent = job.status;
      statusCell.append(pill);
      row.append(statusCell);
      return row;
    }));
  }
  elements.resultCount.textContent = `Showing ${visibleJobs.length} of ${state.jobs.length} jobs`;
}

async function loadJobs() {
  try {
    const result = await api("/api/v1/jobs?page=1&page_size=100");
    state.jobs = result.items;
    updateMetrics(state.jobs);
    renderJobs();
  } catch (error) {
    elements.jobsBody.innerHTML = '<tr><td colspan="4" class="table-message">Jobs could not be loaded.</td></tr>';
    showToast(error.message, true);
  }
}

function methodLabel(method) {
  return {
    rule_based: "Rule-based · offline",
    rule_based_fallback: "Rule-based fallback",
    deepseek: "DeepSeek",
    mock: "Mock · development",
  }[method] || method;
}

function renderExtraction(result) {
  state.extraction = result;
  elements.previewTitle.value = result.title || "";
  elements.previewCompany.value = result.company || "";
  elements.previewLocation.value = result.location || "";
  elements.extractionMethod.textContent = methodLabel(result.extraction_method);
  elements.skillList.replaceChildren(...(result.skills.length ? result.skills : ["No skills detected"]).map((skill) => {
    const chip = document.createElement("span");
    chip.className = "skill-chip";
    chip.textContent = skill;
    return chip;
  }));
  if (result.fallback_reason) {
    elements.fallbackNote.textContent = `Primary provider was unavailable (${result.fallback_reason}); the offline extractor completed this preview.`;
    elements.fallbackNote.hidden = false;
  } else {
    elements.fallbackNote.hidden = true;
  }
  elements.preview.hidden = false;
  elements.preview.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

async function extractJob() {
  const text = elements.jdText.value.trim();
  if (!text) {
    showToast("Paste a job description before extracting.", true);
    elements.jdText.focus();
    return;
  }
  const button = document.querySelector("#extract-job");
  button.disabled = true;
  button.textContent = "Extracting…";
  try {
    state.sourceText = text;
    const result = await api("/api/v1/job-extract", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    renderExtraction(result);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
    button.textContent = "Extract job";
  }
}

async function saveJob() {
  const title = elements.previewTitle.value.trim();
  const company = elements.previewCompany.value.trim();
  if (!title || !company) {
    showToast("Title and company are required before saving.", true);
    return;
  }
  const button = document.querySelector("#save-job");
  button.disabled = true;
  button.textContent = "Saving…";
  try {
    const job = await api("/api/v1/jobs", {
      method: "POST",
      body: JSON.stringify({
        title,
        company,
        location: elements.previewLocation.value.trim() || null,
        description: state.sourceText,
        source_url: null,
        status: "saved",
      }),
    });
    showToast(`${job.title} saved to the tracker.`);
    await loadJobs();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
    button.textContent = "Save to job tracker";
  }
}

document.querySelector("#use-sample").addEventListener("click", () => {
  elements.jdText.value = sampleJobDescription;
  elements.jdText.focus();
});
document.querySelector("#extract-job").addEventListener("click", extractJob);
document.querySelector("#save-job").addEventListener("click", saveJob);
document.querySelector("#refresh-jobs").addEventListener("click", loadJobs);
elements.statusFilter.addEventListener("change", renderJobs);
elements.keywordFilter.addEventListener("input", renderJobs);

loadJobs();
