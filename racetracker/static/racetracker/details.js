document.addEventListener('DOMContentLoaded', () => {
    const closeSeasonButton = document.querySelector('#close-season-button');
    const reopenSeasonButton = document.querySelector('#reopen-season-button');
    const closeStatus = document.querySelector('#close-status');
    const editRaceButtons = document.querySelectorAll('.edit-racename-button');
    const addRaceButton = document.querySelector('#add-race-button')
    const seasonId = document.querySelector('h1').dataset.seasonId;
    const raceNames = document.querySelectorAll('.racenames');

    raceNames.forEach(raceName => {
        raceName.addEventListener('click', event => {
            event.preventDefault();
        })
    })

    editRaceButtons.forEach(button => {
        button.addEventListener('click', event => {
            event.preventDefault();
            const raceId = button.dataset.raceId;        
            editRaceName(raceId);
        })
    })

    if (closeSeasonButton) {
        closeSeasonButton.addEventListener('click', () => {
            closeSeasonButton.disabled = true;
            fetch(`/api/season/${seasonId}/close/`, {
                method: 'PUT'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload()
                } else {
                    closeStatus.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
                    closeSeasonButton.disabled = false;
                }
            })
            .catch(error => {
                closeStatus.innerHTML = `<div class="alert alert-danger">Error: Could not close the season.</div>`;
                console.error(error);
                closeSeasonButton.disabled = false;
            });
        });
    }
    if (reopenSeasonButton) {
        reopenSeasonButton.addEventListener('click', () => {
            reopenSeasonButton.disabled = true;
            fetch(`/api/season/${seasonId}/reopen/`, {
                method: 'PUT'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload()
                } else {
                    closeStatus.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
                    reopenSeasonButton.disabled = false;
                }
            })
            .catch(error => {
                closeStatus.innerHTML = `<div class="alert alert-danger">Error: Could not reopen the season.</div>`;
                console.error(error);
                reopenSeasonButton.disabled = false;
            })            
        });
    }
    
    if (addRaceButton) {
        addRaceButton.addEventListener('click', () => {
            addRaceButton.disabled = true;
            fetch(`/api/season/${seasonId}/add/`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(`Error: ${data.error}`);
                    console.error(data.error);
                }
            })
            .catch(error => {
                console.error(error);
                addRaceButton.disabled = false;
            })
        });
    } 
});

function editRaceName(raceId) {
    const raceName = document.querySelector(`#race-name-${raceId}`);
    const originalName = raceName.innerHTML;

    const renameButton = document.querySelector(`#rename-button-${raceId}`);
    renameButton.disabled = true;

    raceName.innerHTML = 
    `<div><input id="edit-name-${raceId}" class="form-control" type="text" value="${originalName}" maxlength="128" required>
    <button id="save-name-${raceId}" class="btn btn-sm btn-primary" style="border-radius:8px">Save</button>
    <button id="cancel-name-${raceId}" class="btn btn-sm btn-danger" style="border-radius:8px">Cancel</button></div>`;

    document.querySelector(`#save-name-${raceId}`).addEventListener('click', () => {
        const newName = document.querySelector(`#edit-name-${raceId}`).value.trim();

        if (!newName) {
            alert("Race name cannot be empty.");
            return;
        }

        renameButton.disabled = false;

        fetch(`/api/race/${raceId}/rename/`, {
            method: 'PUT',
            body: JSON.stringify({ new_name: newName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                raceName.innerHTML = newName;
            }
        })
        .catch(error => console.error(error));
    });

    document.querySelector(`#cancel-name-${raceId}`).addEventListener('click', () => {
        raceName.innerHTML = originalName;
        renameButton.disabled = false;
    });
}