# UX Validation — task outcomes and evidence

A successful click is not the same as a user successfully understanding or
completing a task. Identify audience, context, desired outcome, and likely
mistakes, then author scripts in JSON (see `templates/ux-tasks.example.json`).

```bash
python scripts/ux_scenarios.py validate templates/ux-tasks.example.json
python scripts/ux_scenarios.py run site.html my-tasks.json --out /tmp/task-qa --width 390
```

The runner checks the browser actions/DOM assertions you explicitly wrote.
It can simulate navigation, content checks, buttons, forms and focus states;
it **does not** automatically know whether participants understand a page.
For actual user-task evaluation, observe representative people and record
completion rate, time, misunderstanding, hesitation and recovery separately.
Do not manufacture such observations from browser scripts or model simulation.
