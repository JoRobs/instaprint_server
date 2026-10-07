# Insta-Print Server

An server that prints from an Instax printer through a frontend web app.

Built using `fasapi` and a companion python library [pyinstaxble](https://github.com/JoRobs/pyinstaxble), which is forked from https://github.com/javl/InstaxBLE and heavily modified to use the `bleak` python library for async bluetooth communication.

The project is comprised of several components,
- The companion library
- A backend server that communicates with the printer
- A frontend server that serves static HTML, CSS and JS files
- A docker compose file with additional services, including [cloudflared](https://github.com/cloudflare/cloudflared) for serving over the internet, and [dozzle](https://github.com/amir20/dozzle) for inspecting container logs

## Development

### Pre-reqs

Development on this project requires several tools to be installed
- `docker`
- `uv`

...and optionally
- `make`

It's also a good idea to make a copy of the `.env.sample` file and rename it to `.env` and fill in your environment preferences.

If you want to serve this over the internet a `cloudflared` container is included in the `docker-compose.yml` file. It can be configured using a config file the the `cloudflared/` directory, a sample file is included.

### Build

The project can be built using `make` from the root directory

- `make build` will build the frontend and backend container images using `docker`
- `make buildfront` and `make buildback` will buildthe front and backend respectively

### Run locally

The servers can be run directly without building with `make devfront` and `make devback`. In this mode the backend will use a "dummy printer" that mocks the real printer behaviour.

Alternatively, running `make local` will start the front and backend containers. They are configured to use internal networks without ports exposed, so they will be unconnectable by default without modifying the compose file.

Finally `make run` will start all containers, including a `dozzle` container with port `8080` exposed for easy container log access, and cloudflared.

# TODO

- [x] `pyinstaxble` rewrite with `bleak`
- [ ] UX
  - [x] Print submission modal
  - [ ] Current queue list
  - [ ] Printer status indicators
    - [x] Online
    - [ ] Printing
    - [ ] #photos in queue
    - [x] #film remaining
    - [x] Out of film
    - [ ] Battery?
- [ ] Stability
  - [x] Always-on printer
  - [ ] Queue service recovery
- [ ] Recovery
  - [ ] Queue backed by sqlite db
  - [x] Logging to disk
- [ ] Security
  - [x] Front/backend split
  - [ ] ~~CORS enabled for backend service~~ No longer required
  - [x] Backend endpoints only accessible by frontend
  - [x] Separate endpoint interface for front and backend
- [x] Color reproduction tweaks

