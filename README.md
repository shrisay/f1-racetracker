# Racetracker

Racetracker is a Django-based web application that allows users to simulate and manage motorsport-style competitions. Users can add races, assign qualifying and race results, award points, and view live season standings for racers and constructors. The app supports features like pole positions, wins, podiums, dynamic season stats, and championship closures.

## Distinctiveness and Complexity

Racetracker is built to go well beyond the scope of basic database operations. Rather than simply collecting and displaying user-submitted data, this app models the intricacies of a competitive motorsport season. From enforcing real-world constraints in qualifying and race logic, to dynamically updating and displaying championship standings, this project was designed to mimic an actual competition.

Races can be created and deleted, with appropriate editing of the database, counting a racer's points, wins, podiums, pole positions and number of races.

One complexity is the accurate handling of race results and qualification logic. The application enforces constraints like no duplicate racer placements, disallowing ordering finished racers behind DNFs, and syncing eligible participants between qualifying and race rounds. Special care was taken to avoid side effects: no stats are committed unless the entire result form is valid. Edge cases, such as entering too few or duplicate racers are handled gracefully.

Another feature is the season closure mechanism. Upon clicking “Finish Competition,” the application calculates and freezes winners by checking for ties and applying appropriate tiebreaker logic, updating permanent stats such as championship counts, and disabling further modification of the competition until the user reopens it. This is a feature that involved frontend and backend coordination, JavaScript fetch calls and REST APIs.

This app also has a night/day mode toggle that persists via localStorage, and all actions are protected behind ownership checks. Forms dynamically adjust based on earlier inputs, such as participant limits.

## File Overview

* `views.py`: All view functions, including race creation, result saving, and API views for finishing/reopening seasons.
* `models.py`: Contains Django models for Racer, Constructor, Season, Race, QualifyingResult, RaceResult, and many-to-many bridge models with custom stats.
* `urls.py`: Defines application URLs, including frontend routes and API endpoints.
* `templates/`: Contains all HTML templates:

  * `layout.html`: Base layout
  * `index.html`: User dashboard
  * `create.html`: For adding new competitions
  * `details.html`: Season overview with race list and stats toggle
  * `race.html`: View individual race
  * `qualifying_form.html`, `race_form.html`, `set_participants.html`: Forms for entering results and setting participants
  * `login.html`, `register.html`: Forms for registering and logging into the users' accounts
* `static/`:

  * `layout.js`: Handles light/dark mode and form submission protection
  * `details.js`: JS logic for race name editing, race creation, and season close/reopen
* `admin.py`: Admin registration for all models

## How to Run

1. Clone the repository:

   ```bash
   git clone --branch web50/projects/2020/x/capstone https://github.com/me50/shrisay.git
   cd shrisay
   ```

2. Install Django (and any other dependencies):

   ```bash
   pip install django
   ```

3. Apply migrations:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Create a superuser to access the admin panel (optional):

   ```bash
   python manage.py createsuperuser
   ```

5. Run the server:

   ```bash
   python manage.py runserver
   ```

6. Visit `http://127.0.0.1:8000/` on your web browser to start using Racetracker.

## Additional Notes

* Every logged-in user has their own set of seasons, racers, and constructors.
* No season can be closed unless it has races and results.
* Race names can be renamed in-place using the Edit feature.
* The application prevents race result errors such as blank fields, duplicates, or invalid DNF placements.
* Only racers who participated in qualifying can be included in races, and this constraint is enforced throughout the app.
* Season stats update in real time and championships are declared only upon closing the season.

---

This project was created as the final capstone for CS50's Web Programming with Python and JavaScript (CS50W).
