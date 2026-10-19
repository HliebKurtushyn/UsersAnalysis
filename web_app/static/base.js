const menuToggle = document.querySelector(".menu-toggle");
const sidebar = document.querySelector("#sidebar");

if (menuToggle && sidebar) {
  menuToggle.addEventListener("click", () => {
    const isOpen = sidebar.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
  });

  sidebar.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      sidebar.classList.remove("is-open");
      menuToggle.setAttribute("aria-expanded", "false");
    });
  });
}
