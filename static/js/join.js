const joinDialog = document.querySelector("#join-dialog");
const joinTriggers = document.querySelectorAll("[data-open-join]");
let activeJoinTrigger = joinTriggers[0];

if (joinDialog && joinTriggers.length && typeof joinDialog.showModal === "function") {
  joinTriggers.forEach((trigger) => {
    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      activeJoinTrigger = trigger;
      if (!joinDialog.open) joinDialog.showModal();
    });
  });

  joinDialog.querySelector("[data-close-join]").addEventListener("click", (event) => {
    event.preventDefault();
    joinDialog.close();
  });

  joinDialog.addEventListener("click", (event) => {
    if (event.target !== joinDialog) return;
    const bounds = joinDialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right ||
        event.clientY < bounds.top || event.clientY > bounds.bottom) {
      joinDialog.close();
    }
  });

  joinDialog.addEventListener("close", () => activeJoinTrigger?.focus());

  // Upgrade the server-rendered fallback to a modal after a full-page submission.
  if (joinDialog.open) {
    joinDialog.removeAttribute("open");
    joinDialog.showModal();
  }
}
