# SupaBRCK Local Dashboard

This dashboard implements a local view into the state of the SupaBRCK.

It is composed of two components:

- The API
- A web dashboard that consumes the API


## API

The API is developed using Flask and packaged for deployment on a SupaBRCK
using opkg.

The API documentation is built on Swagger and lives in `api-documentation`


# Releases

Package releases include both the dashboard and the api.

Deployment is exposed behing _Nginx_ at _http://local.brck.com_


# Notes

- API :ballot_box_with_check:
    - Authentication (default login + password change interface)
    - Device(s) status API (connection, storage)
    - Firmware type management API
    - Plex?
    - Configuration? FTP / File Management
    - Compute (features)
    - Per-device configuration
    - Per-device configuration or connection
- Frontend :ballot_box_with_check:
    - Web interface accessible @ local.brck.com
    - Content?
    - Compute?
    - React-based
    - Password change view
