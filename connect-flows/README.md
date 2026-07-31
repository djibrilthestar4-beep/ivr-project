# Connect Flows

Exported Amazon Connect contact flows, version-controlled as JSON.

## Why this exists

Amazon Connect flows are authored visually in the console — there's no
native "write flow as code" option. This folder + the export/import
scripts give you a way to track history, diff changes, and review flow
edits via pull requests, even though the actual editing still happens in
the visual designer.

## Workflow

**Making a change to a flow:**

1. Edit the flow in the Amazon Connect console as usual, then **Save** (and **Publish** if it's ready to go live).
2. Pull the updated content into this repo:
   ```bash
   python scripts/export_flows.py --instance-id <INSTANCE_ID> --name "MainMenu"
   ```
3. Review the diff:
   ```bash
   git diff connect-flows/main-menu.json
   ```
4. Commit it:
   ```bash
   git add connect-flows/main-menu.json
   git commit -m "Update MainMenu: add Spanish language option"
   ```

**Rolling back or pushing a saved version to a different environment (e.g. dev → staging):**

1. Make sure `connect-flows/<flow>.json` has the `ContactFlowId` for the
   *target* instance (each Connect instance has its own IDs for what may
   be "the same" flow conceptually — see note below).
2. Preview first:
   ```bash
   python scripts/import_flows.py --instance-id <INSTANCE_ID> --file connect-flows/main-menu.json --dry-run
   ```
3. Apply it:
   ```bash
   python scripts/import_flows.py --instance-id <INSTANCE_ID> --file connect-flows/main-menu.json
   ```

## Important: flows are per-instance

A `ContactFlowId` is scoped to one Connect instance. If you have separate
dev/staging/prod Connect instances, the "same" flow will have a
**different** `ContactFlowId` in each one. This means:

- You generally can't take a dev-exported JSON file and blindly import it
  into prod — the `ContactFlowId` won't match a flow that exists there.
- The common pattern is: create the flow once in each environment via the
  console (so each gets its own ID), export each to confirm the IDs, then
  use `import_flows.py` going forward to push *content* updates to each
  environment's matching ID.
- Keeping a small mapping (e.g. in `config/dev.env` / `config/prod.env`)
  of flow name → ContactFlowId per environment helps avoid mixing these up.

## File format

Each exported file looks like:

```json
{
  "Name": "MainMenu",
  "Type": "CONTACT_FLOW",
  "Description": "",
  "ContactFlowId": "arn-or-id-here",
  "Content": { ... the actual flow definition ... }
}
```

`Content` is the flow logic itself (blocks, branches, prompts). `Name`,
`Type`, and `ContactFlowId` are metadata used by `import_flows.py` to know
which flow to update.
