// ============================================
// GenAI Data Analytics Platform - App JavaScript
// ============================================

// Configure API base URL - defaults to localhost:8000 for local development
// For Vercel production, it will automatically use the same origin
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE_URL = isLocalhost ? "http://localhost:8000" : `${window.location.origin}/api`;
const VALID_FILE_TYPES = [".csv", ".xlsx", ".xls", ".txt", ".pdf", ".docx"];

const state = {
    currentSection: "dashboard",
    isConnected: false,
    dbConnected: false,
    currentData: null,
    currentDataset: null,
    currentQueryResult: null,
    currentSchema: null,
    chatHistory: [],
    charts: [],
    stats: {
        datasets: 0,
        queries: 0,
        charts: 0
    },
    settings: {
        theme: "light",
        openaiKey: "",
        groqKey: "",
        ollamaUrl: "http://localhost:11434",
        defaultServer: "",
        defaultDatabase: "",
        llmProvider: "openai"
    }
};

let currentChart = null;

document.addEventListener("DOMContentLoaded", () => {
    initializeApp();
});

function initializeApp() {
    loadSettings();
    setupEventListeners();
    clearChat(false);
    loadInitialData();
    checkApiStatus();
}

function setupEventListeners() {
    document.querySelectorAll(".nav-item").forEach((item) => {
        item.addEventListener("click", (event) => {
            event.preventDefault();
            navigateToSection(item.dataset.section);
        });
    });

    const sidebarToggle = document.getElementById("sidebarToggle");
    sidebarToggle.addEventListener("click", toggleSidebar);

    document.querySelectorAll(".quick-action-btn").forEach((button) => {
        button.addEventListener("click", () => {
            handleQuickAction(button.dataset.action);
        });
    });

    const uploadArea = document.getElementById("uploadArea");
    const fileInput = document.getElementById("fileInput");
    const browseBtn = document.getElementById("browseBtn");

    uploadArea.addEventListener("click", () => fileInput.click());
    browseBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        fileInput.click();
    });
    uploadArea.addEventListener("dragover", (event) => {
        event.preventDefault();
        uploadArea.classList.add("dragover");
    });
    uploadArea.addEventListener("dragleave", () => {
        uploadArea.classList.remove("dragover");
    });
    uploadArea.addEventListener("drop", handleFileDrop);
    fileInput.addEventListener("change", handleFileSelect);

    document.getElementById("dbConnectionForm").addEventListener("submit", handleDbConnection);

    const queryInput = document.getElementById("queryInput");
    document.getElementById("sendQueryBtn").addEventListener("click", sendQuery);
    queryInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && event.ctrlKey) {
            event.preventDefault();
            sendQuery();
        }
    });
    document.getElementById("clearChatBtn").addEventListener("click", () => clearChat(true));

    document.getElementById("generateChartBtn").addEventListener("click", generateChart);
    document.getElementById("settingsForm").addEventListener("submit", saveSettings);
    document.getElementById("exportResultsBtn").addEventListener("click", exportResults);

    document.querySelectorAll('input[name="theme"]').forEach((radio) => {
        radio.addEventListener("change", (event) => {
            setTheme(event.target.value);
        });
    });

    const llmProvider = document.getElementById("llmProvider");
    llmProvider.addEventListener("change", (event) => {
        state.settings.llmProvider = event.target.value;
    });

    bindExampleQueryClicks();
}

function bindExampleQueryClicks() {
    document.querySelectorAll(".example-queries li").forEach((item) => {
        item.addEventListener("click", () => {
            document.getElementById("queryInput").value = item.textContent.replaceAll('"', "").trim();
            navigateToSection("query");
        });
    });
}

function navigateToSection(section) {
    const previousSection = state.currentSection;

    document.querySelectorAll(".nav-item").forEach((item) => {
        item.classList.toggle("active", item.dataset.section === section);
    });

    document.querySelectorAll(".content-section").forEach((node) => {
        node.classList.remove("active");
    });

    const targetSection = document.getElementById(`${section}Section`);
    if (targetSection) {
        targetSection.classList.add("active");
    }

    const titles = {
        dashboard: "Dashboard",
        data: "Data Upload",
        query: "AI Query",
        visualize: "Visualizations",
        settings: "Settings"
    };

    const pageTitle = document.querySelector(".page-title");
    if (pageTitle) {
        pageTitle.textContent = titles[section] || "Dashboard";
    }

    state.currentSection = section;

    if (section === "query" && previousSection !== "query") {
        clearChat(false);
    }

    if (section === "visualize") {
        populateChartColumns();
    }
}

function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("collapsed");
}

function handleQuickAction(action) {
    const sectionMap = {
        upload: "data",
        query: "query",
        visualize: "visualize",
        export: "data"
    };

    navigateToSection(sectionMap[action] || "dashboard");
}

function handleFileDrop(event) {
    event.preventDefault();
    document.getElementById("uploadArea").classList.remove("dragover");

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

async function uploadFile(file) {
    const extension = `.${file.name.split(".").pop().toLowerCase()}`;
    if (!VALID_FILE_TYPES.includes(extension)) {
        showToast("Invalid file type. Please upload CSV, Excel, TXT, PDF, or DOCX.", "error");
        return;
    }

    const uploadProgress = document.getElementById("uploadProgress");
    const progressFill = document.getElementById("progressFill");
    const progressFilename = document.getElementById("progressFilename");
    const progressPercent = document.getElementById("progressPercent");

    uploadProgress.style.display = "block";
    progressFilename.textContent = file.name;
    progressFill.style.width = "20%";
    progressPercent.textContent = "20%";

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await apiRequest("/api/upload", {
            method: "POST",
            body: formData
        });

        progressFill.style.width = "100%";
        progressPercent.textContent = "100%";

        hydrateCurrentDataset(response.file);
        state.stats.datasets += 1;
        updateStats();

        showToast(`${response.file.filename} uploaded successfully.`, "success");
    } catch (error) {
        showToast(`Error uploading file: ${error.message}`, "error");
    } finally {
        document.getElementById("fileInput").value = "";
        setTimeout(() => {
            uploadProgress.style.display = "none";
            progressFill.style.width = "0%";
            progressPercent.textContent = "0%";
        }, 300);
    }
}

function hydrateCurrentDataset(dataset) {
    state.currentDataset = dataset;
    state.currentData = Array.isArray(dataset.preview) ? dataset.preview : null;
    state.currentQueryResult = null;

    updateUploadedFilesList(dataset);
    displayPreviewForDataset(dataset);
    populateChartColumns();
}

function displayPreviewForDataset(dataset) {
    if (!dataset || !Array.isArray(dataset.preview) || dataset.preview.length === 0) {
        document.getElementById("dataPreview").style.display = "none";
        return;
    }

    displayDataPreview(dataset.preview, dataset.row_count, dataset.column_count);
}

function displayDataPreview(rows, rowCount, columnCount) {
    const dataPreview = document.getElementById("dataPreview");
    const previewHead = document.getElementById("previewHead");
    const previewBody = document.getElementById("previewBody");
    const rowCountNode = document.getElementById("rowCount");
    const colCountNode = document.getElementById("colCount");

    if (!rows || rows.length === 0) {
        dataPreview.style.display = "none";
        return;
    }

    const columns = Object.keys(rows[0]);
    rowCountNode.textContent = rowCount ?? rows.length;
    colCountNode.textContent = columnCount ?? columns.length;

    previewHead.innerHTML = `<tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr>`;
    previewBody.innerHTML = rows.slice(0, 10).map((row) => {
        const cells = columns.map((column) => `<td>${formatCell(row[column])}</td>`).join("");
        return `<tr>${cells}</tr>`;
    }).join("");

    dataPreview.style.display = "block";
}

function updateUploadedFilesList(dataset) {
    const uploadedFiles = document.getElementById("uploadedFiles");
    const fileList = document.getElementById("fileList");

    fileList.innerHTML = "";
    uploadedFiles.style.display = "block";

    const item = document.createElement("div");
    item.className = "table-item";
    item.innerHTML = `
        <span>${escapeHtml(dataset.filename)}</span>
        <span style="margin-left: 8px; color: var(--text-muted);">
            ${escapeHtml(dataset.dataset_kind)} | ${dataset.row_count || 0} rows
        </span>
    `;

    fileList.appendChild(item);
}

async function handleDbConnection(event) {
    event.preventDefault();

    const server = document.getElementById("dbServer").value.trim();
    const database = document.getElementById("dbDatabase").value.trim();
    const username = document.getElementById("dbUsername").value.trim();
    const password = document.getElementById("dbPassword").value;

    if (!server || !database) {
        showToast("Please enter server and database name.", "warning");
        return;
    }

    showLoading(true);

    try {
        const formData = new FormData();
        formData.append("server", server);
        formData.append("database", database);
        formData.append("username", username);
        formData.append("password", password);

        const response = await apiRequest("/api/database/connect", {
            method: "POST",
            body: formData
        });

        state.dbConnected = true;
        state.isConnected = true;
        updateConnectionStatus(true);
        displayTables(response.tables || []);

        showToast(response.message || "Connected to database successfully.", "success");
    } catch (error) {
        state.dbConnected = false;
        updateConnectionStatus(false);
        showToast(`Failed to connect: ${error.message}`, "error");
    } finally {
        showLoading(false);
    }
}

function updateConnectionStatus(connected) {
    const connectionStatus = document.getElementById("connectionStatus");
    const dbStatusBadge = document.getElementById("dbStatusBadge");

    if (connected) {
        connectionStatus.innerHTML = `
            <span class="status-dot connected"></span>
            <span class="status-text">Connected</span>
        `;
        dbStatusBadge.textContent = "Connected";
        dbStatusBadge.className = "badge success";
    } else {
        connectionStatus.innerHTML = `
            <span class="status-dot disconnected"></span>
            <span class="status-text">Not Connected</span>
        `;
        dbStatusBadge.textContent = "Not Connected";
        dbStatusBadge.className = "badge danger";
    }
}

function displayTables(tables) {
    const tableExplorer = document.getElementById("tableExplorer");
    const tableList = document.getElementById("tableList");

    tableList.innerHTML = tables.map((table) => {
        const tableName = typeof table === "string" ? table : table.name;
        return `<div class="table-item" data-table="${escapeHtml(tableName)}">${escapeHtml(tableName)}</div>`;
    }).join("");

    tableList.querySelectorAll(".table-item").forEach((item) => {
        item.addEventListener("click", () => showTableSchema(item.dataset.table));
    });

    tableExplorer.style.display = "block";
}

async function showTableSchema(tableName) {
    const schemaView = document.getElementById("schemaView");
    const schemaContent = document.getElementById("schemaContent");

    try {
        const response = await apiRequest(`/api/database/tables/${encodeURIComponent(tableName)}/schema`);
        const schema = response.schema || [];

        schemaContent.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Type</th>
                        <th>Nullable</th>
                        <th>Key</th>
                    </tr>
                </thead>
                <tbody>
                    ${schema.map((column) => `
                        <tr>
                            <td>${escapeHtml(column.column)}</td>
                            <td>${escapeHtml(column.type)}</td>
                            <td>${escapeHtml(column.nullable)}</td>
                            <td>${escapeHtml(column.key)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;

        schemaView.style.display = "block";
    } catch (error) {
        showToast(`Unable to load schema: ${error.message}`, "error");
    }
}

async function sendQuery() {
    const queryInput = document.getElementById("queryInput");
    const query = queryInput.value.trim();

    if (!query) {
        showToast("Please enter a query.", "warning");
        return;
    }

    if (!state.currentDataset && !state.dbConnected) {
        showToast("Please upload data or connect to a database first.", "warning");
        return;
    }

    addChatMessage("user", query);
    queryInput.value = "";
    showLoading(true);

    try {
        const formData = new FormData();
        formData.append("prompt", query);
        formData.append("provider", state.settings.llmProvider || "openai");
        if (state.currentDataset) {
            formData.append("data_context", state.currentDataset.filename);
        }

        const response = await apiRequest("/api/query", {
            method: "POST",
            body: formData
        });

        const queryPayload = response.query;
        addChatMessage("assistant", queryPayload.answer || "Query completed.");
        displayQueryResults(queryPayload.result);

        state.currentQueryResult = Array.isArray(queryPayload.result?.data) ? queryPayload.result.data : null;
        state.stats.queries += 1;
        updateStats();
    } catch (error) {
        addChatMessage("assistant", `I could not process that request: ${error.message}`);
        showToast(`Error processing query: ${error.message}`, "error");
    } finally {
        showLoading(false);
    }
}

function addChatMessage(role, content) {
    const chatContainer = document.getElementById("chatContainer");
    const welcomeMessage = chatContainer.querySelector(".welcome-message");
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    const message = document.createElement("div");
    message.className = `chat-message ${role}`;
    message.innerHTML = `
        <div class="message-content">${renderMessageContent(content)}</div>
        <div class="message-time" style="font-size: 11px; opacity: 0.7; margin-top: 8px;">
            ${new Date().toLocaleTimeString()}
        </div>
    `;

    chatContainer.appendChild(message);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    state.chatHistory.push({
        role,
        content,
        timestamp: new Date().toISOString()
    });
}

function clearChat(showToastMessage) {
    const chatContainer = document.getElementById("chatContainer");
    const queryResults = document.getElementById("queryResults");
    const resultsContent = document.getElementById("resultsContent");

    chatContainer.innerHTML = getWelcomeMessageMarkup();
    resultsContent.innerHTML = "";
    queryResults.style.display = "none";

    state.chatHistory = [];
    state.currentQueryResult = null;

    bindExampleQueryClicks();

    if (showToastMessage) {
        showToast("Chat cleared.", "success");
    }
}

function getWelcomeMessageMarkup() {
    return `
        <div class="welcome-message">
            <div class="welcome-icon">AI</div>
            <h3>Welcome to AI Assistant!</h3>
            <p>Ask me anything about your data using natural language.</p>
            <div class="example-queries">
                <p>Try asking:</p>
                <ul>
                    <li>"Show me sales by region"</li>
                    <li>"Find customers with high spending"</li>
                    <li>"Summarize the uploaded PDF"</li>
                </ul>
            </div>
        </div>
    `;
}

function displayQueryResults(result) {
    const queryResults = document.getElementById("queryResults");
    const resultsContent = document.getElementById("resultsContent");
    const columns = Array.isArray(result?.columns) ? result.columns : [];
    const rows = Array.isArray(result?.data) ? result.data : [];

    if (columns.length === 0 || rows.length === 0) {
        queryResults.style.display = "none";
        resultsContent.innerHTML = "";
        return;
    }

    resultsContent.innerHTML = `
        <div class="table-container">
            <table>
                <thead>
                    <tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr>
                </thead>
                <tbody>
                    ${rows.map((row) => `
                        <tr>${columns.map((column) => `<td>${formatCell(row[column])}</td>`).join("")}</tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;

    queryResults.style.display = "block";
}

function getVisualizationSourceData() {
    if (Array.isArray(state.currentQueryResult) && state.currentQueryResult.length > 0) {
        return state.currentQueryResult;
    }

    if (Array.isArray(state.currentData) && state.currentData.length > 0) {
        return state.currentData;
    }

    return null;
}

function populateChartColumns() {
    const sourceData = getVisualizationSourceData();
    if (!sourceData || sourceData.length === 0) {
        return;
    }

    const columns = Object.keys(sourceData[0]);
    const options = '<option value="">Select column...</option>' +
        columns.map((column) => `<option value="${escapeAttribute(column)}">${escapeHtml(column)}</option>`).join("");

    document.getElementById("xAxis").innerHTML = options;
    document.getElementById("yAxis").innerHTML = options;
}

function generateChart() {
    const sourceData = getVisualizationSourceData();
    const chartType = document.getElementById("chartType").value;
    const xAxis = document.getElementById("xAxis").value;
    const yAxis = document.getElementById("yAxis").value;
    const chartTitle = document.getElementById("chartTitle").value || "Data Visualization";

    if (!xAxis || !yAxis) {
        showToast("Please select X and Y axis columns.", "warning");
        return;
    }

    if (!sourceData) {
        showToast("Please upload data or run a query first.", "warning");
        return;
    }

    const chartContainer = document.getElementById("chartContainer");
    if (currentChart) {
        currentChart.destroy();
    }

    if (!chartContainer.querySelector("canvas")) {
        chartContainer.innerHTML = '<canvas id="chartCanvas"></canvas>';
    }

    const labels = sourceData.map((row) => row[xAxis]);
    const values = sourceData.map((row) => {
        const numericValue = Number(row[yAxis]);
        return Number.isNaN(numericValue) ? 0 : numericValue;
    });

    const colors = [
        "rgba(99, 102, 241, 0.7)",
        "rgba(139, 92, 246, 0.7)",
        "rgba(236, 72, 153, 0.7)",
        "rgba(16, 185, 129, 0.7)",
        "rgba(245, 158, 11, 0.7)",
        "rgba(6, 182, 212, 0.7)"
    ];

    currentChart = new Chart(document.getElementById("chartCanvas").getContext("2d"), {
        type: chartType,
        data: {
            labels,
            datasets: [{
                label: yAxis,
                data: values,
                backgroundColor: chartType === "pie" ? colors : colors[0],
                borderColor: chartType === "pie" ? colors.map((color) => color.replace("0.7", "1")) : colors[0].replace("0.7", "1"),
                borderWidth: 2,
                fill: chartType === "area",
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: chartType === "pie",
                    position: "bottom"
                },
                title: {
                    display: true,
                    text: chartTitle
                }
            },
            scales: chartType === "pie" ? {} : {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    state.stats.charts += 1;
    updateStats();
    addToSavedCharts(chartTitle, chartType);
    showToast("Chart generated successfully.", "success");
}

function addToSavedCharts(title, type) {
    const savedCharts = document.getElementById("savedCharts");
    const noDataMessage = savedCharts.querySelector(".no-data");
    if (noDataMessage) {
        noDataMessage.remove();
    }

    const item = document.createElement("div");
    item.className = "saved-chart-item";
    item.innerHTML = `
        <div class="saved-chart-preview">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
        </div>
        <div style="font-weight: 500;">${escapeHtml(title)}</div>
        <div style="font-size: 12px; color: var(--text-muted);">${escapeHtml(type)} chart</div>
    `;

    savedCharts.appendChild(item);
}

function loadSettings() {
    const savedSettings = localStorage.getItem("dataai_settings");
    if (!savedSettings) {
        setTheme(state.settings.theme);
        return;
    }

    const settings = JSON.parse(savedSettings);
    Object.assign(state.settings, settings);

    document.getElementById("openaiKey").value = settings.openaiKey || "";
    document.getElementById("groqKey").value = settings.groqKey || "";
    document.getElementById("ollamaUrl").value = settings.ollamaUrl || "http://localhost:11434";
    document.getElementById("defaultServer").value = settings.defaultServer || "";
    document.getElementById("defaultDatabase").value = settings.defaultDatabase || "";
    document.getElementById("llmProvider").value = settings.llmProvider || "openai";

    setTheme(settings.theme || "light");
}

function saveSettings(event) {
    event.preventDefault();

    state.settings.openaiKey = document.getElementById("openaiKey").value;
    state.settings.groqKey = document.getElementById("groqKey").value;
    state.settings.ollamaUrl = document.getElementById("ollamaUrl").value;
    state.settings.defaultServer = document.getElementById("defaultServer").value;
    state.settings.defaultDatabase = document.getElementById("defaultDatabase").value;
    state.settings.llmProvider = document.getElementById("llmProvider").value;

    localStorage.setItem("dataai_settings", JSON.stringify(state.settings));
    showToast("Settings saved successfully.", "success");
}

function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    state.settings.theme = theme;

    const themeInput = document.querySelector(`input[name="theme"][value="${theme}"]`);
    if (themeInput) {
        themeInput.checked = true;
    }
}

async function loadInitialData() {
    updateStats();

    try {
        const response = await apiRequest("/api/datasets");
        const datasets = response.datasets || [];
        state.stats.datasets = datasets.length;
        updateStats();

        if (datasets.length > 0) {
            const activeId = response.active_dataset_id;
            const activeDataset = datasets.find((dataset) => dataset.id === activeId) || datasets[datasets.length - 1];
            hydrateCurrentDataset(activeDataset);
        }
    } catch (error) {
        console.error("Failed to load initial datasets", error);
    }
}

function updateStats() {
    document.getElementById("totalDatasets").textContent = state.stats.datasets;
    document.getElementById("queriesProcessed").textContent = state.stats.queries;
    document.getElementById("chartsGenerated").textContent = state.stats.charts;
}

async function checkApiStatus() {
    const apiStatusNode = document.querySelector(".stat-value.status-ok");

    try {
        // Try /api/health first (FastAPI default), fallback to /health
        await apiRequest("/api/health");
        state.isConnected = true;
        if (apiStatusNode) {
            apiStatusNode.textContent = "Online";
        }
    } catch (error) {
        try {
            // Fallback to /health endpoint
            await apiRequest("/health");
            state.isConnected = true;
            if (apiStatusNode) {
                apiStatusNode.textContent = "Online";
            }
        } catch (fallbackError) {
            state.isConnected = false;
            if (apiStatusNode) {
                apiStatusNode.textContent = "Offline";
            }
            showToast("API health check failed. Verify the backend is running at http://localhost:8000", "warning");
        }
    }
}

function exportResults() {
    const exportData = (Array.isArray(state.currentQueryResult) && state.currentQueryResult.length > 0)
        ? state.currentQueryResult
        : state.currentData;

    if (!exportData || exportData.length === 0) {
        showToast("No data available to export.", "warning");
        return;
    }

    const columns = Object.keys(exportData[0]);
    const csvContent = [
        columns.join(","),
        ...exportData.map((row) => columns.map((column) => csvEscape(row[column])).join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "query_results.csv";
    link.click();
    window.URL.revokeObjectURL(url);

    showToast("Data exported successfully.", "success");
}

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, options);
    let payload = {};

    try {
        payload = await response.json();
    } catch (error) {
        payload = {};
    }

    if (!response.ok || payload.success === false) {
        throw new Error(payload.error || `Request failed with status ${response.status}`);
    }

    return payload;
}

function showLoading(show) {
    const overlay = document.getElementById("loadingOverlay");
    overlay.classList.toggle("active", Boolean(show));
}

function showToast(message, type = "info") {
    const toastContainer = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    const icons = {
        success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
        error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
        warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
        info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function renderMessageContent(content) {
    return escapeHtml(String(content || "")).replace(/\n/g, "<br>");
}

function formatCell(value) {
    return escapeHtml(String(value ?? ""));
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function escapeAttribute(value) {
    return escapeHtml(value);
}

function csvEscape(value) {
    const stringValue = String(value ?? "");
    if (stringValue.includes(",") || stringValue.includes('"') || stringValue.includes("\n")) {
        return `"${stringValue.replaceAll('"', '""')}"`;
    }
    return stringValue;
}

window.showTableSchema = showTableSchema;
