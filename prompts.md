# DEV_PROMPTS.md

## Raspberry Pi Scheduled Website Blocker — Agent Prompts

This document contains task-specific prompts for developers or AI agents working on the project. Each prompt targets a distinct functionality or component of the system.

---

### 1. System Initialization & Project Setup

> You are a Python backend engineer. Set up a new Flask (or FastAPI) project that will run on a Raspberry Pi. Include basic routing, static file support, and systemd service creation so the app starts at boot. Ensure Python 3.11+ compatibility and lightweight footprint.

---

### 2. AdGuard API Wrapper

> You are a Python developer working with AdGuard Home. Create a class that interacts with the AdGuard Home API to:
> - Add domains to blocklist
> - Remove domains from blocklist
> - Check current block status for a domain
> Use a configuration file or env variables to store AdGuard credentials and URL.

---

### 3. Domain Scheduling Logic

> You are building a background job service using Python (preferably APScheduler). Write code that:
> - Checks current time every minute
> - Compares it with stored schedules per domain
> - Calls AdGuard wrapper to block/unblock accordingly
> - Logs every change with timestamp
> All schedules are recurring daily (start time → end time).

---

### 4. Web UI - Authentication

> You are a full-stack developer. Create a login screen for a web app using Flask + Jinja2 templates (or React frontend if preferred). Use hardcoded or config-based login credentials for MVP. After login, redirect to dashboard. Use session-based authentication.

---

### 5. Web UI - Domain & Schedule Management

> Design a UI form for users to:
> - Enter a domain (e.g., youtube.com)
> - Pick start and end time using a visual time picker (HTML5 or JavaScript)
> - Toggle schedule on/off
> Also, create a table view showing all current domain schedules with edit/delete/toggle buttons.
> Use Flask or a lightweight frontend framework.

---

### 6. Storage Layer (Schedule + Logs)

> You are a Python backend developer. Implement a lightweight storage system using SQLite or JSON to:
> - Save domain names, start/end times, toggle status
> - Record history logs of block/unblock actions
> Ensure thread-safe acce
