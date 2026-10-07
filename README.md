# Insta-Print Server

A server that can connect and print from an Instax printer through a frontend web app.

Built using containers connected together with docker compose, intended to be run on a secure private network and served through a zero trust tunnel.

Built using the companion python library https://github.com/JoRobs/pyinstaxble, which is forked from https://github.com/javl/InstaxBLE and heavily modified to use `bleak` for async bluetooth communication.

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
  - [ ] Logging to disk
- [ ] Security
  - [x] Front/backend split
  - [ ] CORS enabled for backend service
  - [x] Backend endpoints only accessible by frontend
  - [x] Separate endpoint interface for front and backend
- [x] Color reproduction tweaks

