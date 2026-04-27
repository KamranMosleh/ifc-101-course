# Streamlit IFC Pages Guide

This guide explains what each page in the app does, where each tab gets its information, and how the app uses ifcOpenShell under the hood.

## Table of Contents

- [Who This Guide Is For](#who-this-guide-is-for)
- [Quick IFC and BIM Basics](#quick-ifc-and-bim-basics)
- [Run the app](#run-the-app)
- [Recommended Workflow](#recommended-workflow)
- [Tech Stack](#tech-stack)
- [ifcOpenShell Interactions in This App](#ifcopenshell-interactions-in-this-app)
- [Common Questions](#common-questions)
  - [What does "model health" mean in this app?](#what-does-model-health-mean-in-this-app)
  - [What are inverse attributes and inverse references?](#what-are-inverse-attributes-and-inverse-references)
  - [What do Inspect From Id and Inspect from Model do?](#what-do-inspect-from-id-and-inspect-from-model-do)
  - [Which ID type should I use in Viewer/Health debug?](#which-id-type-should-i-use-in-viewerhealth-debug)
  - [Are app IDs related to GUID/GlobalId?](#are-app-ids-related-to-guidglobalid)
  - [Why not use GlobalId for Inspect buttons?](#why-not-use-globalid-for-inspect-buttons)
  - [Why did I see "Instance with GlobalId '458' not found"?](#why-did-i-see-instance-with-globalid-458-not-found)
  - [Do Add Schedule buttons save to IFC, and can I download the result?](#do-add-schedule-buttons-save-to-ifc-and-can-i-download-the-result)
- [Page Guide](#page-guide)
  - [Home](#home)
  - [Viewer](#viewer)
    - [Viewer Tab: Properties](#viewer-tab-properties)
    - [Viewer Tab: Debugger](#viewer-tab-debugger)
  - [Quantities](#quantities)
    - [Quantities Tab: DataFrame Utilities](#quantities-tab-dataframe-utilities)
    - [Quantities Tab: Quantities Review](#quantities-tab-quantities-review)
  - [Health](#health)
    - [Health Tab: Debug](#health-tab-debug)
    - [Health Tab: Charts](#health-tab-charts)
    - [Health Tab: Schedules](#health-tab-schedules)
    - [Health Sidebar: Add Schedule Buttons and Save](#health-sidebar-add-schedule-buttons-and-save)
      - [Add Cost Schedule Button](#add-cost-schedule-button)
      - [Add Work Schedule Button](#add-work-schedule-button)
      - [Save File Button](#save-file-button)
- [Practical Notes](#practical-notes)
- [Short Summary](#short-summary)

## Who This Guide Is For

- BIM users who need a practical map of the app.
- Developers and analysts who are new to IFC files.
- Anyone who wants to inspect model objects, quantities, and schedules in one workflow.

## Quick IFC and BIM Basics

- BIM combines 3D geometry with data about building elements.
- IFC is the open exchange format used to share BIM data.
- IFC files are made of entities (for example `IfcWall`, `IfcDoor`, `IfcTask`) and relationships.
- STEP entity references look like `#123` in the IFC text file.
- In this app, ID inputs use the numeric entity ID, so for `#123` you enter `123`.
- `GlobalId` is a different identifier (GUID-style string) used for cross-tool identity.
- Property sets (Psets) describe metadata. Quantity sets (Qto) describe measurable values.
- Work schedules are timeline-oriented (4D). Cost schedules are cost-oriented (5D).

## Run the app

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start Streamlit:

```bash
streamlit run Homepage.py
```

3. Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Recommended Workflow

1. Open Home and upload an IFC file.
2. Open Viewer to inspect geometry and selected object data.
3. Open Quantities for tabular and quantity review.
4. Open Health for diagnostics, charts, and schedules.

The app is session-based. If no IFC file is uploaded on Home, other pages will have limited or no data.

## Tech Stack

- UI: Streamlit multipage app.
- IFC processing: ifcOpenShell.
- 3D viewer: IFC.js + Three.js via a custom Streamlit component.
- Data processing: pandas.
- Charts: Plotly and Matplotlib.
- Export: CSV and Excel (`xlsxwriter`).

## ifcOpenShell Interactions in This App

This section summarizes where ifcOpenShell reads and writes happen.

- Parse uploaded IFC text into model object:
  - `ifcopenshell.file.from_string(...)` in Home.
- Entity lookup by ID:
  - `session.ifc_file.by_id(step_id)` in Viewer Debugger and Health Debug.
- Query entities by class:
  - `session.ifc_file.by_type(...)` for classes such as `IfcBuildingElement`, `IfcWorkSchedule`, `IfcTask`, `IfcCostSchedule`, `IfcCostItem`.
- Read inverse relationships:
  - `session.ifc_file.get_inverse(entity)` in debug inspectors.
- Add schedules (write operations):
  - `ifcopenshell.api.run("sequence.add_work_schedule", ...)`
  - `ifcopenshell.api.run("cost.add_cost_schedule", ...)`
- Save edited model back to disk:
  - `session.ifc_file.write(session.file_name)`.

## Common Questions

### What does "model health" mean in this app?

It means model diagnostics and data checks, not structural analysis.

On the Health page, "health" mainly means:

- Can I inspect entities and their relationships?
- What types of objects dominate the model?
- Are work schedules, tasks, and cost schedules present?

### What are inverse attributes and inverse references?

- **Inverse attributes**: reverse relationship fields for an entity (who points to this object and through which IFC relation).
- **Inverse references**: the concrete list of entities that reference the current entity.

In short: inverse attributes describe the reverse links; inverse references list the linked objects.

### What do Inspect From Id and Inspect from Model do?

- **Inspect From Id**: uses the value you type in Object ID.
- **Inspect from Model**: uses the ID of the object you selected in the 3D viewer.

Both buttons load the same debug content: direct attributes, inverse attributes, inverse references, and clickable linked objects.

### Which ID type should I use in Viewer/Health debug?

Use **STEP/Express numeric ID** (for example, `458`).

- `#458` in the IFC text corresponds to `458` in the app input.
- `GlobalId` is not the expected debug input type in these pages.

### Are app IDs related to GUID/GlobalId?

Yes, they can refer to the same object, but they are different systems:

- STEP/Express ID: integer, local to IFC model instance, used for fast interactive lookup.
- GlobalId: GUID-like stable ID for interoperability across tools/files.

The app uses STEP/Express IDs for debug actions because viewer selection and `by_id(...)` lookup are integer-based and immediate.

### Why not use GlobalId for Inspect buttons?

Because the inspect workflow is built around:

- IFC.js selection IDs (Express IDs), and
- ifcOpenShell `by_id(...)` lookup.

Also, not every inspectable entity is equally practical to traverse by GlobalId in this interactive debug flow.

### Why did I see "Instance with GlobalId '458' not found"?

That happens when the input is treated as text (GlobalId-style) instead of numeric STEP ID.

The Health inspect flow now normalizes values like `458`, `#458`, and `458.0` to integer STEP IDs and shows friendly warnings if the entity is missing.

### Do Add Schedule buttons save to IFC, and can I download the result?

- **Add Schedule** buttons modify the in-memory IFC model.
- **Save File** writes that updated model to disk (`session.ifc_file.write(session.file_name)`).

Current behavior is save-to-disk on the running machine. There is no dedicated browser download button for the modified IFC in this app version.

## Page Guide

### Home

Home initializes the session model.

Main functions:

- Upload IFC into session state.
- Parse IFC into an in-memory ifcOpenShell model.
- Reset cached analysis data when a new model is loaded.
- Show project name and allow quick project-name update in memory.

### Viewer

Viewer handles geometry display and selection-driven inspection.

Main functions:

- Send uploaded IFC bytes to the embedded IFC.js component.
- Display model geometry in 3D.
- Return selected object payload from IFC.js to Streamlit.
- Let users inspect selected or manually entered IDs.

#### Viewer Tab: Properties

Where data comes from:

- Source: IFC.js selection payload stored in `session.ifc_js_response`.
- Flow: selection in 3D viewer -> JSON payload -> parsed by `get_psets_from_ifc_js()` -> formatted by `format_ifc_js_psets(...)`.

What is shown:

- Property and quantity groups for the selected object.

#### Viewer Tab: Debugger

Where data comes from:

- Source model: `session.ifc_file` (ifcOpenShell model in session).
- Lookup method: `session.ifc_file.by_id(step_id)`.

ID type used:

- STEP/Express entity ID (integer). Example: `#456` in IFC file -> enter `456` in app input.

Buttons and behavior:

- Object ID input + **Inspect From Id**:
  - Uses the typed ID and fetches entity details from `session.ifc_file`.
- **Inspect from Model**:
  - Uses selected object ID coming from IFC.js viewer payload.
- **Get Object** buttons:
  - Follow linked entity IDs from attributes/inverse references.

What is shown:

- Direct attributes.
- Inverse attributes.
- Inverse references.

### Quantities

Quantities provides DataFrame-based review built from IFC model extraction.

Shared source for both Quantities tabs:

- `session.ifc_file` (ifcOpenShell model) -> `ifchelper.get_objects_data_by_class(session.ifc_file, "IfcBuildingElement")` -> `ifchelper.create_pandas_dataframe(...)` -> `session.DataFrame`.

This means Quantities is focused on `IfcBuildingElement` extraction, not every IFC class in the file.

#### Quantities Tab: DataFrame Utilities

Where data comes from:

- Directly from `session.DataFrame` built in `load_data()`.

What is shown and done:

- Full extracted DataFrame display.
- CSV export and Excel export of that DataFrame.

#### Quantities Tab: Quantities Review

Where data comes from:

- Starts from the same `session.DataFrame`.
- Filter by class via `pandashelper.filter_dataframe_per_class(...)`.
- Detect quantity sets via `pandashelper.get_qsets_columns(...)`.
- Detect quantities via `pandashelper.get_quantities(...)`.
- Build chart via `graph_maker.load_graph(...)`.

What is shown:

- Quantity charts split by Level or Type.
- If quantity is `Count`, total count is shown instead of chart.

### Health

Health provides diagnostics, charts, and schedule review/editing.

Shared load sequence:

- `load_data()` prepares:
  - `session.Graphs` (chart figures)
  - `session.SequenceData` (work schedule/task data)
  - `session.CostData` (cost schedule/item data)

#### Health Tab: Debug

Where data comes from:

- Source model: `session.ifc_file`.
- Lookup: `session.ifc_file.by_id(...)`.
- Inverse links: `session.ifc_file.get_inverse(entity)`.

ID type used:

- STEP/Express entity ID (integer), same as Viewer Debugger.

What is shown:

- Entity attributes.
- Inverse attributes.
- Inverse references.
- Linked entity navigation with Get Object buttons.

#### Health Tab: Charts

Where data comes from:

- Chart 1: building element class counts from `graph_maker.get_elements_graph(session.ifc_file)`.
- Chart 2: high-frequency entity types from `graph_maker.get_high_frequency_entities_graph(session.ifc_file)`.

Both are computed from the currently loaded IFC model.

#### Health Tab: Schedules

Where data comes from:

- Work schedules: `session.ifc_file.by_type("IfcWorkSchedule")`.
- Tasks: `session.ifc_file.by_type("IfcTask")` and recursive traversal by `ifchelper.get_schedule_tasks(...)`.
- Task table formatting: `ifchelper.get_task_data(...)`.
- Cost schedules: `session.ifc_file.by_type("IfcCostSchedule")`.
- Cost item presence check: `session.ifc_file.by_type("IfcCostItem")`.

What is shown:

- Work schedule list and selected schedule task details.
- Cost schedule list.
- Warning when no cost items exist.

Current button behavior in this tab:

- Adding a **Work Schedule** creates a schedule container with the entered name, but it does not automatically create tasks.
- Adding a **Cost Schedule** creates a schedule container with the entered name, but it does not automatically create cost items.
- Because of this, a newly created schedule may appear as empty until related tasks or cost items are added later.

#### Health Sidebar: Add Schedule Buttons and Save

##### Add Cost Schedule Button

- Trigger: sidebar button linked to `add_cost_schedule()`.
- Data used:
  - Current in-memory IFC model (`session.ifc_file`).
  - Text input value (`session.cost_input`) used as schedule name.
- Action:
  - Calls `ifchelper.create_cost_schedule(...)` which runs `ifcopenshell.api.run("cost.add_cost_schedule", ...)`.
- After action:
  - Reloads cost schedule data for display.

##### Add Work Schedule Button

- Trigger: sidebar button linked to `add_work_schedule()`.
- Data used:
  - Current in-memory IFC model (`session.ifc_file`).
  - Text input value (`session.schedule_input`) used as schedule name.
- Action:
  - Calls `ifchelper.create_work_schedule(...)` which runs `ifcopenshell.api.run("sequence.add_work_schedule", ...)`.
- After action:
  - Reloads work schedule data for display.

##### Save File Button

- Writes the current edited in-memory IFC model to disk using:
  - `session.ifc_file.write(session.file_name)`.

## Practical Notes

- Always load file in Home first.
- Viewer Debugger and Health Debug use the same ID type (STEP/Express integer ID).
- Viewer Debugger supports both manual ID inspection and model-selection inspection.
- Quantities is intentionally element-focused (`IfcBuildingElement`).
- Health is the page with the strongest editing impact due to schedule creation and file saving.

## Short Summary

- Home loads and initializes the IFC model in session.
- Viewer shows geometry and selection-driven object data.
- Quantities builds a DataFrame from IFC building elements and supports quantity analysis.
- Health reads diagnostics and schedules from IFC, and can add schedules and save edits.
