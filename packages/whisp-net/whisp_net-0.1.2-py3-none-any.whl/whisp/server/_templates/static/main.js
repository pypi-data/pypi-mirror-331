console.log("hello world");

document.addEventListener('DOMContentLoaded', function () {
    function addCell(row, content) {
        const nameCell = document.createElement('td');
        nameCell.textContent = content;
        row.appendChild(nameCell);
    }

    // Function to update the connections table using the fetched data.
    function updateConnectionsTable(connections) {
        const tbody = document.getElementById('connections-tbody');
        if (!tbody) return;
        // Clear existing rows
        tbody.innerHTML = '';

        // If no connections exist, show a fallback row
        if (Object.keys(connections).length === 0) {
            tbody.innerHTML = '<tr><td colspan="2">No connections available.</td></tr>';
            return;
        }

        // Create and append a new row for each connection
        Object.entries(connections).forEach(([sid, connection]) => {
            if (!connection.name) {
                return;
            }

            const row = document.createElement('tr');

            addCell(row, connection.name || "N/A");
            addCell(row, connection.sid);

            tbody.appendChild(row);
        });
    }

    // Function to update the connections table using the fetched data.
    function updateMessagesTable(messages) {
        const tbody = document.getElementById('messages-tbody');
        if (!tbody) return;
        // Clear existing rows
        tbody.innerHTML = '';

        // If no connections exist, show a fallback row
        if (Object.keys(messages).length === 0) {
            tbody.innerHTML = '<tr><td colspan="2">No connections available.</td></tr>';
            return;
        }

        // Create and append a new row for each connection
        Object.entries(messages).forEach(([sid, message]) => {
            const eventName = message["event"];
            const data = message["data"];

            const unixTimestamp = data["time_stamp"];
            const sender = data["sender"];

            // date
            const date = new Date(unixTimestamp);
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');
            const milliseconds = String(date.getMilliseconds()).padStart(3, '0');

            const formattedDate = `${hours}:${minutes}:${seconds}.${milliseconds}`;

            // data
            let dataOnly = Object.assign({}, data);
            delete dataOnly["time_stamp"];
            delete dataOnly["sender"];

            const row = document.createElement('tr');

            addCell(row, formattedDate);
            addCell(row, sender);
            addCell(row, eventName);
            addCell(row, JSON.stringify(dataOnly));

            tbody.appendChild(row);
        });
    }

    // Function to fetch connections from the API
    function fetchConnections() {
        fetch('/api/connections')
            .then(response => response.json())
            .then(data => {
                updateConnectionsTable(data);
            })
            .catch(error => console.error('Error fetching connections:', error));
    }

    // Initial fetch
    fetchConnections();

    // Update the connections table every 3 seconds
    // setInterval(fetchConnections, 3000);

    // connect to websocket
    const lastMessages = [];
    const client = new WhispClient()

    client.onMessage((message) => {

        // filter non-whisp messages
        if (!("event" in message))
            return;

        const eventName = message["event"];

        // filter whisp internal messages
        if (eventName === "whisp/joined") {
            fetchConnections();
            return;
        }

        if (eventName === "whisp/left") {
            fetchConnections();
            return;
        }

        // handle all other whisp messages
        lastMessages.unshift(message);

        if (lastMessages.length > 20) {
            lastMessages.pop();
        }

        updateMessagesTable(lastMessages);
    });
});