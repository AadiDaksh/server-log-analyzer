const fileInput =
    document.getElementById(
        "fileInput"
    );

const browseButton =
    document.getElementById(
        "browseButton"
    );

const dropZone =
    document.getElementById(
        "dropZone"
    );

const uploadSection =
    document.getElementById(
        "uploadSection"
    );

const dashboard =
    document.getElementById(
        "dashboard"
    );

const message =
    document.getElementById(
        "message"
    );

const liveButton =
    document.getElementById(
        "liveButton"
    );

const liveStatus =
    document.getElementById(
        "liveStatus"
    );


let liveSocket = null;
let requestChart = null;
let statusChart = null;

liveButton.addEventListener(
    "click",
    () => {
        if (liveSocket) {
            stopLiveMonitoring();
        }
        else {
            startLiveMonitoring();
        }
    }
);

browseButton.addEventListener(
    "click",
    event => {
        event.stopPropagation();

        fileInput.click();
    }
);


dropZone.addEventListener(
    "click",
    () => {
        fileInput.click();
    }
);


fileInput.addEventListener(
    "change",
    () => {
        if (
            fileInput.files.length
            > 0
        ) {
            uploadLog(
                fileInput.files[0]
            );
        }
    }
);


dropZone.addEventListener(
    "dragover",
    event => {
        event.preventDefault();

        dropZone.classList.add(
            "dragging"
        );
    }
);


dropZone.addEventListener(
    "dragleave",
    () => {
        dropZone.classList.remove(
            "dragging"
        );
    }
);


dropZone.addEventListener(
    "drop",
    event => {
        event.preventDefault();

        dropZone.classList.remove(
            "dragging"
        );

        if (
            event.dataTransfer
                .files.length > 0
        ) {
            uploadLog(
                event.dataTransfer
                    .files[0]
            );
        }
    }
);

function startLiveMonitoring() {
    const protocol =
        window.location.protocol
        === "https:"
            ? "wss"
            : "ws";

    const socketUrl =
        `${protocol}://${window.location.host}/ws/live`;

    liveSocket =
        new WebSocket(
            socketUrl
        );


    liveSocket.onopen = () => {
        liveButton.textContent =
            "Stop Live";

        liveButton.classList.add(
            "active"
        );

        liveStatus.classList.remove(
            "hidden"
        );

        uploadSection.classList.add(
            "hidden"
        );

        dashboard.classList.remove(
            "hidden"
        );


        document.getElementById(
            "filename"
        ).textContent =
            "logs/live.log";

        document.getElementById(
            "detectedFormat"
        ).textContent =
            "Waiting...";

        document.getElementById(
            "parsedCount"
        ).textContent =
            "0";

        document.getElementById(
            "ignoredCount"
        ).textContent =
            "—";
    };


    liveSocket.onmessage = event => {
        const data =
            JSON.parse(
                event.data
            );

        if (
            data.type !==
            "dashboard_update"
        ) {
            return;
        }

        renderLiveDashboard(
            data
        );
    };


    liveSocket.onerror = () => {
        console.error(
            "WebSocket error"
        );
    };


    liveSocket.onclose = () => {
        liveSocket = null;

        liveButton.textContent =
            "Start Live";

        liveButton.classList.remove(
            "active"
        );

        liveStatus.classList.add(
            "hidden"
        );
    };
}


function stopLiveMonitoring() {
    if (liveSocket) {
        liveSocket.close();
    }
}

function renderLiveDashboard(data) {
    const dashboardData =
        data.dashboard;

    const summary =
        dashboardData.summary;


    document.getElementById(
        "detectedFormat"
    ).textContent =
        data.format;


    document.getElementById(
        "parsedCount"
    ).textContent =
        data.parsed_requests;


    document.getElementById(
        "totalRequests"
    ).textContent =
        summary.total_requests
            .toLocaleString();


    document.getElementById(
        "successRate"
    ).textContent =
        `${summary.success_rate}%`;


    document.getElementById(
        "errorRate"
    ).textContent =
        `${summary.error_rate}%`;


    document.getElementById(
        "p95Latency"
    ).textContent =
        formatLatency(
            summary.latency.p95
        );


    document.getElementById(
        "averageLatency"
    ).textContent =
        formatLatency(
            summary.latency.average
        );


    document.getElementById(
        "p50Latency"
    ).textContent =
        formatLatency(
            summary.latency.p50
        );


    document.getElementById(
        "latencyP95"
    ).textContent =
        formatLatency(
            summary.latency.p95
        );


    document.getElementById(
        "p99Latency"
    ).textContent =
        formatLatency(
            summary.latency.p99
        );


    document.getElementById(
        "maxLatency"
    ).textContent =
        formatLatency(
            summary.latency.max
        );


    updateHealth(
        summary,
        dashboardData.endpoints
    );


    renderEndpoints(
        dashboardData.endpoints
    );


    renderProblems(
        dashboardData
            .recent_problems
    );


    renderRequestChart(
        dashboardData
            .requests_over_time
    );


    renderStatusChart(
        dashboardData
            .status_codes
    );
}

async function uploadLog(file) {
    message.classList.remove(
        "error"
    );

    message.textContent =
        `Analyzing ${file.name}...`;

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    try {
        const response =
            await fetch(
                "/api/analyze",
                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail
                || "Analysis failed."
            );
        }

        renderDashboard(
            data
        );

        message.textContent = "";
    }

    catch (error) {
        message.classList.add(
            "error"
        );

        message.textContent =
            error.message;
    }
}


function formatLatency(value) {
    if (
        value === null
        || value === undefined
    ) {
        return "N/A";
    }

    return `${value}ms`;
}


function renderDashboard(data) {
    uploadSection.classList.add(
        "hidden"
    );

    dashboard.classList.remove(
        "hidden"
    );

    document.getElementById(
        "filename"
    ).textContent =
        data.filename;

    document.getElementById(
        "parsedCount"
    ).textContent =
        data.parsed_requests;

    document.getElementById(
        "ignoredCount"
    ).textContent =
        data.ignored_lines;

    document.getElementById(
        "detectedFormat"
    ).textContent =
        Object.keys(
            data.formats
        ).join(", ");


    const dashboardData =
        data.dashboard;

    const summary =
        dashboardData.summary;


    document.getElementById(
        "totalRequests"
    ).textContent =
        summary.total_requests
            .toLocaleString();


    document.getElementById(
        "successRate"
    ).textContent =
        `${summary.success_rate}%`;


    document.getElementById(
        "errorRate"
    ).textContent =
        `${summary.error_rate}%`;


    document.getElementById(
        "p95Latency"
    ).textContent =
        formatLatency(
            summary.latency.p95
        );


    document.getElementById(
        "averageLatency"
    ).textContent =
        formatLatency(
            summary.latency.average
        );


    document.getElementById(
        "p50Latency"
    ).textContent =
        formatLatency(
            summary.latency.p50
        );


    document.getElementById(
        "latencyP95"
    ).textContent =
        formatLatency(
            summary.latency.p95
        );


    document.getElementById(
        "p99Latency"
    ).textContent =
        formatLatency(
            summary.latency.p99
        );


    document.getElementById(
        "maxLatency"
    ).textContent =
        formatLatency(
            summary.latency.max
        );


    updateHealth(
        summary,
        dashboardData.endpoints
    );


    renderEndpoints(
        dashboardData.endpoints
    );


    renderProblems(
        dashboardData
            .recent_problems
    );


    renderRequestChart(
        dashboardData
            .requests_over_time
    );


    renderStatusChart(
        dashboardData
            .status_codes
    );
}


function updateHealth(
    summary,
    endpoints
) {
    const element =
        document.getElementById(
            "overallHealth"
        );

    const critical =
        endpoints.some(
            endpoint =>
                endpoint.health
                === "Critical"
        );

    const warning =
        endpoints.some(
            endpoint =>
                endpoint.health
                === "Warning"
                ||
                endpoint.health
                === "Slow"
        );

    element.className =
        "health-pill";

    if (
        critical
        || summary.error_rate >= 10
    ) {
        element.textContent =
            "Critical";

        element.classList.add(
            "critical"
        );
    }

    else if (
        warning
        || summary.error_rate >= 5
    ) {
        element.textContent =
            "Warning";

        element.classList.add(
            "warning"
        );
    }

    else {
        element.textContent =
            "Healthy";

        element.classList.add(
            "healthy"
        );
    }
}


function renderEndpoints(
    endpoints
) {
    const table =
        document.getElementById(
            "endpointTable"
        );

    table.innerHTML = "";

    endpoints.forEach(
        endpoint => {
            const row =
                document.createElement(
                    "tr"
                );

            const healthClass =
                endpoint.health
                    .toLowerCase();

            row.innerHTML = `
                <td class="method">
                    ${escapeHtml(
                        endpoint.method
                    )}
                </td>

                <td class="endpoint">
                    ${escapeHtml(
                        endpoint.endpoint
                    )}
                </td>

                <td>
                    ${endpoint.requests}
                </td>

                <td>
                    ${endpoint.error_rate}%
                </td>

                <td>
                    ${formatLatency(
                        endpoint
                            .average_latency
                    )}
                </td>

                <td>
                    ${formatLatency(
                        endpoint
                            .p95_latency
                    )}
                </td>

                <td>
                    <span
                        class="badge ${healthClass}"
                    >
                        ${endpoint.health}
                    </span>
                </td>
            `;

            table.appendChild(
                row
            );
        }
    );
}


function renderProblems(
    problems
) {
    const table =
        document.getElementById(
            "problemTable"
        );

    table.innerHTML = "";

    if (problems.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="6">
                    No problems detected.
                </td>
            </tr>
        `;

        return;
    }

    problems.forEach(
        problem => {
            const row =
                document.createElement(
                    "tr"
                );

            const issueClass =
                problem.issue
                === "Slow Request"

                ? "slow-request"
                : "problem";

            row.innerHTML = `
                <td>
                    ${escapeHtml(
                        problem.timestamp
                    )}
                </td>

                <td class="method">
                    ${escapeHtml(
                        problem.method
                    )}
                </td>

                <td class="endpoint">
                    ${escapeHtml(
                        problem.endpoint
                    )}
                </td>

                <td>
                    ${problem.status}
                </td>

                <td>
                    ${formatLatency(
                        problem
                            .response_time
                    )}
                </td>

                <td>
                    <span
                        class="badge ${issueClass}"
                    >
                        ${escapeHtml(
                            problem.issue
                        )}
                    </span>
                </td>
            `;

            table.appendChild(
                row
            );
        }
    );
}


function renderRequestChart(
    data
) {
    if (requestChart) {
        requestChart.destroy();
    }

    requestChart =
        new Chart(
            document.getElementById(
                "requestChart"
            ),
            {
                type: "line",

                data: {
                    labels:
                        data.map(
                            item =>
                                item.time
                        ),

                    datasets: [
                        {
                            label:
                                "Requests",

                            data:
                                data.map(
                                    item =>
                                        item.requests
                                ),

                            borderWidth: 2,

                            tension: 0.3,

                            fill: false
                        }
                    ]
                },

                options: {
                    responsive: true,

                    maintainAspectRatio:
                        false,

                    plugins: {
                        legend: {
                            display: false
                        }
                    },

                    scales: {
                        y: {
                            beginAtZero:
                                true,

                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            }
        );
}


function renderStatusChart(
    data
) {
    if (statusChart) {
        statusChart.destroy();
    }

    statusChart =
        new Chart(
            document.getElementById(
                "statusChart"
            ),
            {
                type: "doughnut",

                data: {
                    labels:
                        data.map(
                            item =>
                                String(
                                    item.status
                                )
                        ),

                    datasets: [
                        {
                            data:
                                data.map(
                                    item =>
                                        item.count
                                )
                        }
                    ]
                },

                options: {
                    responsive: true,

                    maintainAspectRatio:
                        false
                }
            }
        );
}


function escapeHtml(value) {
    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );
}