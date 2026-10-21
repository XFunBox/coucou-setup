# syntax=docker/dockerfile:1
ARG NODE_IMAGE=node:22.23.3-bookworm-slim
ARG RUST_IMAGE=rust:1.99-bookworm
FROM ${NODE_IMAGE} AS node
FROM ${RUST_IMAGE} AS build
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
RUN apt-get update && apt-get install -y --no-install-recommends \
    libwebkit2gtk-4.1-dev libgtk-layer-shell-dev libayatana-appindicator3-dev \
    librsvg2-dev libssl-dev libdbus-1-dev libasound2-dev dbus patchelf \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app/windows
COPY windows/package.json windows/package-lock.json ./
RUN npm ci --include=optional
COPY windows ./
COPY NotchBuddy/Resources/sounds /app/NotchBuddy/Resources/sounds
COPY NotchBuddy/Resources/Localizable.xcstrings /app/NotchBuddy/Resources/Localizable.xcstrings
COPY NotchBuddy/Resources/Info.plist /app/NotchBuddy/Resources/Info.plist
COPY NotchBuddy/Resources/InfoAppStore.plist /app/NotchBuddy/Resources/InfoAppStore.plist
COPY NotchBuddy/Sources/App/SettingsView.swift /app/NotchBuddy/Sources/App/SettingsView.swift
COPY NotchBuddy/project.yml /app/NotchBuddy/project.yml
COPY LICENSE LICENSE-ASSETS.md /app/
COPY android/LICENSE /app/LICENSE-ANDROID
ENV CARGO_BUILD_JOBS=2
COPY android/relay/test-vectors.json /app/android/relay/test-vectors.json
RUN npm test
RUN cargo test --manifest-path tests/github-rust/Cargo.toml --target-dir /app/github-test-target
RUN cargo build --locked --release -p coucou-hook
RUN cargo test --locked --workspace --release
RUN dbus-run-session -- cargo test --locked --workspace --release spotify -- --ignored --test-threads=1
RUN npm run tauri -- build --config src-tauri/tauri.linux.conf.json --no-bundle
RUN mkdir -p /out && cp target/release/coucou target/release/coucou-hook /out/ \
 && cp /app/LICENSE /app/LICENSE-ASSETS.md /app/LICENSE-ANDROID /out/ \
 && cd /out && sha256sum coucou coucou-hook > SHA256SUMS
FROM scratch
COPY --from=build /out/ /

