document.addEventListener("DOMContentLoaded", function () {
    const racerCheckboxes = document.querySelectorAll('input[name="racers"]');

    racerCheckboxes.forEach((checkbox) => {
        const dropdownId = checkbox.getAttribute("data-dropdown-id");
        const dropdown = document.getElementById(dropdownId);

        if (dropdown) dropdown.disabled = !checkbox.checked;

        checkbox.addEventListener("change", () => {
            if (dropdown) {
                dropdown.disabled = !checkbox.checked;
            }
        });
    });
});
