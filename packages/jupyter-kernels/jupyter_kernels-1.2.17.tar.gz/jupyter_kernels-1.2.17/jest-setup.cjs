/*
 * Copyright (c) 2023-2024 Datalayer, Inc.
 *
 * Datalayer License
 */

/**
 * Additional shim for Jest
 */

/* global globalThis */

globalThis.CSS = Object.freeze({
    supports: () => false
});

globalThis.BroadcastChannel = class BroadcastChannel {}

__webpack_public_path__ = '';
