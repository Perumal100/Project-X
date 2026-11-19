const consequential = /\b(send|submit|publish|post|buy|purchase|delete|remove|upload|share|invite|pay)\b/i;

async function activeTab() {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  return tab;
}

async function readActivePage() {
  const tab = await activeTab();
  if (!tab?.id) throw new Error("No active browser tab is available.");
  const [result] = await chrome.scripting.executeScript({
    target: {tabId: tab.id},
    func: () => ({title: document.title, url: location.href, text: document.body?.innerText?.slice(0, 5000) || ""}),
  });
  return result.result;
}

async function runBrowserCommand(command) {
  if (consequential.test(command)) {
    return {state: "handoff", message: "This could send, publish, buy, share, upload, or delete. RelayPilot stopped before taking that consequential action."};
  }
  const normalized = command.trim().toLowerCase();
  if (normalized.startsWith("search google ")) {
    const query = command.slice(command.toLowerCase().indexOf("search google ") + 14).trim();
    await chrome.tabs.create({url: `https://www.google.com/search?q=${encodeURIComponent(query)}`});
    return {state: "completed", message: `Opened a Google search for “${query}”.`};
  }
  if (/\b(open|go to) (gmail|google mail)\b/.test(normalized)) {
    await chrome.tabs.create({url: "https://mail.google.com/"});
    return {state: "completed", message: "Opened Gmail in your existing Chrome profile. Sign-in and account prompts remain yours."};
  }
  if (/\b(read|summari[sz]e|inspect|status|what is on)\b/.test(normalized)) {
    const page = await readActivePage();
    return {state: "completed", message: `Read the active tab: ${page.title || page.url}`, evidence: page.text.slice(0, 700) || "No readable page text."};
  }
  return {state: "blocked", message: "Use a local RelayPilot command, “search Google …”, “open Gmail”, or “read this page”."};
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.kind === "browser-run") {
    runBrowserCommand(message.command).then(sendResponse).catch(error => sendResponse({state: "blocked", message: error.message}));
    return true;
  }
  if (message.kind === "active-tab") {
    activeTab().then(tab => sendResponse({title: tab?.title || "No active tab", url: tab?.url || ""}));
    return true;
  }
});
