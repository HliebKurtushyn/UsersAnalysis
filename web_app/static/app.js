const endpointByOperation = {
  enqueue: ["/api/queue", "POST"],
  dequeue: ["/api/queue/dequeue", "DELETE"],
  push: ["/api/transactions", "POST"],
  pop: ["/api/transactions/pop", "DELETE"],
  undo: ["/api/undo", "POST"],
};

const state = {
  queue: [],
  transactions: [],
  logs: [],
  logOffset: 0,
};

function showMessage(target, message, isError = false) {
  const element = document.querySelector(`[data-message-for="${target}"]`);
  if (!element) return;
  element.textContent = message;
  element.classList.toggle("is-error", isError);
}

function renderList(target, items, isStack = false) {
  const container = document.querySelector(
    `.js-${target === "queue" ? "queue" : "transactions"}-list`,
  );
  if (!container) return;

  if (!items.length) {
    container.innerHTML = `
      <div class="empty-state">
        <strong>${isStack ? "Стек порожній" : "Черга порожня"}</strong>
        <span>${isStack ? "Додані транзакції з’являться тут." : "Наразі немає клієнтів, які очікують обслуговування."}</span>
      </div>
    `;
    return;
  }

  const visibleItems = isStack ? [...items].reverse() : items;
  container.innerHTML = `
    <ol class="item-list ${isStack ? "item-list--stack" : ""}">
      ${visibleItems
        .map(
          (item, index) => `
            <li>
              ${
                isStack && index === 0
                  ? '<span class="badge badge--accent">TOP</span>'
                  : `<span class="item-position">${index + 1}</span>`
              }
              <span>${item}</span>
            </li>
          `,
        )
        .join("")}
    </ol>
  `;
}

async function refreshStructures() {
  const [queueResponse, transactionsResponse] = await Promise.all([
    fetch("/api/queue"),
    fetch("/api/transactions"),
  ]);
  if (!queueResponse.ok || !transactionsResponse.ok) {
    throw new Error("Не вдалося завантажити стан структур.");
  }

  state.queue = (await queueResponse.json()).items;
  state.transactions = (await transactionsResponse.json()).items;
  renderList("queue", state.queue);
  renderList("transactions", state.transactions, true);
}

function renderLogs(items) {
  const list = document.querySelector("[data-log-list]");
  if (!list) return;

  if (!items.length) {
    list.innerHTML =
      '<tr><td colspan="6" class="empty-cell">Операцій ще немає.</td></tr>';
    return;
  }

  list.innerHTML = items
    .map(
      (log) => `
        <tr>
          <td>${log.timestamp ? new Date(log.timestamp).toLocaleString("uk-UA") : "—"}</td>
          <td>${log.user_id}</td>
          <td>${log.structure}</td>
          <td>${log.operation_type}</td>
          <td>${log.value}</td>
          <td>${log.description || "—"}</td>
        </tr>
      `,
    )
    .join("");
}

function logQuery(offset = 0) {
  const filters = document.querySelector("[data-log-filters]");
  const params = new URLSearchParams(
    filters
      ? [...new FormData(filters)].filter(([, value]) => value.trim())
      : [],
  );
  params.set("limit", "50");
  params.set("offset", String(offset));
  return params;
}

async function refreshLogs() {
  state.logOffset = 0;
  const response = await fetch(`/api/logs?${logQuery().toString()}`);
  if (!response.ok) throw new Error("Не вдалося завантажити журнал.");
  const result = await response.json();
  state.logs = result.items;
  state.logOffset = state.logs.length;
  renderLogs(state.logs);
  updateLoadMoreButton(result.has_more);
}

async function loadMoreLogs() {
  const response = await fetch(`/api/logs?${logQuery(state.logOffset).toString()}`);
  if (!response.ok) throw new Error("Не вдалося завантажити журнал.");
  const result = await response.json();
  state.logs = [...state.logs, ...result.items];
  state.logOffset = state.logs.length;
  renderLogs(state.logs);
  updateLoadMoreButton(result.has_more);
}

function updateLoadMoreButton(hasMore) {
  const button = document.querySelector("[data-load-more-logs]");
  if (button) button.hidden = !hasMore;
}

async function handleOperation(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const operation = form.dataset.operation;
  const target = form.dataset.target;
  const [url, method] = endpointByOperation[operation];
  const body = Object.fromEntries(new FormData(form));
  const options = { method, headers: { "Content-Type": "application/json" } };

  if (method !== "GET") options.body = JSON.stringify(body);

  try {
    const response = await fetch(url, options);
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "Операція не виконана.");
    }
    await Promise.all([refreshStructures(), refreshLogs()]);
    showMessage(target, "Операцію виконано.");
    if (operation === "enqueue" || operation === "push") form.reset();
  } catch (error) {
    showMessage(target, error.message, true);
  }
}

document.querySelectorAll(".operation-form").forEach((form) => {
  form.addEventListener("submit", handleOperation);
});

document.querySelector("[data-refresh-logs]")?.addEventListener("click", () => {
  refreshLogs().catch((error) => showMessage("logs", error.message, true));
});

document.querySelector("[data-load-more-logs]")?.addEventListener("click", () => {
  loadMoreLogs().catch((error) => showMessage("logs", error.message, true));
});

document.querySelector("[data-log-filters]")?.addEventListener("submit", (event) => {
  event.preventDefault();
  refreshLogs().catch((error) => showMessage("logs", error.message, true));
});

document.querySelector("[data-log-filters]")?.addEventListener("reset", () => {
  window.setTimeout(() => {
    refreshLogs().catch((error) => showMessage("logs", error.message, true));
  }, 0);
});

Promise.all([refreshStructures(), refreshLogs()]).catch((error) => {
  showMessage("queue", error.message, true);
  showMessage("transactions", error.message, true);
  showMessage("logs", error.message, true);
});
