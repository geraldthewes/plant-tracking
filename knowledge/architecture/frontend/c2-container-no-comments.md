---
title: C2 Container Diagram for Plant Tracking System - Frontend Focus
---
flowchart LR
    gardener(["Gardener\n(Actor)"])
    telegram[["Telegram\n(External Service)"]]
    phomemo[["Phomemo M120\n(Bluetooth Printer)"]]

    subgraph sys["Plant Tracking System"]
        subgraph frontend["Mobile App Frontend\n(Next.js 14, React, TypeScript, Docker)"]
            ui["UI Layer\n(Next.js Pages, Tailwind CSS)"]
            api_client["API Client\n(React Hooks, SWR)"]
            camera["Camera Module\n(Expo/Web Camera API)"]
            qr_scanner["QR Scanner\n(ZXing/Lens Barcode)"]
            storage["Local Storage\n(IndexedDB, localStorage)"]
            hermes_client["Hermes Client\n(Telegram Bot API)"]
        end

        backend["Backend API\n(Node.js/Express, Docker)"]
        db[("Plant Database\n(Markdown Files, JSON)")]
        qr_service["QR Code Service\n(Node.js, Docker)"]
        printer_service["Printer Service\n(Python, Bluetooth, Docker)"]
    end

    gardener -->|"Views/enters data via touch UI"| ui
    gardener -->|"Captures photos via camera"| camera
    gardener -->|"Scans QR codes via camera"| qr_scanner
    gardener -->|"Interacts via Telegram"| telegram

    ui -->|"Triggers API calls via SWR hooks"| api_client
    ui -->|"Requests camera access via Expo"| camera
    ui -->|"Initiates QR scan via Lens"| qr_scanner
    ui -->|"Reads/writes cached data via"| storage
    ui -->|"Sends messages via Telegram API"| hermes_client

    api_client -->|"REST API calls via HTTPS/JSON"| backend
    camera -->|"Captures images via Web Camera API"| storage
    qr_scanner -->|"Decodes QR data via ZXing"| storage
    hermes_client -->|"Sends/receives messages via Bot API"| telegram

    backend -->|"Reads/writes plant data via file I/O"| db
    backend -->|"Requests QR codes via HTTP/JSON"| qr_service
    backend -->|"Sends print jobs via Bluetooth/RFCOMM"| printer_service

    printer_service -->|"Prints labels via Bluetooth LE"| phomemo
    qr_service -->|"Generates QR images via HTTP response"| backend
