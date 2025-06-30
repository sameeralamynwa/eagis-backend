window.searchFilter = function searchFilter(event) {
  if (event.key === "Enter") {
    const url = new URL(window.location);
    url.searchParams.set("search", event.target.value);
    url.searchParams.delete("page");
    location.href = url.href;
  }
};

window.record_per_page = function handle_per_page(event) {
  const url = new URL(window.location);
  url.searchParams.set("per_page", event.target.value);
  url.searchParams.delete("search");
  url.searchParams.delete("page");
  location.href = url.href;
};

window.deleteTableRecord = function deleteTableRecord(button, url, csrf) {
  button.disabled = true;
  const originalText = button.innerText;
  button.innerText = "Deleting...";

  const formData = new FormData();
  formData.append("csrf_token", csrf);
  fetch(url, {
    method: "DELETE",
    body: formData,
    redirect: "manual",
  })
    .then((res) => {
      location.reload();
    })
    .catch(() => {
      alert("Network error");
    })
    .finally(() => {
      button.disabled = false;
      button.innerText = originalText;
    });
};
