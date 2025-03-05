class WhispClient {
    /**
     * @param {Object} options
     * @param {string} options.name - Client name (for logging or identification)
     * @param {string} [options.address="http://127.0.0.1:14000"] - Server address.
     * @param {boolean} [options.autoConnect=true] - Whether to automatically connect.
     */
    constructor({name = "_WhispWeb", address = "http://127.0.0.1:14000", autoConnect = true} = {}) {
        this.name = name;
        this.address = address;
        this.onMessageCallback = null;

        // Initialize the socket with autoConnect option.
        this.socket = io(this.address, {autoConnect});

        // Setup event handlers to catch all messages.
        this._setupSocket();

        // Auto-connect if enabled.
        if (autoConnect) {
            this.socket.connect();
        }
    }

    /**
     * Setup the socket to intercept all incoming events.
     * This overrides the default onevent handler to call our callback.
     */
    _setupSocket() {
        // Keep a reference to the original onevent function.
        const originalOnevent = this.socket.onevent.bind(this.socket);

        // Override onevent to capture all incoming events.
        this.socket.onevent = (packet) => {
            // packet.data is an array: first element is the event name and the rest are arguments.
            const [event, ...args] = packet.data || [];

            // Call the original handler to preserve normal behavior.
            originalOnevent(packet);

            // If a callback is registered, call it with a simple message object.
            if (this.onMessageCallback && typeof this.onMessageCallback === 'function') {
                // Pass the event name and data (if there's one argument, unwrap it).
                const data = (args.length === 1) ? args[0] : args;
                this.onMessageCallback({event, data});
            }
        };

        // Optional: Log connect/disconnect events.
        this.socket.on("connect", () => {
            console.log(`[${this.name}] Connected to ${this.address}`);
        });

        this.socket.on("disconnect", () => {
            console.log(`[${this.name}] Disconnected from ${this.address}`);
        });
    }

    /**
     * Register a callback that is invoked on every websocket message.
     * @param {Function} callback - Function that takes an object with { event, data }.
     */
    onMessage(callback) {
        if (typeof callback === 'function') {
            this.onMessageCallback = callback;
        } else {
            console.error("onMessage callback must be a function");
        }
    }

    /**
     * Disconnect the client from the server.
     */
    disconnect() {
        this.socket.disconnect();
    }
}