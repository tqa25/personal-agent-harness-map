# Personal Agent Harness

This context defines the domain language for a personal AI agent system built on top of the current harness scaffold.

## Language

**Personal Copilot**:
An AI assistant that helps one primary user think, research, summarize, plan, and draft work while leaving consequential real-world actions under the user's control.
_Avoid_: Personal OS, task executor, autonomous employee

**Primary User**:
The person the Personal Copilot is designed to serve and remember preferences for. In this project, there is exactly one Primary User.
_Avoid_: customer, account, tenant

**Harness**:
The runtime wrapper around the model that provides tools, planning, memory, session state, and web search.
_Avoid_: app, bot, model

**Tool**:
A capability the Personal Copilot can call to fetch facts, inspect systems, compute values, or prepare actions.
_Avoid_: plugin, integration, command

**Action**:
A change outside the conversation, such as sending a message, editing a document, creating a calendar event, committing code, or moving a file.
_Avoid_: response, suggestion, tool call

**Draft**:
Output prepared for the Primary User to review before it becomes an Action.
_Avoid_: final send, automatic action

**Technical Work**:
Work where the Personal Copilot helps the Primary User understand, change, test, document, or review software projects.
_Avoid_: generic productivity, office work

**Personal Knowledge Work**:
Work where the Personal Copilot helps the Primary User read, organize, summarize, connect, and reuse notes, documents, learnings, and research material.
_Avoid_: file storage, generic memory

**Working Preference**:
A durable preference about how the Primary User wants technical work, explanations, plans, documentation, or reviews to be performed.
_Avoid_: temporary instruction, one-off request

**Repo Learning**:
A durable fact learned from working in the repository, such as a recurring error, architectural decision, important convention, feature request, or verified solution.
_Avoid_: chat transcript, incidental observation

**V1 Scope**:
The first useful version of the Personal Copilot, focused on Technical Work and Personal Knowledge Work before communication automation or life scheduling.
_Avoid_: everything assistant, full personal OS

**V1 Complete**:
The milestone where the Personal Copilot has a CLI Work Surface, mandatory Web Research with Source Comparison, Repository Edit capability, a Memory Surface, and a Backlog of Local Issues.
_Avoid_: prototype, full personal OS

**Repository Knowledge**:
The code, tests, documentation, learnings, issues, and decision records stored inside the current repository and treated as the primary local source of truth for V1.
_Avoid_: all local files, cloud drive, private inbox

**Current Repository**:
The single repository where the Personal Copilot performs V1 Technical Work, Repository Edits, Memory Writes, Verification Runs, and Local Issues.
_Avoid_: workspace, all repos, remote repository

**Memory Surface**:
The repository-backed place where Working Preferences and Repo Learnings are stored so future sessions can reuse them.
_Avoid_: hidden model memory, private black box

**Learnings File**:
The Memory Surface file for reusable discoveries, conventions, solutions, and confirmed Working Preferences that should influence future sessions in the Current Repository.
_Avoid_: changelog, scratch notes

**Errors File**:
The Memory Surface file for recurring errors, failed attempts, root causes, and verified fixes.
_Avoid_: test output dump, incident log

**Feature Requests File**:
The Memory Surface file for desired future capabilities of the Personal Copilot or repository.
_Avoid_: implementation plan, issue tracker replacement

**Local Issue**:
A repository-backed markdown task that is concrete enough for the Personal Copilot or another agent to implement independently.
_Avoid_: vague idea, feature request, chat todo

**Backlog**:
The collection of Local Issues that represent implementation-ready work for the Personal Copilot system.
_Avoid_: memory surface, todo list

**Knowledge Output**:
The durable result of Personal Knowledge Work. Reusable knowledge becomes a Memory Write, while implementation-ready follow-up work becomes a Local Issue.
_Avoid_: extra document by default, chat-only knowledge

**Codex Issues Directory**:
The repository location `.codex/issues/` where Local Issues for the Backlog are stored as markdown files.
_Avoid_: docs folder, learnings folder

**Memory Write**:
An Action that updates the Memory Surface. Repo Learnings and recurring errors may be written automatically; Working Preferences require confirmation from the Primary User before they become durable.
_Avoid_: hidden memory update, automatic preference inference

**Web Research**:
Fresh external research performed through web search when Repository Knowledge is missing, stale, or needs outside validation. Web Research is mandatory in V1 for current facts, library behavior, public documentation, and external references.
_Avoid_: model memory, cached knowledge, general browsing

**Search Provider**:
The replaceable Web Research backend that performs external search and source retrieval. V1 defaults to Microsoft hosted web search when available, but the Personal Copilot should not treat one provider as permanent.
_Avoid_: hard-coded search API, browser

**Source Comparison**:
The default quality bar for Web Research. The Personal Copilot should inspect multiple relevant sources, prefer official documentation or primary sources, and state which sources support the answer.
_Avoid_: single-link answer, uncited summary, model recall

**Source Conflict**:
A Web Research result where relevant sources disagree, are stale relative to each other, or support different conclusions. The Personal Copilot should surface the conflict, prefer primary sources, state confidence, and avoid pretending certainty.
_Avoid_: forced conclusion, silent source selection

**Research Learning**:
A Repo Learning produced from Web Research that is likely to be useful again, such as official documentation behavior, a verified fix, a technology decision input, or an important external reference.
_Avoid_: every search result, temporary citation

**Autonomy Level**:
The current permission mode that defines how far the Personal Copilot may go without stopping for approval. V1 defaults to editing files in the repository, while higher levels can allow commits, pushes, PRs, or broader automation when explicitly selected.
_Avoid_: safety mode, permissions, aggressiveness

**Edit Mode**:
The default Autonomy Level for V1. The Personal Copilot may perform Repository Edits and run verification, but Delivery Actions require approval or a higher mode.
_Avoid_: safe mode, read-write mode

**Deliver Mode**:
An Autonomy Level where the Personal Copilot may perform Repository Edits and Delivery Actions that are directly requested by the Primary User.
_Avoid_: deploy mode, publish mode

**Auto Mode**:
An Autonomy Level where the Personal Copilot may choose and perform Repository Edits and Delivery Actions it judges necessary for the current goal, within explicitly configured boundaries.
_Avoid_: unrestricted mode, full access

**Repository Edit**:
An Action that changes code, tests, documentation, or configuration inside the current repository.
_Avoid_: suggestion, draft

**Delivery Action**:
An Action that publishes work outside the local working tree, such as committing, pushing, creating a pull request, enabling Pages, or deploying.
_Avoid_: repository edit, local change

**Work Surface**:
The interface where the Primary User gives tasks to the Personal Copilot and receives working output. V1 uses a CLI Work Surface.
_Avoid_: dashboard, landing page

**Status Page**:
A static page that explains the current system structure, scope, and missing capabilities for the Primary User. It is not the Work Surface.
_Avoid_: app UI, chat interface

**Status Page Update**:
An update to the Status Page made when the system's scope, architecture, glossary, or major decisions change enough that the current page would mislead the Primary User.
_Avoid_: changelog entry, routine task output

**Task Intake**:
The moment the Primary User gives the Personal Copilot a task. V1 uses free-form Task Intake and only asks follow-up questions when the task is ambiguous, risky, or requires a higher Autonomy Level.
_Avoid_: mandatory task form, rigid workflow selector

**Plan Approval**:
The Primary User's confirmation of a short proposed plan before the Personal Copilot executes a large, ambiguous, or risky task.
_Avoid_: full specification, automatic execution

**Completion Report**:
The summary the Personal Copilot gives after finishing work. It should state what changed, which files matter, what verification ran, and any blocker or residual risk.
_Avoid_: verbose transcript, hidden test result

**Verification Run**:
The checks performed after Repository Edits, including relevant tests and any static checks defined by the repository. If no relevant check exists, the Personal Copilot must say so in the Completion Report.
_Avoid_: confidence without tests, silent verification

**Secret Configuration**:
Local credentials or API keys needed by the Personal Copilot, such as model provider or Search Provider keys. Secret Configuration may be written to `.env.local` only after Primary User approval and must not be committed.
_Avoid_: committed secret, hidden credential write

## Example Dialogue

Developer: "Should the agent send emails by itself?"

Domain Expert: "No. As a Personal Copilot, it may write a Draft, but sending the email is an Action and needs explicit user approval."

Developer: "Can it remember how I like reports formatted?"

Domain Expert: "Yes. That is a preference for the Primary User and belongs in memory."

Developer: "Should it remember every detail from every conversation?"

Domain Expert: "No. It should store Working Preferences and Repo Learnings that are likely to matter again."

Developer: "What should happen after a useful knowledge task?"

Domain Expert: "Reusable knowledge should become a Memory Write. Concrete follow-up work should become a Local Issue."

Developer: "Where should everyday memory go?"

Domain Expert: "Use `.learnings/LEARNINGS.md`, `.learnings/ERRORS.md`, and `.learnings/FEATURE_REQUESTS.md` as the Memory Surface. Keep `CONTEXT.md` for language and ADRs for major decisions."

Developer: "Where do confirmed Working Preferences live in V1?"

Domain Expert: "In `.learnings/LEARNINGS.md` inside the Current Repository. V1 does not use a global preference store."

Developer: "What is the difference between a feature request and a local issue?"

Domain Expert: "A Feature Request can be a rough idea. A Local Issue is concrete enough to implement and belongs in the Backlog."

Developer: "Where do implementation-ready local issues live?"

Domain Expert: "In the Codex Issues Directory, `.codex/issues/`, as markdown files."

Developer: "Can the copilot decide that something is my preference?"

Domain Expert: "It can propose a Working Preference, but a Memory Write for that preference needs confirmation from the Primary User."

Developer: "Should v1 manage my calendar and send messages?"

Domain Expert: "No. V1 Scope is Technical Work and Personal Knowledge Work. Calendar and messaging can come later."

Developer: "When is v1 actually complete?"

Domain Expert: "When the copilot can work from the CLI, research the web with source comparison, edit the repo, write reusable memory, and track implementation-ready local issues."

Developer: "If the repo has no answer about a current library or article, should the copilot guess?"

Domain Expert: "No. It should use Web Research and cite the source instead of relying on model memory."

Developer: "Does v1 work across many local repos?"

Domain Expert: "No. V1 is limited to the Current Repository. Multi-repo support can be revisited after the single-repo workflow is solid."

Developer: "Is web research tied forever to Microsoft hosted search?"

Domain Expert: "No. Microsoft hosted search is the V1 default Search Provider, but the system should be able to swap providers."

Developer: "Is one search result enough?"

Domain Expert: "Not by default. Web Research should use Source Comparison, especially for current technical facts or recommendations."

Developer: "What if two sources disagree?"

Domain Expert: "Treat it as a Source Conflict. Explain the disagreement, prefer primary sources, and state confidence instead of hiding the uncertainty."

Developer: "Should web research always be written into memory?"

Domain Expert: "No. Only reusable Research Learnings should become Memory Writes."

Developer: "Can the copilot edit files?"

Domain Expert: "Yes, when the Autonomy Level allows Repository Edit. Delivery Actions require a higher Autonomy Level or explicit approval."

Developer: "How does the user choose how much autonomy the copilot has?"

Domain Expert: "There is a default Autonomy Level in configuration, and the Primary User can change it during a session."

Developer: "Is the HTML page where the user works with the copilot?"

Domain Expert: "No. V1 uses the CLI as the Work Surface. The static page is a Status Page for explanation and visibility."

Developer: "Should every small code change update the Status Page?"

Domain Expert: "No. A Status Page Update is needed only when the current page would misrepresent the system."

Developer: "Does the user need to choose a task type every time?"

Domain Expert: "No. Task Intake is free-form. The copilot should infer the task type and ask only when it affects execution."

Developer: "Should the copilot plan before every tiny edit?"

Domain Expert: "No. Plan Approval is for large, ambiguous, or risky tasks. Small clear edits can proceed under the current Autonomy Level."

Developer: "What should the user see after work finishes?"

Domain Expert: "A Completion Report with the relevant changes, verification, and unresolved risks. The length should match the task size."

Developer: "Can the copilot finish a repository edit without mentioning tests?"

Domain Expert: "No. It must run a relevant Verification Run or explicitly report why verification was not available."

Developer: "Can the copilot save API keys by itself?"

Domain Expert: "No. Secret Configuration can be written to `.env.local` only after Primary User approval and must stay out of git."
