const sampleJobDescription = `Company: Example Tech
Role: Python 后端开发实习生
Location: 北京

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
    const message = payload?.error?.message || `请求失败，HTTP 状态码：${response.status}`;
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
    elements.jobsBody.innerHTML = '<tr><td colspan="4" class="table-message">没有符合当前筛选条件的岗位。</td></tr>';
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
      pill.textContent = statusLabel(job.status);
      statusCell.append(pill);
      row.append(statusCell);
      return row;
    }));
  }
  elements.resultCount.textContent = `当前显示 ${visibleJobs.length} 个，共 ${state.jobs.length} 个岗位`;
}

async function loadJobs() {
  try {
    const result = await api("/api/v1/jobs?page=1&page_size=100");
    state.jobs = result.items;
    updateMetrics(state.jobs);
    renderJobs();
  } catch (error) {
    elements.jobsBody.innerHTML = '<tr><td colspan="4" class="table-message">岗位数据加载失败，请稍后重试。</td></tr>';
    showToast(error.message, true);
  }
}

function methodLabel(method) {
  return {
    rule_based: "规则解析",
    rule_based_fallback: "规则解析（自动切换）",
    deepseek: "DeepSeek",
    mock: "测试 Provider",
  }[method] || method;
}

function statusLabel(status) {
  return {
    saved: "已收藏",
    applied: "已投递",
    interview: "面试中",
    offer: "已录用",
    rejected: "未通过",
    closed: "已结束",
  }[status] || status;
}

function renderExtraction(result) {
  state.extraction = result;
  elements.previewTitle.value = result.title || "";
  elements.previewCompany.value = result.company || "";
  elements.previewLocation.value = result.location || "";
  elements.extractionMethod.textContent = methodLabel(result.extraction_method);
  elements.skillList.replaceChildren(...(result.skills.length ? result.skills : ["未识别到技能关键词"]).map((skill) => {
    const chip = document.createElement("span");
    chip.className = "skill-chip";
    chip.textContent = skill;
    return chip;
  }));
  if (result.fallback_reason) {
    elements.fallbackNote.textContent = `外部 Provider 当前不可用（${result.fallback_reason}），已切换为规则解析。`;
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
    showToast("请先粘贴职位描述。", true);
    elements.jdText.focus();
    return;
  }
  const button = document.querySelector("#extract-job");
  button.disabled = true;
  button.textContent = "正在提取…";
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
    button.textContent = "提取岗位信息";
  }
}

async function saveJob() {
  const title = elements.previewTitle.value.trim();
  const company = elements.previewCompany.value.trim();
  if (!title || !company) {
    showToast("保存前请填写职位名称和公司。", true);
    return;
  }
  const button = document.querySelector("#save-job");
  button.disabled = true;
  button.textContent = "正在保存…";
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
    showToast(`已保存岗位：${job.title}`);
    await loadJobs();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
    button.textContent = "保存岗位";
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
