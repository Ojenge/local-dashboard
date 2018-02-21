# SupaBRCK Local Dashboard

This dashboard implements a local view into the state of the SupaBRCK.

It is composed of two components:

- The API
- A web dashboard that consumes the API


## API

The API is developed using Flask and packaged for deployment on a SupaBRCK
using opkg.

The API documentation is built on Swagger and lives in `api-docs`

## Architecture

![Architecture](media/stack.png)

## Installation notes

Installation may be performed using `opkg`

`opkg install local-dashboard`

- This will set up the API, database and dashboard, the latter will be exposed at http://local.brck.com when accessed from within the SupaBRCK WiFi network.
- First-time use will require to change the password from the default credentials (admin/admin)


## Feature notes

- API 
    - [x] Authentication (default login + password change interface)
    - [x] Device(s) status API (connection, storage)
    - [x] Firmware type management API
    - [x] SIM connection management
    - [ ] Plex?
    - [ ] Configuration? FTP / File Management
    - [ ] Compute (features)
- Frontend
    - [x] System State
    - [x] SIM Connection Management
    - [x] Power Management
    - [x] LAN Connection Management
    - [x] System version and packages view
    - [ ] Historical views
