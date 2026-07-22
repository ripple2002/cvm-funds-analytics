const API_URL = "http://localhost:8000";

const fundForm = document.getElementById("fund-form");
const fundMessage = document.getElementById("fund-message");

const summarySection = document.getElementById("summary-section");
const historySection = document.getElementById("history-section");

const historyBody = document.getElementById("history-body");

const rankingButton = document.getElementById("ranking-button");
const rankingMessage = document.getElementById("ranking-message");
const rankingContainer = document.getElementById("ranking-container");
const rankingBody = document.getElementById("ranking-body");


function normalizeCnpj(value) {
    return value.replace(/\D/g, "");
}


function formatCurrency(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return Number(value).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
    });
}


function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined) {
        return "-";
    }

    return Number(value).toLocaleString("pt-BR", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    });
}


function formatInteger(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return Number(value).toLocaleString("pt-BR");
}


function formatPercentage(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return Number(value).toLocaleString("pt-BR", {
        style: "percent",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}


function formatDate(value) {
    if (!value) {
        return "-";
    }

    const datePart = value.split("T")[0];
    const [year, month, day] = datePart.split("-");

    return `${day}/${month}/${year}`;
}


function setMessage(element, text, type = "") {
    element.textContent = text;
    element.className = type;
}


async function requestJson(url) {
    const response = await fetch(url);

    let data;

    try {
        data = await response.json();
    } catch {
        throw new Error("A API retornou uma resposta inválida.");
    }

    if (!response.ok) {
        throw new Error(
            data.detail || "Erro ao consultar a API."
        );
    }

    return data;
}


function createQueryString(startDate, endDate) {
    const params = new URLSearchParams();

    if (startDate) {
        params.append("start_date", startDate);
    }

    if (endDate) {
        params.append("end_date", endDate);
    }

    return params.toString();
}


function renderSummary(summary) {
    document.getElementById("quota").textContent =
        formatNumber(summary.latest.quota, 8);

    document.getElementById("net-asset-value").textContent =
        formatCurrency(summary.latest.net_asset_value);

    document.getElementById("shareholders").textContent =
        formatInteger(summary.latest.shareholders);

    document.getElementById("period-return").textContent =
        formatPercentage(summary.indicators.period_return);

    document.getElementById("net-flow").textContent =
        formatCurrency(summary.indicators.net_flow);

    summarySection.classList.remove("hidden");
}


function renderHistory(history) {
    historyBody.innerHTML = "";

    history.data.forEach((item) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${formatDate(item.date)}</td>
            <td>${formatNumber(item.quota, 8)}</td>
            <td>${formatCurrency(item.net_asset_value)}</td>
            <td>${formatCurrency(item.subscriptions)}</td>
            <td>${formatCurrency(item.redemptions)}</td>
            <td>${formatCurrency(item.net_flow)}</td>
            <td>${formatInteger(item.shareholders)}</td>
        `;

        historyBody.appendChild(row);
    });

    historySection.classList.remove("hidden");
}


function renderRanking(ranking) {
    rankingBody.innerHTML = "";

    ranking.data.forEach((fund) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${fund.position}</td>
            <td>${fund.denominacao_social || "-"}</td>
            <td>${fund.cnpj || "-"}</td>
            <td>${formatCurrency(fund.vl_patrim_liq)}</td>
            <td>${formatInteger(fund.nr_cotst)}</td>
            <td>${formatDate(fund.dt_comptc)}</td>
        `;

        rankingBody.appendChild(row);
    });

    rankingContainer.classList.remove("hidden");
}


fundForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const cnpj = normalizeCnpj(
        document.getElementById("cnpj").value
    );

    const startDate =
        document.getElementById("start-date").value;

    const endDate =
        document.getElementById("end-date").value;

    if (cnpj.length !== 14) {
        setMessage(
            fundMessage,
            "O CNPJ deve possuir 14 dígitos.",
            "error"
        );

        return;
    }

    if (startDate && endDate && startDate > endDate) {
        setMessage(
            fundMessage,
            "A data inicial não pode ser posterior à data final.",
            "error"
        );

        return;
    }

    summarySection.classList.add("hidden");
    historySection.classList.add("hidden");

    setMessage(fundMessage, "Carregando...");

    const queryString = createQueryString(
        startDate,
        endDate
    );

    const summaryUrl =
        `${API_URL}/funds/${cnpj}/summary` +
        (queryString ? `?${queryString}` : "");

    const historyUrl =
        `${API_URL}/funds/${cnpj}/history` +
        (queryString ? `?${queryString}` : "");

    try {
        const [summary, history] = await Promise.all([
            requestJson(summaryUrl),
            requestJson(historyUrl),
        ]);

        renderSummary(summary);
        renderHistory(history);

        setMessage(
            fundMessage,
            "Consulta concluída.",
            "success"
        );
    } catch (error) {
        setMessage(
            fundMessage,
            error.message,
            "error"
        );
    }
});


rankingButton.addEventListener("click", async () => {
    rankingContainer.classList.add("hidden");

    setMessage(
        rankingMessage,
        "Carregando ranking..."
    );

    try {
        const ranking = await requestJson(
            `${API_URL}/analytics/ranking?limit=10`
        );

        renderRanking(ranking);

        setMessage(
            rankingMessage,
            "Ranking carregado.",
            "success"
        );
    } catch (error) {
        setMessage(
            rankingMessage,
            error.message,
            "error"
        );
    }
});