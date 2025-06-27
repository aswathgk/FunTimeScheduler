# Raspberry Pi Scheduled Website Blocker — MVP Requirement Document

## Overview

A web-based application running on a Raspberry Pi (already configured as the network’s DNS server and running AdGuard) that allows users to **block specific websites** based on **daily recurring time schedules**. The app serves as a wrapper around **AdGuard's API** to manage DNS filtering dynamically.

---

## Functional Requirements

### 1. Website Blocking

* Users can input one or more URLs (domains) to block.
* Each website can have its **own recurring daily schedule**.
* Blocking/unblocking is achieved via **AdGuard Home's API**.

### 2. Scheduling

* Users define schedules using a **visual time picker UI** (start time and end time).
* Each website's schedule can be **enabled/disabled** without deleting it.
* The app runs a background service that checks the schedule and updates AdGuard accordingly.

### 3. Authentication

* Web UI is protected by a **simple login/password system**.

### 4. History Logging

* The system logs every **block** and **unblock** event, with timestamps.
* Logs are accessible via the web UI.

### 5. Persistence & Autostart

* All schedules and settings persist across reboots.
* The app **starts automatically** with the Raspberry Pi and resumes its scheduled tasks.

---

## Web UI Requirements

### Pages & Features

* **Login Page**
  Simple login with hardcoded or config-based credentials.

* **Dashboard**

  * Add/Edit/Delete websites
  * Set daily block time per website (start & end)
  * Enable/disable toggle for each website schedule

* **History Page**

  * View recent block/unblock logs with timestamps

---

## System Architecture

### Components

* **Frontend**: Web interface (Flask, FastAPI + Jinja/React/Vue)
* **Backend**:

  * Scheduling service (Python + `schedule` or `APScheduler`)
  * AdGuard API wrapper (HTTP calls to AdGuard)
  * SQLite or JSON file for storing configuration & logs
* **Startup Script**: Systemd service or crontab to run app on boot

### Data Flow

1. User submits website and schedule via UI.
2. Backend stores the schedule.
3. Scheduler checks current time vs. saved schedules.
4. Based on timing:

   * Calls AdGuard API to **add** domain to blocklist
   * Or **remove** it to unblock
5. Each action is logged.

---

## MVP Limitations

* No real-time status of what's currently blocked
* No predefined blocklists (only user-defined domains)
* No HTTPS packet inspection — relies purely on DNS-level blocking
* No multi-user support or role-based access
