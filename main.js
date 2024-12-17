console.log('Hello world!')

const ws = new WebSocket('ws://localhost:8082')

const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('textField');
const sendButton = document.getElementById('sendButton');
const gettingDataMsg = document.getElementById('getting-data');

function isJson(data) {
    if (typeof data === "string") {
        try {
            JSON.parse(data);
            return true;
        } catch (error) {
            return false;
        }
    }

    return typeof data === "object" && data !== null;
}

sendButton.addEventListener('click', () => {
    gettingDataMsg.style.display = 'block';
    const message = messageInput.value;
    if (message) {
        ws.send(message);
        messageInput.value = '';
    }
});

ws.onopen = () => {
    const welcomeMessage = document.createElement('div');
    welcomeMessage.textContent = "Connected to WebSocket server.";
    messagesDiv.appendChild(welcomeMessage);
};

ws.onclose = () => {
    const disconnectMessage = document.createElement('div');
    disconnectMessage.textContent = "Disconnected from WebSocket server.";
    messagesDiv.appendChild(disconnectMessage);
};

ws.onmessage = (e) => {
    gettingDataMsg.style.display = 'none';
    const newMessage = document.createElement('div');
    if(isJson(e.data)) {
        if(JSON.parse(e.data).error_msg) {
            const errorBlock = document.createElement('p');
            errorBlock.style.color = 'red';
            errorBlock.innerHTML = JSON.parse(e.data).error_msg;
            newMessage.appendChild = errorBlock;
        } else if(JSON.parse(e.data).resp_type == 'currencies') {
            const tableBlock = document.createElement('table');
            tableBlock.classList.add('table', 'table-bordered');

            const tableData = JSON.parse(e.data).currenciesData;

            const thead = document.createElement('thead');
            thead.innerHTML = `
                <tr>
                    <th>Date</th>
                    <th>Currency</th>
                    <th>Purchase</th>
                    <th>Sale</th>
                </tr>`;
            tableBlock.appendChild(thead);

            const tbody = document.createElement('tbody');

            for (const [date, currencies] of Object.entries(tableData)) {
                let firstRow = true;

                for (const [currency, rates] of Object.entries(currencies)) {
                    const tr = document.createElement('tr');

                    if (firstRow) {
                        const dateCell = document.createElement('td');
                        dateCell.rowSpan = Object.keys(currencies).length;
                        dateCell.textContent = date;
                        tr.appendChild(dateCell);
                        firstRow = false;
                    }

                    const currencyCell = document.createElement('td');
                    currencyCell.textContent = currency;
                    tr.appendChild(currencyCell);

                    const purchaseCell = document.createElement('td');
                    purchaseCell.textContent = rates.purchase;
                    tr.appendChild(purchaseCell);

                    const saleCell = document.createElement('td');
                    saleCell.textContent = rates.sale;
                    tr.appendChild(saleCell);

                    tbody.appendChild(tr);
                }
            }

            tableBlock.appendChild(tbody);
            newMessage.appendChild(tableBlock);
        } else if(JSON.parse(e.data).resp_type == 'error') {
            data = JSON.parse(e.data)
            messageBlock = document.createElement('p');
            messageBlock.style.color = 'red'
            messageBlock.textContent = data.message
            newMessage.appendChild(messageBlock);
        }
    } else {
        newMessage.textContent = e.data;
    }
    messagesDiv.appendChild(newMessage);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
