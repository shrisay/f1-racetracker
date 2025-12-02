const html = document.querySelector("html");
const toggle = document.querySelector('#toggle-mode');

document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("theme")) {
        html.setAttribute("data-bs-theme", localStorage.getItem("theme"));
    }
    updateButton();

    toggle.addEventListener("click", () => {
        let isDark = html.getAttribute("data-bs-theme") === "dark";
        html.setAttribute("data-bs-theme", isDark ? "light" : "dark");

      updateButton();    
        localStorage.setItem("theme", isDark ? "light" : "dark");
    });

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            const submitButtons = form.querySelectorAll('button[type="submit"]');
            submitButtons.forEach(btn => {
                btn.disabled = true;
                btn.innerText = 'Submitting...';
            });
        });
    });
});

function updateButton() {
    let isDark = html.getAttribute("data-bs-theme") === "dark";
    if (isDark) {
        toggle.classList.remove("btn-dark");
        toggle.classList.add("btn-light"); 
        toggle.textContent = "☀️ Light Mode";            
    } else {
        toggle.classList.add("btn-dark");
        toggle.classList.remove("btn-success");
        toggle.textContent = "🌙 Dark Mode";
    }
}