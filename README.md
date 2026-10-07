# Insta-Print Server

A server that can connect and print from an Instax printer through a frontend web app.

Built using containers connected together with docker compose, intended to be run on a secure private network and served through a zero trust tunnel.

Built using the companion python library https://github.com/JoRobs/pyinstaxble, which is forked from https://github.com/javl/InstaxBLE and heavily modified to use `bleak` for async bluetooth communication.

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

