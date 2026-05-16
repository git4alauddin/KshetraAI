# Build Execution Prompt

Use this prompt when implementing any KshetraAI build from `docs/implementation/`.

This prompt is shared across all builds. Do not copy this full prompt into individual build docs. Each build doc should only define its own scope, task breakdown, allowed files, forbidden files, and completion checklist.

---

# 1. Required Inputs

Before starting a build task, read the relevant files in this order:

1. `docs/architecture/09_development_plan.md`
2. The specific build doc from `docs/implementation/`
3. The matching implementation contract from `docs/implementation_contracts/`
4. `docs/implementation_contracts/00_global_implementation_protocol.md`
5. Any architecture docs referenced by the build doc
6. Any source data dictionary referenced by the build doc

If the documents conflict, follow this authority order:

```text
Architecture docs
Implementation contracts
Specific build doc
This shared execution prompt
Task request
```

---

# 2. Work One Task At A Time

Do not implement an entire build in one pass unless the human explicitly asks for that.

For each task in the build breakdown:

1. Present the exact task heading.
2. Briefly state what will be changed.
3. Briefly state which files are expected to be touched.
4. Briefly state what will remain untouched.
5. Wait for explicit implementation approval.

The task heading should be suitable as the future commit heading.

---

# 3. Task Kickoff Format

Use this format before implementation:

```text
Commit heading:
<exact task heading>

Brief:
<one or two short sentences explaining what this task will add or change>

Expected file scope:
<specific files or folders>

Not touching:
<important forbidden areas for this task>
```

Stop after this kickoff unless the human has already explicitly asked you to implement.

---

# 4. Implementation Rules

During implementation:

- Follow only the active task scope.
- Modify only files allowed by the build doc.
- Do not modify `private-data/`.
- Do not commit or push.
- Do not run destructive git commands.
- Preserve deterministic behavior.
- Preserve explainability and traceability.
- Keep implementation lightweight and aligned with the current scaffold.
- Do not introduce downstream logic from later builds.
- Do not redesign architecture or contracts unless explicitly asked.
- Add tests when the task changes executable behavior.
- Keep outputs stable in naming, ordering, and schema.

---

# 5. Completion Response After Implementation

After implementing a task, report:

- What changed
- Files touched
- How the change stays inside the build boundary
- What verification was run, or why verification was not run
- Any remaining risk or follow-up inside the same build

Do not include a commit block unless the human asks for it.

---

# 6. Commit Block Rule

When the human asks for the commit block, provide only the commands needed to stage and commit the relevant files.

Do not include `git status`.

Use the task heading as the commit message unless the human asks for a different message.

Example:

```bash
git add <relevant files>
git commit -m "<task heading>"
```

---

# 7. After The Human Commits

When the human says the commit is done:

1. Verify the committed change if asked or if verification is part of the workflow.
2. Confirm the task matches the build doc and contract.
3. Mark or recommend marking the relevant checklist item as complete.
4. Propose the next task from the build breakdown.

Do not move to the next task silently.

---

# 8. Definition Of Done Discipline

A task is complete only when:

- The requested behavior is implemented.
- The relevant build checklist item can be honestly checked.
- The implementation stays within the allowed file scope.
- The implementation does not introduce later-build behavior.
- Tests or verification are appropriate for the risk of the change.
- The user has enough information to review and commit intentionally.

